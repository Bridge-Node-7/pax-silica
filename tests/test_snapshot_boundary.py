import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_data.py"


class SnapshotBoundaryTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        shutil.copytree(ROOT / "data", root / "data")
        return root

    def run_validator(self, root):
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--root",
                str(root),
                "--as-of",
                "2026-08-22",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def write_json(self, path, value):
        path.write_text(
            json.dumps(value, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_source_verification_cannot_postdate_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            data_path = root / "data/pax-silica.json"
            data = json.loads(data_path.read_text(encoding="utf-8"))
            data["snapshot"]["verified_through"] = "2026-08-21"
            self.write_json(data_path, data)

            result = self.run_validator(root)
            output = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source verification postdates snapshot", output)
            self.assertIn("S-09", output)

    def test_record_verification_cannot_postdate_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            data_path = root / "data/pax-silica.json"
            sources_path = root / "data/sources.json"

            data = json.loads(data_path.read_text(encoding="utf-8"))
            data["snapshot"]["verified_through"] = "2026-08-21"
            self.write_json(data_path, data)

            source_doc = json.loads(sources_path.read_text(encoding="utf-8"))
            for source in source_doc["sources"]:
                if source["verified_at"] > "2026-08-21":
                    source["verified_at"] = "2026-08-21"
                if source.get("published", "") > "2026-08-21":
                    source["published"] = "2026-08-21"
            self.write_json(sources_path, source_doc)

            result = self.run_validator(root)
            output = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("record verification postdates snapshot", output)
            self.assertIn("C-006", output)

    def test_current_snapshot_boundary_accepts_included_verifications(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            data = json.loads((root / "data/pax-silica.json").read_text(encoding="utf-8"))
            program = next(record for record in data["programs"] if record["id"] == "P-001")
            self.assertEqual(data["snapshot"]["verified_through"], "2026-09-29")
            self.assertEqual(program["eligibility_verified_at"], "2026-09-30")
            self.assertEqual(program["eligibility_source_ids"], ["S-06"])
            result = self.run_validator(root)
            output = result.stdout + result.stderr

            self.assertEqual(result.returncode, 0, output)
            self.assertIn("PASS - data integrity", output)

    def test_present_eligibility_sources_are_typed_resolved_ids(self) -> None:
        values: tuple[object, ...] = (
            None, "", " ", "S-06", False, 42, {},
            [None], [False], [42], [[]], [{}], [""], [" "],
            ["S-MISSING"], [" S-06 "],
        )
        for value in values:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                data_path = root / "data/pax-silica.json"
                data = json.loads(data_path.read_text(encoding="utf-8"))
                data["programs"][0]["eligibility_source_ids"] = value
                self.write_json(data_path, data)
                result = self.run_validator(root)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("P-001.eligibility_source_ids", result.stdout + result.stderr)

    def test_present_eligibility_dates_are_canonical(self) -> None:
        values: tuple[object, ...] = (
            None, "", " ", False, 42, [], {}, "not-a-date",
            "2026-02-30", "20260929", "2026-W39-2", " 2026-09-30 ",
        )
        for value in values:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                data_path = root / "data/pax-silica.json"
                data = json.loads(data_path.read_text(encoding="utf-8"))
                data["programs"][0]["eligibility_verified_at"] = value
                self.write_json(data_path, data)
                result = self.run_validator(root)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("P-001.eligibility_verified_at", result.stdout + result.stderr)

    def test_optional_eligibility_fields_preserve_independent_omission(self) -> None:
        for omitted in ((), ("eligibility_source_ids",), ("eligibility_verified_at",),
                        ("eligibility_source_ids", "eligibility_verified_at")):
            with self.subTest(omitted=omitted), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                data_path = root / "data/pax-silica.json"
                data = json.loads(data_path.read_text(encoding="utf-8"))
                for field in omitted:
                    del data["programs"][0][field]
                self.write_json(data_path, data)
                result = self.run_validator(root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            data_path = root / "data/pax-silica.json"
            data = json.loads(data_path.read_text(encoding="utf-8"))
            data["programs"][0]["eligibility_source_ids"] = []
            self.write_json(data_path, data)
            result = self.run_validator(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
