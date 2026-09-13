from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_check_repo():
    path = ROOT / "scripts/check_repo.py"
    spec = importlib.util.spec_from_file_location("pax_check_repo", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CloseoutV033Tests(unittest.TestCase):
    def test_local_virtualenv_is_outside_public_boundary_but_real_source_is_not(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            local = root / ".venv/lib/python/site-packages/example.txt"
            local.parent.mkdir(parents=True)
            local.write_text("AKIA1234567890ABCDEF\n", encoding="utf-8")
            env = os.environ.copy()
            env["BN7_SCAN_ROOT"] = str(root)
            clean = subprocess.run(
                [sys.executable, str(ROOT / "scripts/check_public_boundary.py")],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)

            (root / "public.txt").write_text("AKIA1234567890ABCDEF\n", encoding="utf-8")
            finding = subprocess.run(
                [sys.executable, str(ROOT / "scripts/check_public_boundary.py")],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(finding.returncode, 0)
            self.assertIn("AWS key", finding.stdout + finding.stderr)

    def test_expected_child_failure_has_bounded_parent_message(self):
        check_repo = load_check_repo()
        with tempfile.TemporaryDirectory() as td:
            script = Path(td) / "fail.py"
            script.write_text("raise SystemExit(7)\n", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, r"FAIL - fail\.py exited with status 7"):
                check_repo.run(script)


if __name__ == "__main__":
    unittest.main()
