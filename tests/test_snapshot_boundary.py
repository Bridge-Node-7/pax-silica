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
                if source["id"] == "S-09":
                    source["verified_at"] = "2026-08-21"
            self.write_json(sources_path, source_doc)

            result = self.run_validator(root)
            output = result.stdout + result.stderr

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("record verification postdates snapshot", output)
            self.assertIn("C-006", output)

    def test_current_snapshot_boundary_accepts_included_verifications(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            result = self.run_validator(root)
            output = result.stdout + result.stderr

            self.assertEqual(result.returncode, 0, output)
            self.assertIn("PASS - data integrity", output)


if __name__ == "__main__":
    unittest.main()
