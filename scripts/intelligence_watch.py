#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_STATUSES = {401, 403, 405, 429}
UNAVAILABLE_STATUSES = {404, 410}


def classify_http_status(status: int) -> str:
    if 200 <= status < 400:
        return "ok"
    if status in MANUAL_STATUSES:
        return "manual_verification"
    if status in UNAVAILABLE_STATUSES:
        return "unavailable"
    if status >= 500:
        return "temporary_error"
    return "manual_verification"


def health_requires_review(record: dict) -> bool:
    return record.get("state") == "unavailable"


def check_source(source: dict) -> dict:
    try:
        req = urllib.request.Request(source["url"], headers={"User-Agent": "BridgeNode7-PaxSilica-SourceWatch/2.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read(1024)
            status = int(resp.status)
            state = classify_http_status(status)
            return {"id": source["id"], "status": status, "state": state, "ok": state == "ok"}
    except urllib.error.HTTPError as exc:
        state = classify_http_status(int(exc.code))
        return {"id": source["id"], "status": int(exc.code), "state": state, "ok": state == "ok", "error": str(exc)[:180]}
    except Exception as exc:
        return {"id": source["id"], "state": "temporary_error", "ok": False, "error": str(exc)[:180]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--warn-days", type=int, default=2)
    ap.add_argument("--check-urls", action="store_true")
    ap.add_argument("--json-output")
    ap.add_argument("--markdown-output")
    args = ap.parse_args()
    as_of = date.fromisoformat(args.as_of)
    cutoff = as_of + timedelta(days=args.warn_days)
    data = json.loads((ROOT / "data/pax-silica.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))["sources"]
    due = []
    for kind, records in (("source", sources), ("claim", data["claims"]), ("program", data["programs"])):
        for record in records:
            if not record.get("review_by"):
                continue
            review = date.fromisoformat(record["review_by"])
            if review <= cutoff:
                due.append({"kind": kind, "id": record.get("id", record.get("opportunity_id", "record")), "review_by": record["review_by"], "days": (review - as_of).days})
    health = [check_source(s) for s in sources] if args.check_urls else []
    unavailable = [h for h in health if health_requires_review(h)]
    report = {"as_of": args.as_of, "warn_days": args.warn_days, "needs_review": bool(due or unavailable), "due": due, "source_health": health}
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = ["# Pax Silica intelligence watch", f"As of: {args.as_of}", ""]
    if due:
        md += ["## Review due"] + [f'- `{x["kind"]}:{x["id"]}` — review by {x["review_by"]} ({x["days"]} days)' for x in due]
    if health:
        counts = {}
        for item in health:
            counts[item["state"]] = counts.get(item["state"], 0) + 1
        md += ["", "## Source health", f'{counts.get("ok", 0)} ok · {counts.get("manual_verification", 0)} manual verification · {counts.get("temporary_error", 0)} temporary error · {counts.get("unavailable", 0)} unavailable']
        for item in health:
            if item["state"] != "ok":
                md.append(f'- `{item["id"]}` — {item["state"]}' + (f' · HTTP {item["status"]}' if item.get("status") else "") + (f' · {item["error"]}' if item.get("error") else ""))
    if not due and not unavailable:
        md += ["", "No canonical intelligence review action required."]
    if args.markdown_output:
        Path(args.markdown_output).write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
