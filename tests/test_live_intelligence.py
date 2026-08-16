from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import live_intelligence as live


class LiveIntelligenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = live.load_json(ROOT / "automation/live-intelligence-policy.json")
        cls.schema = live.load_json(ROOT / "automation/candidate.schema.json")
        cls.data, cls.sources = live.canonical_context(ROOT)

    def decision(self, fixture_name: str, mode: str = "bounded"):
        candidate = live.fixture(fixture_name, self.policy)
        live.validate_candidate_shape(candidate, self.schema)
        return live.evaluate_candidate(candidate, mode, self.data, self.sources, self.policy)

    def test_no_change(self):
        self.assertEqual(self.decision("no-change")["disposition"], "no_change")

    def test_safe_official_status_transition(self):
        d = self.decision("safe-status")
        self.assertEqual(d["disposition"], "auto_publish")
        self.assertEqual(d["rule_id"], "P001_OPEN_TO_CLOSED")

    def test_reported_development_requires_human(self):
        self.assertEqual(self.decision("reported")["disposition"], "human_review")

    def test_contradiction_requires_human(self):
        self.assertEqual(self.decision("contradiction")["disposition"], "human_review")

    def test_unknown_domain_requires_human(self):
        self.assertEqual(self.decision("unknown-domain")["disposition"], "human_review")

    def test_old_value_mismatch_requires_human(self):
        self.assertEqual(self.decision("stale-old")["disposition"], "human_review")

    def test_broad_mode_never_auto_publishes(self):
        self.assertEqual(self.decision("safe-status", mode="broad")["disposition"], "human_review")

    def test_safe_application_changes_only_expected_semantics(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "data").mkdir()
            (root / "data/pax-silica.json").write_text((ROOT / "data/pax-silica.json").read_text(encoding="utf-8"), encoding="utf-8")
            (root / "data/sources.json").write_text((ROOT / "data/sources.json").read_text(encoding="utf-8"), encoding="utf-8")
            candidate = live.fixture("safe-status", self.policy)
            decision = live.evaluate_candidate(candidate, "bounded", self.data, self.sources, self.policy)
            changed = live.apply_auto_publish(root, candidate, decision, "2026-08-20")
            self.assertEqual(changed, ["data/pax-silica.json", "data/sources.json"])
            data = live.load_json(root / "data/pax-silica.json")
            sources = live.load_json(root / "data/sources.json")["sources"]
            program = live.find_record(data, "programs", "P-001")
            claim = live.find_record(data, "claims", "C-004")
            source = next(x for x in sources if x["id"] == "S-06")
            self.assertEqual(program["status"], "closed")
            self.assertNotIn("review_by", program)
            self.assertNotIn("review_by", claim)
            self.assertNotIn("review_by", source)
            self.assertEqual(data["snapshot"]["verified_through"], "2026-08-20")


if __name__ == "__main__":
    unittest.main()
