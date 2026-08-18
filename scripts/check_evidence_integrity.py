#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
import argparse

DEFAULT_ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default=str(DEFAULT_ROOT))
    ap.add_argument('--build-html', default=None)
    args=ap.parse_args()
    ROOT=Path(args.root).resolve()
    data=json.loads((ROOT/"data/pax-silica.json").read_text(encoding="utf-8"))
    sources=json.loads((ROOT/"data/sources.json").read_text(encoding="utf-8"))["sources"]
    baseline=json.loads((ROOT/"data/evidence-baseline.json").read_text(encoding="utf-8"))
    build_html=Path(args.build_html).resolve() if args.build_html else ROOT/"build/web/index.html"
    html=build_html.read_text(encoding="utf-8")

    sm={s["id"]:s for s in sources}
    assert len(sources) >= baseline["minimum_source_count"], (
        f"source-count regression: {len(sources)} < {baseline['minimum_source_count']}"
    )

    # Every source referenced by public claims/events/programs must still exist.
    referenced=set()
    for group in ("claims","events","programs"):
        for record in data[group]:
            if record.get("public",True):
                referenced.update(record.get("source_ids",[]))
    missing=sorted(referenced-set(sm))
    assert not missing, f"orphan source references: {missing}"

    # Every referenced source must be represented in the built evidence layer.
    rendered=set(re.findall(r'data-source-id="(S-\d{2})"',html))
    unrendered=sorted(referenced-rendered)
    assert not unrendered, f"public evidence referenced but not rendered: {unrendered}"

    # If canonical data contains an evidence state, the built page must preserve it.
    canonical_states={s["state"] for s in sources}
    rendered_states=set(re.findall(r'data-evidence-state="([a-z_]+)"',html))
    for state in baseline["required_rendered_states"]:
        if state in canonical_states:
            assert state in rendered_states, f"rendered evidence taxonomy lost state: {state}"

    # Material public events require evidence.
    for e in data["events"]:
        if e.get("state") in {"official","secondary","reported_draft"}:
            assert e.get("source_ids"), f"material event lacks source: {e.get('id')}"

    print(f"PASS - evidence source ratchet ({len(sources)} sources)")
    print(f"PASS - public source coverage ({len(referenced)} referenced IDs)")
    print("PASS - rendered evidence taxonomy")

if __name__=="__main__":
    main()
