import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

class PublicReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'data/pax-silica.json').read_text(encoding='utf-8'))
        cls.sources = json.loads((ROOT / 'data/sources.json').read_text(encoding='utf-8'))['sources']
        cls.source_map = {s['id']: s for s in cls.sources}

    def build(self, out):
        subprocess.check_call([sys.executable, str(ROOT / 'scripts/build_web.py'), '--output', out], cwd=ROOT)

    def test_source_domains_are_deliberately_bounded(self):
        allowed = {
            'state.gov', 'www.state.gov',
            'whitehouse.gov', 'www.whitehouse.gov',
            'simpler.grants.gov',
            'reuters.com', 'www.reuters.com',
            'comune.brindisi.it', 'www.comune.brindisi.it',
        }
        observed = {(urlsplit(s['url']).hostname or '').lower() for s in self.sources}
        self.assertTrue(observed <= allowed, observed - allowed)

    def test_official_claims_have_official_sources(self):
        for claim in self.data['claims']:
            if claim['state'] != 'official':
                continue
            states = {self.source_map[s]['state'] for s in claim['source_ids']}
            self.assertIn('official', states, claim['id'])

    def test_reported_claims_stay_reported(self):
        for claim in self.data['claims']:
            if claim['state'] != 'reported_draft':
                continue
            states = {self.source_map[s]['state'] for s in claim['source_ids']}
            self.assertIn('reported_draft', states, claim['id'])

    def test_italy_has_primary_accession_evidence(self):
        italy = next(s for s in self.data['signatories'] if s['name'] == 'Italy')
        self.assertEqual(italy['evidence_state'], 'official')
        self.assertIn('S-11', italy['source_ids'])
        self.assertEqual(self.source_map['S-11']['state'], 'official')

    def test_hero_uses_official_signal_not_reported_draft(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / 'index.html').read_text(encoding='utf-8')
            self.assertIn('Latest official signal', text)
            # The newest official seed development is the Aug 12 AI Assistance Project.
            self.assertIn('State announces the Pax Silica AI Assistance implementation program and Silicon Highway concept.', text)
            hero = text.split('<nav class="local"', 1)[0]
            self.assertNotIn('Reuters reports a draft U.S. approach', hero)

    def test_no_inline_source_database_or_inline_executable_script(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / 'index.html').read_text(encoding='utf-8')
            self.assertNotIn('id="sourceData"', text)
            scripts = re.findall(r'<script([^>]*)>(.*?)</script>', text, re.I | re.S)
            for attrs, body in scripts:
                self.assertFalse(body.strip(), f'inline script body present: {attrs}')

    def test_public_page_avoids_self_promotional_leadership_claims(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / 'index.html').read_text(encoding='utf-8').lower()
            for phrase in ('industry leader', 'leading pax silica', 'official pax silica partner', 'pax silica partner of record'):
                self.assertNotIn(phrase, text)

    def test_repository_has_no_contributor_ceremony_files(self):
        for rel in ('CODE_OF_CONDUCT.md', 'CONTRIBUTING.md', '.github/CODEOWNERS', 'CITATION.cff', 'RIGHTS.md', 'docs/GENESIS_VALIDATION.md'):
            self.assertFalse((ROOT / rel).exists(), rel)

    def test_only_approved_public_email_is_present(self):
        allowed = {'contact@bridgenode7.com'}
        emails = set()
        for p in ROOT.rglob('*'):
            if not p.is_file() or 'build' in p.parts or '__pycache__' in p.parts:
                continue
            if p.suffix.lower() not in {'.md','.json','.py','.html','.css','.js','.yml','.yaml','.txt','.cff'}:
                continue
            text = p.read_text(encoding='utf-8', errors='ignore')
            emails |= set(re.findall(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', text, re.I))
        self.assertEqual(emails, allowed)

    def test_license_contains_complete_mit_grant_and_liability_text(self):
        text = (ROOT / 'LICENSE').read_text(encoding='utf-8')
        normalized = ' '.join(text.split())
        self.assertIn(
            'and to permit persons to whom the Software is furnished to do so',
            normalized,
        )
        self.assertIn(
            'IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM',
            normalized,
        )

if __name__ == '__main__':
    unittest.main()
