import json
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

class ScriptBodyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._in_script = False
        self._body = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            self._in_script = True
            self._body = []

    def handle_data(self, data):
        if self._in_script:
            self._body.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._in_script:
            self.scripts.append("".join(self._body))
            self._in_script = False
            self._body = []

class PublicReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "data/pax-silica.json").read_text(encoding="utf-8"))
        cls.sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))["sources"]
        cls.source_map = {s["id"]: s for s in cls.sources}

    def build(self, out):
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts/build_web.py"), "--output", out],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )

    def test_source_domains_are_deliberately_bounded(self):
        allowed = {
            "state.gov", "www.state.gov",
            "whitehouse.gov", "www.whitehouse.gov",
            "simpler.grants.gov",
            "reuters.com", "www.reuters.com",
            "comune.brindisi.it", "www.comune.brindisi.it",
        }
        observed = {(urlsplit(s["url"]).hostname or "").lower() for s in self.sources}
        self.assertTrue(observed <= allowed, observed - allowed)

    def test_claim_evidence_state_alignment(self):
        for claim in self.data["claims"]:
            source_states = {self.source_map[s]["state"] for s in claim.get("source_ids", [])}
            if claim["state"] == "official":
                self.assertIn("official", source_states, claim["id"])
            if claim["state"] == "reported_draft":
                self.assertIn("reported_draft", source_states, claim["id"])

    def test_italy_has_primary_accession_evidence(self):
        italy = next(s for s in self.data["signatories"] if s["name"] == "Italy")
        self.assertEqual(italy["evidence_state"], "official")
        self.assertIn("S-11", italy["source_ids"])
        self.assertEqual(self.source_map["S-11"]["state"], "official")

    def test_hero_is_honest_and_not_fake_live(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            hero = text.split('<nav aria-label="Pax Silica sections"', 1)[0]
            self.assertIn("Pax Silica", hero)
            self.assertIn("Pax Silica is a U.S.-led strategic initiative focused on trusted technology and AI supply chains.", hero)
            self.assertIn("Bridge Node 7 transforms public evidence into intelligence for industrial capability.", hero)
            self.assertIn("Reviewed snapshot 15 Aug 2026", hero)
            self.assertNotIn("Latest official signal", hero)
            self.assertNotIn("Live intelligence", hero)
            self.assertNotIn("Verified through", hero)

    def test_no_inline_source_database_or_executable_script(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            parser = ScriptBodyParser()
            parser.feed(text)
            for body in parser.scripts:
                self.assertFalse(body.strip())
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        self.assertNotIn("const evidence={", app)
        self.assertIn(".source-record[data-source-id=", app)

    def test_public_page_avoids_self_promotional_leadership_claims(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8").lower()
            for phrase in (
                "industry leader",
                "leading pax silica",
                "official pax silica partner",
                "pax silica partner of record",
            ):
                self.assertNotIn(phrase, text)

    def test_repository_has_no_contributor_ceremony_files(self):
        for rel in (
            "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", ".github/CODEOWNERS",
            "CITATION.cff", "RIGHTS.md", "docs/GENESIS_VALIDATION.md",
        ):
            self.assertFalse((ROOT / rel).exists(), rel)

    def test_only_approved_public_email_is_present(self):
        allowed = {"contact@bridgenode7.com"}
        emails = set()
        for p in ROOT.rglob("*"):
            if not p.is_file() or "build" in p.parts or "__pycache__" in p.parts:
                continue
            if p.suffix.lower() not in {".md",".json",".py",".html",".css",".js",".yml",".yaml",".txt",".cff"}:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            emails |= set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I))
        self.assertEqual(emails, allowed)

    def test_public_operating_surface_is_minimized(self):
        rels = (
            "README.md",
            "CHANGELOG.md",
            "NOTICE",
            "SECURITY.md",
            "docs/CREDIBILITY.md",
            "docs/INTELLIGENCE_MODEL.md",
            "docs/MAINTENANCE.md",
            "docs/PUBLIC_BOUNDARY.md",
            "docs/RELEASE_ENGINEERING.md",
            "docs/SOURCE_STATES.md",
            "docs/VISUAL_CONTRACT.md",
            "analysis/philippines-capability-accumulation.md",
            "analysis/provenance-vs-qualification.md",
            "analysis/time-to-switch.md",
            "web/index.template.html",
        )

        allowed_hosts = {
            "bridgenode7.com",
            "www.bridgenode7.com",
            "github.com",
            "www.github.com",
        }

        personal_profile_markers = (
            "personal biography",
            "personal profile",
            "curriculum vitae",
            "alma mater",
            "linkedin.com",
            " university ",
            " college ",
        )

        for rel in rels:
            text = (
                ROOT / rel
            ).read_text(
                encoding="utf-8",
            )

            for url in re.findall(
                r"https://[^\s<>)\]\"';]+",
                text,
            ):
                host = (
                    urlsplit(url).hostname
                    or ""
                ).lower()

                self.assertIn(
                    host,
                    allowed_hosts,
                    f"{rel}: {url}",
                )

            normalized = (
                " "
                + " ".join(
                    text.lower().split()
                )
                + " "
            )

            for marker in (
                personal_profile_markers
            ):
                self.assertNotIn(
                    marker,
                    normalized,
                    rel,
                )

    def test_license_contains_complete_mit_text(self):
        normalized = " ".join((ROOT / "LICENSE").read_text(encoding="utf-8").split())
        self.assertIn("and to permit persons to whom the Software is furnished to do so", normalized)
        self.assertIn("IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM", normalized)

    def test_v025_public_ux_contract(self):
        tpl = (ROOT / "web/index.template.html").read_text(encoding="utf-8")
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        self.assertIn('id="evidenceDrawer" inert="" role="dialog"', tpl)
        self.assertIn("drawer.removeAttribute('inert')", app)
        self.assertIn("drawer.setAttribute('inert','')", app)
        for sid in ("network","technology","capability","philippines","four-p","readiness","switching","evidence"):
            self.assertIn(f'id="{sid}"', tpl)
        self.assertNotIn("202 days", tpl)
        self.assertNotIn("Time-to-Switch", tpl)

if __name__ == "__main__":
    unittest.main()
