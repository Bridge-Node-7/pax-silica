#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_STATES={"official","secondary","reported_draft","bn7_analysis","unknown","superseded"}
ALLOWED_WORKFLOW={"candidate","reviewed","approved","published","retired"}
OFFICIAL_HOSTS={"www.state.gov","state.gov","www.whitehouse.gov","whitehouse.gov","simpler.grants.gov","www.comune.brindisi.it","comune.brindisi.it"}
SECONDARY_HOSTS={"reuters.com","www.reuters.com"}
REPORTED_HOSTS={"reuters.com","www.reuters.com"}

def iso(s):
    try:return date.fromisoformat(s)
    except Exception:raise AssertionError(f"invalid ISO date: {s}")

def main():
    data=json.loads((ROOT/"data/pax-silica.json").read_text(encoding="utf-8"))
    sources=json.loads((ROOT/"data/sources.json").read_text(encoding="utf-8"))["sources"]
    ids=[s["id"] for s in sources]
    assert len(ids)==len(set(ids)),"duplicate source ID"
    sm={s["id"]:s for s in sources}
    verified=iso(data["snapshot"]["verified_through"])
    for s in sources:
        assert s["state"] in ALLOWED_STATES
        assert s["url"].startswith("https://"),f"non-HTTPS source {s['id']}"
        host=(urlsplit(s["url"]).hostname or "").lower()
        if s["state"]=="official": assert host in OFFICIAL_HOSTS,f"official source on unapproved host: {s['id']} {host}"
        if s["state"]=="secondary": assert host in SECONDARY_HOSTS,f"secondary source on unapproved host: {s['id']} {host}"
        if s["state"]=="reported_draft": assert host in REPORTED_HOSTS,f"reported/draft source on unapproved host: {s['id']} {host}"
        va=iso(s["verified_at"])
        if s.get("published"): assert va>=iso(s["published"]),f"verified before publication: {s['id']}"
        if s.get("review_by"): assert iso(s["review_by"])>=verified,f"stale source {s['id']}: review_by {s['review_by']} < snapshot {verified}"
    for group in ("signatories","claims","events","programs"):
        for r in data[group]:
            for sid in r.get("source_ids",[]): assert sid in sm,f"orphan source {sid} in {group}"
            if r.get("state") and group!="signatories": assert r["state"] in ALLOWED_STATES,f"bad state {r.get('state')}"
            if r.get("workflow_state"): assert r["workflow_state"] in ALLOWED_WORKFLOW
            for k in ("date","verified_at","review_by","joined","close_date"):
                if r.get(k): iso(r[k])
            if r.get("review_by"): assert iso(r["review_by"])>=verified,f"stale record {r.get('id')}"
    def source_states(record):
        return {sm[sid]["state"] for sid in record.get("source_ids",[])}
    for c in data["claims"]:
        if c["state"]=="official": assert "official" in source_states(c),f"official claim lacks official source: {c['id']}"
        if c["state"]=="reported_draft": assert "reported_draft" in source_states(c),f"reported/draft claim lacks reported source: {c['id']}"
    for e in data["events"]:
        if e["state"]=="official": assert "official" in source_states(e),f"official event lacks official source: {e['id']}"
        if e["state"]=="reported_draft": assert "reported_draft" in source_states(e),f"reported/draft event lacks reported source: {e['id']}"
    for p in data["programs"]:
        assert "official" in source_states(p),f"program lacks official source: {p['id']}"
    for sgn in data["signatories"]:
        assert sgn.get("evidence_state") in {"official","secondary"},f"signatory evidence_state missing: {sgn['name']}"
        if sgn["evidence_state"]=="official": assert "official" in source_states(sgn),f"official signatory lacks official source: {sgn['name']}"
        if sgn["evidence_state"]=="secondary": assert "secondary" in source_states(sgn),f"secondary signatory lacks secondary source: {sgn['name']}"
    active=[s for s in data["signatories"] if s.get("status")=="active"]
    assert len(active)==25,f"seed snapshot expected 25 active signatories, got {len(active)}"
    assert sum(bool(x.get("founding")) for x in active)==7,"expected 7 founders"
    print("PASS - data integrity")
    print("PASS - freshness")
    print("PASS - source credibility")
if __name__=="__main__": main()
