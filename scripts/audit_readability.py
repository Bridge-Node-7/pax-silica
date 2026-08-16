#!/usr/bin/env python3
from __future__ import annotations
import re, subprocess, sys, tempfile
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class VisibleText(HTMLParser):
    def __init__(self): super().__init__();self.skip=0;self.paras=[];self.h2=[];self.stack=[]
    def handle_starttag(self,t,a):
        if t in {"script","style"}: self.skip+=1
        self.stack.append(t)
    def handle_endtag(self,t):
        if t in {"script","style"} and self.skip:self.skip-=1
        if self.stack:self.stack.pop()
    def handle_data(self,d):
        if self.skip:return
        text=" ".join(d.split())
        if not text:return
        if self.stack and self.stack[-1]=="h2": self.h2.append(text)
        if self.stack and self.stack[-1]=="p": self.paras.append(text)
def main():
    with tempfile.TemporaryDirectory() as d:
        subprocess.check_call([sys.executable,str(ROOT/"scripts/build_web.py"),"--output",d],cwd=ROOT,stdout=subprocess.DEVNULL)
        text=(Path(d)/"index.html").read_text(encoding="utf-8")
        p=VisibleText();p.feed(text)
        visible=" ".join(p.h2+p.paras)
        if re.search(r"\\b(?:you|your|yours|yourself|yourselves)\\b",visible,re.I): raise SystemExit("spoken-language audit: second-person language found")
        for h in p.h2:
            if len(re.findall(r"\\b[\\w’'-]+\\b",h))>6: raise SystemExit(f"spoken-language audit: long section heading: {h}")
        for para in p.paras:
            # Evidence support rows are structured metadata, not spoken prose.
            if para.startswith("Supports:"): continue
            for sent in re.split(r"(?<=[.!?])\\s+",para):
                words=re.findall(r"\\b[\\w’'-]+\\b",sent)
                if len(words)>38: raise SystemExit(f"spoken-language audit: sentence >38 words: {sent}")
    print("PASS - spoken-language audit")
if __name__=="__main__":main()
