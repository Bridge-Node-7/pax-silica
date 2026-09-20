import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseBuilderTests(unittest.TestCase):
    def test_next_release_evidence_is_complete_and_deterministic(self):
        commit = "0" * 40
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for output in (first, second):
                subprocess.run(
                    [
                        "python", str(ROOT / "scripts/build_release.py"), "--root", str(ROOT),
                        "--output-dir", output, "--commit", commit,
                    ], check=True, capture_output=True, text=True,
                )
            one, two = Path(first), Path(second)
            names = {path.name for path in one.iterdir()}
            version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
            archive_name = f"pax-silica-v{version}.zip"
            self.assertEqual(names, {archive_name, "RELEASE_NOTES.md", "SHA256SUMS", "VALIDATION_EVIDENCE.json"})
            self.assertEqual((one / archive_name).read_bytes(), (two / archive_name).read_bytes())
            evidence = json.loads((one / "VALIDATION_EVIDENCE.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["source_commit"], commit)
            with zipfile.ZipFile(one / archive_name) as archive:
                self.assertIn("VERSION", archive.namelist())
                self.assertIn("CHANGELOG.md", archive.namelist())


if __name__ == "__main__":
    unittest.main()
