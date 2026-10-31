#!/usr/bin/env python3
"""Align VERSION, evidence baseline, strip pre-tag CHANGELOG compare URLs."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
COMPARE_HEADING_RE = re.compile(
    r"(^## \[\d+\.\d+\.\d+\])\(https://github\.com/[^\s)]+/compare/[^\s)]+\)( \(\d{4}-\d{2}-\d{2}\))",
    re.MULTILINE,
)
def main() -> int:
    root = Path(".").resolve()
    version = str(json.loads((root / ".release-please-manifest.json").read_text(encoding="utf-8")).get(".", "")).strip()
    if not VERSION_RE.fullmatch(version):
        print(f"FAIL: invalid manifest version {version!r}", file=sys.stderr); return 1
    vp = root / "VERSION"
    if vp.read_text(encoding="utf-8").strip() != version:
        vp.write_text(version + "\n", encoding="utf-8", newline="\n")
        print(f"PASS: aligned VERSION to {version}")
    else:
        print(f"PASS: VERSION already {version}")
    cl = root / "CHANGELOG.md"
    text = cl.read_text(encoding="utf-8")
    rewritten, n = COMPARE_HEADING_RE.subn(r"\1\2", text, count=1)
    if n:
        cl.write_text(rewritten, encoding="utf-8", newline="\n")
        print("PASS: stripped pre-tag CHANGELOG compare URL")
    else:
        print("PASS: CHANGELOG compare heading already plain or absent")
    b = root / "data/evidence-baseline.json"
    data = json.loads(b.read_text(encoding="utf-8"))
    if data.get("release") != f"v{version}":
        data["release"] = f"v{version}"
        b.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("PASS: aligned evidence baseline release")
    else:
        print("PASS: evidence baseline already aligned")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
