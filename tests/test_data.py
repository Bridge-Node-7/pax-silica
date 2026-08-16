import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/"data/pax-silica.json").read_text(encoding="utf-8"))
        cls.sources=json.loads((ROOT/"data/sources.json").read_text(encoding="utf-8"))["sources"]
    def test_active_count(self):
        self.assertEqual(sum(x["status"]=="active" for x in self.data["signatories"]),25)
    def test_founder_count(self):
        self.assertEqual(sum(bool(x.get("founding")) for x in self.data["signatories"] if x["status"]=="active"),7)
    def test_source_ids_unique(self):
        ids=[x["id"] for x in self.sources]; self.assertEqual(len(ids),len(set(ids)))
    def test_claim_ids_unique(self):
        ids=[x["id"] for x in self.data["claims"]]; self.assertEqual(len(ids),len(set(ids)))
    def test_event_ids_unique(self):
        ids=[x["id"] for x in self.data["events"]]; self.assertEqual(len(ids),len(set(ids)))
    def test_philippines_location_source_boundary(self):
        by_id={x["id"]:x for x in self.sources}
        self.assertNotIn(
            "New Clark City AI-native industrial acceleration hub",
            by_id["S-07"]["supports"],
        )
        self.assertIn(
            "New Clark City location",
            by_id["S-10"]["supports"],
        )
if __name__=="__main__": unittest.main()
