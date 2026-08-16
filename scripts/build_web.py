#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib, html, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

STATE_LABELS={
    "official":"OFFICIAL","secondary":"SECONDARY","reported_draft":"REPORTED / DRAFT",
    "bn7_analysis":"BN7 ANALYSIS","unknown":"UNKNOWN","superseded":"SUPERSEDED"
}
STATE_GROUPS=[("official","PRIMARY / OFFICIAL"),("secondary","SECONDARY"),("reported_draft","REPORTED / DRAFT"),("bn7_analysis","BN7 ANALYSIS"),("unknown","UNKNOWN"),("superseded","SUPERSEDED")]

def money(n:int)->str:
    return f"${n//1_000_000}M" if n>=1_000_000 else f"${n:,}"

def state_label(state:str)->str:
    return STATE_LABELS.get(state,state.upper())

def fmt_date(iso:str)->str:
    y,m,d=map(int,iso.split("-"));months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return f"{d} {months[m-1]} {y}"

def fmt_short(iso:str)->str:
    y,m,d=map(int,iso.split("-"));months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return f"{months[m-1]} {d}, {y}"

def evidence_dates(s:dict)->str:
    parts=[]
    if s.get("standing_reference"): parts.append("<span><b>Record</b> Standing reference</span>")
    if s.get("published"): parts.append(f'<span><b>Published</b> {html.escape(fmt_short(s["published"]))}</span>')
    parts.append(f'<span><b>Verified</b> {html.escape(fmt_short(s["verified_at"]))}</span>')
    if s.get("review_by"): parts.append(f'<span class="review-date"><b>Review by</b> {html.escape(fmt_short(s["review_by"]))}</span>')
    return "".join(parts)

