from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import intelligence_watch as watch


class IntelligenceWatchHealthTests(unittest.TestCase):
    def test_status_taxonomy(self):
        self.assertEqual(watch.classify_http_status(200), "ok")
        self.assertEqual(watch.classify_http_status(302), "ok")
        self.assertEqual(watch.classify_http_status(403), "manual_verification")
        self.assertEqual(watch.classify_http_status(429), "manual_verification")
        self.assertEqual(watch.classify_http_status(404), "unavailable")
        self.assertEqual(watch.classify_http_status(410), "unavailable")
        self.assertEqual(watch.classify_http_status(503), "temporary_error")

    def test_only_unavailable_health_requires_review(self):
        self.assertTrue(watch.health_requires_review({"state": "unavailable"}))
        for state in ("ok", "manual_verification", "temporary_error"):
            self.assertFalse(watch.health_requires_review({"state": state}))


if __name__ == "__main__":
    unittest.main()
