#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, time, urllib.request
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--expected-dir",required=True);ap.add_argument("--base-url",required=True);ap.add_argument("--output",default="production-attestation.json");ap.add_argument("--attempts",type=int,default=8);ap.add_argument("--delay-seconds",type=int,default=10);args=ap.parse_args()
    root=Path(args.expected_dir)
    files=["index.html","styles.css","app.js","data/pax-silica.json","data/sources.json","WEB_MANIFEST.sha256"]
    last={}
    for attempt in range(1,args.attempts+1):
        ok=True;obs={}
        for rel in files:
            try:
                with urllib.request.urlopen(args.base_url.rstrip("/")+"/"+rel,timeout=15) as r:data=r.read()
                obs[rel]={"expected":sha((root/rel).read_bytes()),"actual":sha(data),"bytes":len(data)}
                ok &= obs[rel]["expected"]==obs[rel]["actual"]
            except Exception as e:
                obs[rel]={"error":str(e)};ok=False
        last={"attempt":attempt,"pass":ok,"files":obs}
        if ok:break
        time.sleep(args.delay_seconds)
    Path(args.output).write_text(json.dumps(last,indent=2)+"\n", encoding="utf-8")
    if not last["pass"]: raise SystemExit("production bytes do not match expected build")
    print("PASS - anonymous production readback")
if __name__=="__main__":main()