def evidence_sort_key(s:dict):
    # Standing reference leads the official group. Otherwise newest publication first.
    standing=1 if s.get("standing_reference") else 0
    published=s.get("published","")
    return (standing,published,s.get("verified_at",""),s["id"])

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",default="build/web");args=ap.parse_args()
    out=Path(args.output);out=out if out.is_absolute() else ROOT/out;out.mkdir(parents=True,exist_ok=True);(out/"data").mkdir(exist_ok=True)
    data=json.loads((ROOT/"data/pax-silica.json").read_text(encoding="utf-8"))
    sources=json.loads((ROOT/"data/sources.json").read_text(encoding="utf-8"))["sources"]
    claims={c["id"]:c for c in data["claims"]}
    active=[x for x in data["signatories"] if x.get("status")=="active"]
    founders=[x for x in active if x.get("founding")]
    official_signatories=[x for x in active if x.get("evidence_state")=="official"]
    declaration_metric=str(len(active)) if len(official_signatories)==len(active) else f"{len(official_signatories)} / {len(active)}"
    declaration_meta="declaration signatories" if len(official_signatories)==len(active) else "official / tracked"
    regions=["All"]+sorted({x["region"] for x in active})
    filters="".join(f'<button aria-pressed="{str(i==0).lower()}" data-region="{html.escape(r)}">{html.escape(r)}</button>' for i,r in enumerate(regions))
    cards="".join(f'<div class="member" data-region="{html.escape(x["region"])}"><strong>{html.escape(x["name"])}</strong><small>{html.escape(x["region"])}{" · tracked" if x.get("evidence_state")!="official" else ""}</small></div>' for x in sorted(active,key=lambda x:x["name"]))
    events=sorted(data["events"],key=lambda e:e["date"],reverse=True)
    event_html="".join(f'<article class="event"><time>{html.escape(fmt_date(e["date"]))}</time><div><span class="state {html.escape(e["state"])}">{state_label(e["state"])}</span><h3>{html.escape(e["title"])}</h3><p>{html.escape(e["summary"])}</p></div></article>' for e in events)
    official_events=[e for e in events if e.get("state")=="official"]
    if not official_events: raise SystemExit("no official event available for hero signal")
    latest=official_events[0]
    program=data["programs"][0]
    controls=[]
    for i,(name,val) in enumerate(zip(["Detect","Decide","Contract","Tooling","Qualify","Regulatory","Logistics","Ramp"],[3,5,14,30,75,20,10,45])):
        controls.append(f'<div class="control"><label><span>{name}</span><output id="out{i}">{val}d</output></label><input id="in{i}" type="range" min="0" max="120" value="{val}" aria-label="{name} days"></div>')
    evidence_groups=[]
    for state,label in STATE_GROUPS:
        group=sorted([s for s in sources if s["state"]==state],key=evidence_sort_key,reverse=True)
        if not group: continue
        rows=[]
        for s in group:
            rows.append(
                f'<article class="evidence-card" id="source-{html.escape(s["id"])}">'
                f'<div class="evidence-id"><code>{html.escape(s["id"])}</code><span class="state {html.escape(s["state"])}">{state_label(s["state"])}</span></div>'
                f'<div class="evidence-body"><h3>{html.escape(s["publisher"])} · {html.escape(s["title"])}</h3>'
                f'<div class="evidence-dates">{evidence_dates(s)}</div>'
                f'<p class="evidence-note">{html.escape(s["note"])}</p>'
                f'<p class="evidence-supports"><strong>Supports:</strong> {html.escape("; ".join(s["supports"]))}</p>'
                f'<a href="{html.escape(s["url"])}" target="_blank" rel="noopener">Open source ↗</a></div></article>'
            )
        evidence_groups.append(f'<section class="evidence-group" data-evidence-group="{html.escape(state)}"><div class="evidence-group-head"><h3>{label}</h3><span>{len(group)}</span></div>{"".join(rows)}</section>')
    t=(ROOT/"web/index.template.html").read_text(encoding="utf-8")
    repl={
        "{{VERIFIED_THROUGH}}":fmt_date(data["snapshot"]["verified_through"]),"{{LATEST_SIGNAL}}":html.escape(latest["summary"]),
        "{{LATEST_SIGNAL_STATE}}":state_label(latest["state"]),"{{LATEST_SIGNAL_DATE}}":fmt_date(latest["date"]),"{{SIGNATORY_COUNT}}":str(len(active)),
        "{{OFFICIAL_SIGNATORY_COUNT}}":str(len(official_signatories)),"{{DECLARATION_METRIC}}":declaration_metric,"{{DECLARATION_META}}":declaration_meta,
        "{{FOUNDING_COUNT}}":str(len(founders)),"{{AWARD_MAX}}":money(program["award_max_usd"]),"{{CLOSE_DATE}}":fmt_date(program["close_date"]).replace(" 2026",""),
        "{{PROGRAM_STATUS}}":program["status"].upper()+" · verified "+fmt_date(program["verified_at"]),"{{CLAIM_C001}}":html.escape(claims["C-001"]["text"]),
        "{{CLAIM_A001}}":html.escape(claims["A-001"]["text"]),"{{CLAIM_A002}}":html.escape(claims["A-002"]["text"]),"{{CLAIM_C005}}":html.escape(claims["C-005"]["text"]),
        "{{FILTER_BUTTONS}}":filters,"{{SIGNATORY_CARDS}}":cards,"{{EVENTS}}":event_html,"{{TTS_CONTROLS}}":"".join(controls),"{{EVIDENCE_CARDS}}":"".join(evidence_groups),
    }
    for k,v in repl.items(): t=t.replace(k,v)
    if re.search(r"\\{\\{[A-Z0-9_]+\\}\\}",t): raise SystemExit("unresolved template token")
    (out/"index.html").write_text(t,encoding="utf-8")
    (out/"styles.css").write_bytes((ROOT/"web/styles.css").read_bytes());(out/"app.js").write_bytes((ROOT/"web/app.js").read_bytes())
    (out/"data/pax-silica.json").write_bytes((ROOT/"data/pax-silica.json").read_bytes());(out/"data/sources.json").write_bytes((ROOT/"data/sources.json").read_bytes())
    files=["app.js","data/pax-silica.json","data/sources.json","index.html","styles.css"]
    (out/"WEB_MANIFEST.sha256").write_text("\n".join(f'{hashlib.sha256((out/rel).read_bytes()).hexdigest()}  {rel}' for rel in files)+"\n",encoding="utf-8")
    print(f"PASS - built {out}")
if __name__=="__main__":main()
