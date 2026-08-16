#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, urllib.request
from datetime import date, timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--as-of",default=date.today().isoformat());ap.add_argument("--warn-days",type=int,default=2);ap.add_argument("--check-urls",action="store_true");ap.add_argument("--json-output");ap.add_argument("--markdown-output");args=ap.parse_args()
    as_of=date.fromisoformat(args.as_of);cutoff=as_of+timedelta(days=args.warn_days)
    data=json.loads((ROOT/"data/pax-silica.json").read_text(encoding="utf-8"));sources=json.loads((ROOT/"data/sources.json").read_text(encoding="utf-8"))["sources"]
    due=[]
    for kind,records in (("source",sources),("claim",data["claims"]),("program",data["programs"])):
        for r in records:
            if not r.get("review_by"):continue
            review=date.fromisoformat(r["review_by"])
            if review<=cutoff: due.append({"kind":kind,"id":r.get("id",r.get("opportunity_id","record")),"review_by":r["review_by"],"days":(review-as_of).days})
    health=[]
    if args.check_urls:
        for s in sources:
            try:
                req=urllib.request.Request(s["url"],headers={"User-Agent":"BridgeNode7-PaxSilica-SourceWatch/1.0"})
                with urllib.request.urlopen(req,timeout=15) as resp:
                    resp.read(1024);health.append({"id":s["id"],"status":resp.status,"ok":200<=resp.status<400})
            except Exception as exc: health.append({"id":s["id"],"ok":False,"error":str(exc)[:180]})
    report={"as_of":args.as_of,"warn_days":args.warn_days,"needs_review":bool(due or any(not h.get("ok") for h in health)),"due":due,"source_health":health}
    if args.json_output: Path(args.json_output).write_text(json.dumps(report,indent=2)+"\n", encoding="utf-8")
    md=["# Pax Silica intelligence watch",f"As of: {args.as_of}",""]
    if due:
        md += ["## Review due"]+[f'- `{x["kind"]}:{x["id"]}` — review by {x["review_by"]} ({x["days"]} days)' for x in due]
    if health:
        failed=[h for h in health if not h.get("ok")]
        md += ["","## Source health",f"{len(health)-len(failed)}/{len(health)} source URLs responded successfully."]
        md += [f'- `{h["id"]}` — {h.get("error","unavailable")}' for h in failed]
    if not due and not any(not h.get("ok") for h in health): md += ["No review action required."]
    if args.markdown_output: Path(args.markdown_output).write_text("\n".join(md)+"\n", encoding="utf-8")
    print(json.dumps(report))
if __name__=="__main__":main()
