#!/usr/bin/env python3
from __future__ import annotations
import hashlib, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED={
"README.md","VERSION","PROJECT_FACTS.json","SECURITY.md","LICENSE","NOTICE",
"data/pax-silica.json","data/sources.json","web/index.template.html","web/styles.css","web/app.js",
"scripts/build_web.py","scripts/validate_data.py","scripts/check_public_boundary.py","scripts/browser_uat.py","scripts/verify_production.py",
".github/workflows/ci.yml",".github/workflows/browser-uat.yml",".github/workflows/pages.yml",".github/workflows/intelligence-watch.yml",
"docs/BRIDGENODE7_INTEGRATION.md","docs/CREDIBILITY.md","docs/LIVE_INTELLIGENCE.md","tests/test_bn7_synergy.py","tests/test_release_polish.py","tests/test_live_intelligence.py","tests/test_intelligence_watch.py","scripts/audit_readability.py","scripts/intelligence_watch.py","scripts/live_intelligence.py","automation/live-intelligence-policy.json","automation/candidate.schema.json",".github/workflows/live-intelligence.yml","Makefile",".editorconfig",".gitattributes"
}
def files_digest(root):
    root=Path(root)
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
def run(*args): subprocess.check_call([sys.executable,*map(str,args)],cwd=ROOT)
def main():
    missing=[p for p in sorted(REQUIRED) if not (ROOT/p).exists()]
    if missing: raise SystemExit("missing required files: "+", ".join(missing))
    run(ROOT/"scripts/validate_data.py")
    run(ROOT/"scripts/check_public_boundary.py")
    run(ROOT/"scripts/audit_readability.py")
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        run(ROOT/"scripts/build_web.py","--output",a);run(ROOT/"scripts/build_web.py","--output",b)
        if files_digest(a)!=files_digest(b): raise SystemExit("non-deterministic build")
    print("PASS - deterministic build")
    subprocess.check_call([sys.executable,"-m","unittest","discover","-s","tests","-p","test_*.py"],cwd=ROOT)
    print("PASS - tests")
    print("PASS - repository gate")
if __name__=="__main__": main()
