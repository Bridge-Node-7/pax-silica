import subprocess
import sys
import tempfile
import unittest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SynergyTests(unittest.TestCase):
    def build(self, out):
        subprocess.check_call([sys.executable, str(ROOT / "scripts/build_web.py"), "--output", out], cwd=ROOT)

    def test_corporate_identity_contract(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            self.assertIn('content="#06101f"', text)
            self.assertIn('og:site_name" content="Bridge Node 7"', text)
            self.assertIn('https://bridgenode7.com/pax-silica/', text)
            self.assertIn('aria-label="Primary navigation"', text)
            self.assertIn('>Materials-to-Mission</a>', text)
            self.assertIn('>Partner</a>', text)
            self.assertIn('>Strategic Inquiry</a>', text)
            self.assertIn('mailto:contact@bridgenode7.com?subject=Bridge%20Node%207%20%7C%20Strategic%20Inquiry', text)
            self.assertIn('>Golden Age</a> · <a href="https://bridgenode7.com/materials-to-mission/">Materials-to-Mission</a> · <a href="https://bridgenode7.com/partner/">Partner</a>', text)
            self.assertNotRegex(text, re.compile(r'>\s*Current\b', re.I))

    def test_csp_and_social_contract(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", text)
            self.assertIn("style-src 'self'", text)
            self.assertIn("script-src 'self'", text)
            self.assertNotIn("script-src 'unsafe-inline'", text)
            self.assertIn('property="og:title" content="Pax Silica Intelligence · Bridge Node 7"', text)
            self.assertIn('name="twitter:card" content="summary_large_image"', text)

    def test_design_tokens(self):
        css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
        for token in ['--bg:#050914','--gold:#f1c86b','--gold2:#fff0b3','--blue:#78d7ff','--violet:#c6a7ff','--max:1160px']:
            self.assertIn(token, css)
        self.assertNotIn('.global a:first-child{display:none}', css)
        self.assertNotIn('.global a:nth-child(2){display:none}', css)

if __name__ == '__main__':
    unittest.main()
