"""Regression checks for scoped post-snapshot public evidence updates."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NovemberEvidenceUpdateTests(unittest.TestCase):
    def test_baseline_is_preserved_and_sources_have_limits(self):
        baseline = json.loads((ROOT / "data/pax-silica.json").read_text(encoding="utf-8"))
        delta = json.loads((ROOT / "data/evidence-update-2026-11-17.json").read_text(encoding="utf-8"))
        self.assertEqual(baseline["snapshot"]["verified_through"], "2026-09-29")
        self.assertEqual(delta["baseline_snapshot"], baseline["snapshot"]["verified_through"])
        self.assertGreater(delta["reviewed_at"], delta["baseline_snapshot"])
        self.assertGreaterEqual(len(delta["observations"]), 2)
        for item in delta["observations"]:
            with self.subTest(item=item["id"]):
                self.assertTrue(item["finding"].strip())
                self.assertTrue(item["limit"].strip())
                self.assertTrue(item["source"]["url"].startswith("https://"))
                self.assertLessEqual(item["source"]["published"], delta["reviewed_at"])

    def test_deterministic_public_html_renders_addendum(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.check_call(
                [sys.executable, str(ROOT / "scripts/build_web.py"), "--output", directory],
                cwd=ROOT,
            )
            page = (Path(directory) / "index.html").read_text(encoding="utf-8")
            self.assertIn("Philippines: New evidence and unresolved questions", page)
            self.assertIn("Baseline retained: 29 Sep 2026", page)
            self.assertIn("Reviewed 17 Nov 2026", page)
            self.assertIn("Human Rights Watch", page)
            self.assertIn("GMA News", page)
            self.assertIn("Evidence limit:", page)
            self.assertIn("Still requiring independent verification", page)
            self.assertNotIn("{{NOVEMBER_UPDATE}}", page)
            self.assertEqual(page.count('class="november-update"'), 1)
            # Linked, explicitly attributed reporting; no iframe or external script.
            self.assertIn('rel="noopener noreferrer" target="_blank"', page)


if __name__ == "__main__":
    unittest.main()
