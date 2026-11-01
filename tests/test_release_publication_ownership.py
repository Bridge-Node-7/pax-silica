"""t91u: release-please must not create GitHub Releases; Stable Release is sole publisher."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RP = ROOT / ".github" / "workflows" / "release-please.yml"
STABLE = ROOT / ".github" / "workflows" / "release.yml"


class ReleasePublicationOwnershipTests(unittest.TestCase):
    def test_release_please_skips_github_release(self) -> None:
        text = RP.read_text(encoding="utf-8")
        self.assertRegex(
            text,
            r"(?m)^\s*skip-github-release:\s*true\s*$",
        )

    def test_stable_release_is_sole_github_release_creator(self) -> None:
        rp = RP.read_text(encoding="utf-8")
        stable = STABLE.read_text(encoding="utf-8")
        self.assertNotIn("gh release create", rp)
        self.assertIn("gh release create", stable)
        self.assertIn("git/tags", stable)
        self.assertIn("dry_run", stable)

    def test_release_please_avoids_pat_secrets(self) -> None:
        text = RP.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"secrets\.[A-Z0-9_]*(TOKEN|PAT|APP)")


if __name__ == "__main__":
    unittest.main()
