#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
TEXT_EXT={".md",".json",".py",".html",".css",".js",".yml",".yaml",".txt"}
patterns=[
    (re.compile(r"AKIA[0-9A-Z]{16}"),"AWS key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),"private key"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),"GitHub token"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"),"GitHub token"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"),"API secret"),
    (re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\\\r\n]+"),"Windows user path"),
    (re.compile(r"/home/[^/\s]+/"),"home path"),
]
allowed_email={"contact@bridgenode7.com"}
def main():
    errors=[]
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or p.suffix.lower() not in TEXT_EXT or p.resolve()==Path(__file__).resolve(): continue
        text=p.read_text(encoding="utf-8",errors="ignore")
        for rx,label in patterns:
            if rx.search(text): errors.append(f"{p.relative_to(ROOT)}: {label}")
        emails=set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",text,re.I))
        bad=emails-allowed_email
        if bad: errors.append(f"{p.relative_to(ROOT)}: unapproved email(s) {sorted(bad)}")
    if errors: raise SystemExit("\n".join(errors))
    print("PASS - public boundary")
if __name__=="__main__": main()
