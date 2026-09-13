#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    ".editorconfig", ".gitattributes", ".gitignore",
    ".github/ISSUE_TEMPLATE/config.yml", ".github/ISSUE_TEMPLATE/public-source-correction.yml",
    ".github/workflows/browser-uat.yml", ".github/workflows/ci.yml", ".github/workflows/codeql.yml",
    ".github/workflows/freshness.yml", ".github/workflows/pages.yml",
    "CHANGELOG.md", "LICENSE", "Makefile", "NOTICE", "README.md", "SECURITY.md", "VERSION",
    "data/evidence-baseline.json", "data/pax-silica.json", "data/schemas/pax-silica.schema.json",
    "data/schemas/sources.schema.json", "data/sources.json", "docs/CREDIBILITY.md", "docs/SOURCE_STATES.md",
    "requirements-browser.lock", "scripts/audit_readability.py", "scripts/browser_smoke.py", "scripts/browser_uat.py",
    "scripts/build_web.py", "scripts/check_evidence_integrity.py", "scripts/check_public_boundary.py",
    "scripts/check_repo.py", "scripts/serve_preview.py", "scripts/validate_data.py", "scripts/verify_production.py",
    "tests/test_bn7_synergy.py", "tests/test_build.py", "tests/test_data.py", "tests/test_encoding_contract.py",
    "tests/test_git_hygiene.py", "tests/test_hardening_v026.py", "tests/test_hardening_v027.py", "tests/test_html.py",
    "tests/test_public_release.py", "tests/test_release_polish.py", "web/app.js", "web/index.template.html",
    "web/map-display.json", "web/styles.css",
}

FORBIDDEN = {
    "ROADMAP.md", "PROJECT_FACTS.json", "MANIFEST.json", "analysis", "intelligence", "governance",
    "docs/INTELLIGENCE_MODEL.md", "docs/MAINTENANCE.md", "docs/PUBLIC_BOUNDARY.md",
    "docs/RELEASE_ENGINEERING.md", "docs/VISUAL_CONTRACT.md",
}

def files_digest(root):
    root = Path(root)
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*") if p.is_file()
    }

def run(*args):
    result = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"FAIL - {Path(args[0]).name} exited with status {result.returncode}")

def check_release_identity():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        raise SystemExit("empty VERSION")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {version}\n" not in changelog:
        raise SystemExit("CHANGELOG does not contain current VERSION")
    baseline = json.loads((ROOT / "data/evidence-baseline.json").read_text(encoding="utf-8"))
    if baseline.get("release") != f"v{version}":
        raise SystemExit("evidence baseline release does not match VERSION")
    print(f"PASS - release identity v{version}")

def main():
    missing = [rel for rel in sorted(REQUIRED) if not (ROOT / rel).exists()]
    if missing:
        raise SystemExit("missing required files: " + ", ".join(missing))
    present_forbidden = [rel for rel in sorted(FORBIDDEN) if (ROOT / rel).exists()]
    if present_forbidden:
        raise SystemExit("unnecessary public artifacts remain: " + ", ".join(present_forbidden))

    check_release_identity()
    run(ROOT / "scripts/validate_data.py")
    run(ROOT / "scripts/check_public_boundary.py")
    run(ROOT / "scripts/audit_readability.py")

    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        run(ROOT / "scripts/build_web.py", "--output", a)
        run(ROOT / "scripts/build_web.py", "--output", b)
        if files_digest(a) != files_digest(b):
            raise SystemExit("non-deterministic build")
        run(ROOT / "scripts/check_evidence_integrity.py", "--root", ROOT, "--build-html", Path(a) / "index.html")
        public_env = os.environ.copy()
        public_env["BN7_SCAN_ROOT"] = str(Path(a).resolve())
        result = subprocess.run([sys.executable, str(ROOT / "scripts/check_public_boundary.py")], cwd=ROOT, env=public_env)
        if result.returncode != 0:
            raise SystemExit(f"FAIL - check_public_boundary.py exited with status {result.returncode}")

    print("PASS - deterministic build")
    print("PASS - evidence integrity")
    print("PASS - generated public boundary")

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=ROOT,
    )
    if result.returncode != 0:
        raise SystemExit(f"FAIL - unittest discovery exited with status {result.returncode}")

    print("PASS - tests")
    print("PASS - repository gate")

if __name__ == "__main__":
    main()
