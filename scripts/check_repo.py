#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/public-source-correction.yml",
    ".github/workflows/browser-uat.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/codeql.yml",
    ".github/workflows/pages.yml",
    "CHANGELOG.md",
    "LICENSE",
    "Makefile",
    "NOTICE",
    "PROJECT_FACTS.json",
    "README.md",
    "SECURITY.md",
    "VERSION",
    "analysis/philippines-capability-accumulation.md",
    "analysis/provenance-vs-qualification.md",
    "analysis/time-to-switch.md",
    "data/evidence-baseline.json",
    "data/pax-silica.json",
    "data/schemas/pax-silica.schema.json",
    "data/schemas/sources.schema.json",
    "data/sources.json",
    "docs/CREDIBILITY.md",
    "docs/INTELLIGENCE_MODEL.md",
    "docs/MAINTENANCE.md",
    "docs/PUBLIC_BOUNDARY.md",
    "docs/RELEASE_ENGINEERING.md",
    "docs/SOURCE_STATES.md",
    "docs/VISUAL_CONTRACT.md",
    "requirements-browser.lock",
    "scripts/audit_readability.py",
    "scripts/browser_uat.py",
    "scripts/build_web.py",
    "scripts/check_evidence_integrity.py",
    "scripts/check_public_boundary.py",
    "scripts/check_repo.py",
    "scripts/serve_preview.py",
    "scripts/validate_data.py",
    "scripts/verify_production.py",
    "tests/test_bn7_synergy.py",
    "tests/test_build.py",
    "tests/test_data.py",
    "tests/test_encoding_contract.py",
    "tests/test_git_hygiene.py",
    "tests/test_html.py",
    "tests/test_public_release.py",
    "tests/test_release_polish.py",
    "web/app.js",
    "web/index.template.html",
    "web/styles.css",
}

def files_digest(root):
    root = Path(root)
    return {
        p.relative_to(root).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }

def run(*args):
    subprocess.check_call(
        [sys.executable, *map(str, args)],
        cwd=ROOT,
    )

def main():
    missing = [
        rel for rel in sorted(REQUIRED)
        if not (ROOT / rel).exists()
    ]
    if missing:
        raise SystemExit(
            "missing required files: " + ", ".join(missing)
        )

    run(ROOT / "scripts/validate_data.py")
    run(ROOT / "scripts/check_public_boundary.py")
    run(ROOT / "scripts/audit_readability.py")

    with tempfile.TemporaryDirectory() as a, \
         tempfile.TemporaryDirectory() as b:
        run(ROOT / "scripts/build_web.py", "--output", a)
        run(ROOT / "scripts/build_web.py", "--output", b)
        if files_digest(a) != files_digest(b):
            raise SystemExit("non-deterministic build")

        run(
            ROOT / "scripts/check_evidence_integrity.py",
            "--root", ROOT,
            "--build-html", Path(a) / "index.html",
        )

    print("PASS - deterministic build")
    print("PASS - evidence integrity")

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ],
        cwd=ROOT,
    )

    print("PASS - tests")
    print("PASS - repository gate")

if __name__ == "__main__":
    main()
