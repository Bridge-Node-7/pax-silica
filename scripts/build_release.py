#!/usr/bin/env python3
"""Build deterministic evidence for the next meaningful Pax Silica release."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], check=True, capture_output=True
    )
    return sorted(item.decode("utf-8") for item in result.stdout.split(b"\0") if item)


def release_notes(root: Path, version: str) -> str:
    lines = (root / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    marker = f"## {version}"
    start = lines.index(marker)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    body = "\n".join(lines[start + 1 : end]).strip()
    if not body:
        raise ValueError(f"CHANGELOG entry {marker!r} has no release notes")
    return f"# Pax Silica v{version}\n\n{body}\n"


def build(root: Path, output: Path, commit: str) -> dict[str, str]:
    root, output = root.resolve(), output.resolve()
    if output == root or root in output.parents:
        raise ValueError("release output must be outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    archive = output / f"pax-silica-v{version}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for relative in tracked_files(root):
            info = zipfile.ZipInfo(relative, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, (root / relative).read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    notes = release_notes(root, version)
    (output / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8", newline="\n")
    evidence = {
        "project": "Pax Silica",
        "version": version,
        "tag": f"v{version}",
        "source_commit": commit,
        "archive": archive.name,
        "archive_sha256": digest,
        "validation": "python scripts/check_repo.py",
    }
    (output / "VALIDATION_EVIDENCE.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    (output / "SHA256SUMS").write_text(f"{digest}  {archive.name}\n", encoding="utf-8", newline="\n")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=ROOT)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    print(json.dumps(build(Path(args.root), Path(args.output_dir), args.commit), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
