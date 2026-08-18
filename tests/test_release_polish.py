import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ReleasePolishTests(unittest.TestCase):
    def build(self, out):
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts/build_web.py"), "--output", out],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )

    def test_evidence_hierarchy_and_dates(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            self.assertIn("Official Sources", text)
            self.assertIn("Secondary Sources", text)
            self.assertIn("Reported Development", text)
            self.assertNotIn("REPORTED / DRAFT", text)
            self.assertIn("Published ", text)
            self.assertIn("Reviewed ", text)
            self.assertIn("Review by ", text)
            self.assertEqual(text.count('class="source-record"'), 10)

    def test_final_taxonomy(self):
        tpl = (ROOT / "web/index.template.html").read_text(encoding="utf-8")
        order = [tpl.index(f'href="#{sid}"') for sid in (
            "network","technology","capability","philippines","four-p","readiness","switching","evidence"
        )]
        self.assertEqual(order, sorted(order))
        for phrase in (
            "The Pax Silica Network",
            "Technology Dependencies",
            "Industrial Capability",
            "Philippines in Pax Silica",
            "People. Planet. Profits. Product.",
            "Capability Readiness",
            "Supply Resilience",
            "Sources &amp; Evidence",
            "Bridge Node 7 Analysis",
            "From Intelligence to Decision",
            "Advancing a Golden Age",
        ):
            self.assertIn(phrase, tpl)

    def test_public_language_contract(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            visible = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>", " ", text, flags=re.I)
            self.assertIsNone(re.search(r"\b(?:you|your|yours|yourself|yourselves)\b", visible, re.I))
            self.assertNotIn("—", visible)

    def test_no_public_202_day_model(self):
        tpl = (ROOT / "web/index.template.html").read_text(encoding="utf-8")
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        for phrase in ("202 days", "Baseline Time-to-Switch", "Compare prequalified scenario", "ttsTotal"):
            self.assertNotIn(phrase, tpl + app)

    def test_header_and_closing_contract(self):
        tpl = (ROOT / "web/index.template.html").read_text(encoding="utf-8")
        self.assertIn('>Materials-to-Mission</a>', tpl)
        self.assertIn('>Partner</a>', tpl)
        self.assertNotIn(">Strategic Inquiry</a>", tpl)
        self.assertIn("Frontier Decision Engine", tpl)
        self.assertIn("bn7-links-equal", tpl)
        self.assertIn("footer-home", tpl)

    def test_github_actions_are_sha_pinned(self):
        for path in (ROOT / ".github/workflows").glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            for ref in re.findall(r"uses:\s*([^\s#]+)", text):
                self.assertRegex(ref, r"@[0-9a-f]{40}$", msg=f"unpinned action in {path}: {ref}")

    def test_mobile_touch_target_contract(self):
        css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
        self.assertIn("min-height:44px", css)
        self.assertIn("scrollbar-gutter:stable", css)
        self.assertIn("@media (forced-colors:active)", css)

    def test_browser_uat_is_required(self):
        text = (ROOT / ".github/workflows/browser-uat.yml").read_text(encoding="utf-8")
        self.assertIn("name: Browser UAT required", text)
        self.assertIn("needs: chromium", text)
        self.assertNotIn("  pull_request:\n    paths:", text)

    def test_public_boundary_policy_and_evidence_gate(self):
        boundary = (ROOT / "scripts/check_public_boundary.py").read_text(encoding="utf-8")
        gate = (ROOT / "scripts/check_repo.py").read_text(encoding="utf-8")
        self.assertIn("PUBLIC_SURFACE", boundary)
        self.assertIn("NONPUBLIC_DISCLOSURE_PATTERNS", boundary)
        self.assertIn("check_evidence_integrity.py", gate)

if __name__ == "__main__":
    unittest.main()
