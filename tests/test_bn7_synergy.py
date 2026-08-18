import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SynergyTests(unittest.TestCase):
    def build(self, out):
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts/build_web.py"), "--output", out],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )

    def test_corporate_identity_contract(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            self.assertIn('content="#050914"', text)
            self.assertRegex(text, r'<meta\b(?=[^>]*property="og:site_name")(?=[^>]*content="Bridge Node 7")[^>]*>')
            self.assertIn('https://bridgenode7.com/pax-silica/', text)
            self.assertIn('aria-label="Primary navigation"', text)
            self.assertIn(">Materials-to-Mission</a>", text)
            self.assertIn(">Partner</a>", text)
            self.assertIn("Frontier Decision Engine", text)
            self.assertIn("Advancing a Golden Age", text)
            self.assertIn('aria-label="Bridge Node 7 home"', text)

    def test_csp_and_social_contract(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            text = (Path(d) / "index.html").read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", text)
            self.assertIn("style-src 'self'", text)
            self.assertIn("script-src 'self'", text)
            self.assertNotIn("script-src 'unsafe-inline'", text)
            self.assertRegex(text, r'<meta\b(?=[^>]*property="og:title")(?=[^>]*content="Pax Silica Intelligence · Bridge Node 7")[^>]*>')
            self.assertRegex(text, r'<meta\b(?=[^>]*name="twitter:card")(?=[^>]*content="summary_large_image")[^>]*>')

    def test_design_tokens(self):
        css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
        for token in ("--bg:#050914", "--gold:#f1c86b", "--gold2:#fff0b3", "--aqua:#78d7ff", "--violet:#c6a7ff"):
            self.assertIn(token, css)
        self.assertIn("--max:1180px", css)

if __name__ == "__main__":
    unittest.main()
