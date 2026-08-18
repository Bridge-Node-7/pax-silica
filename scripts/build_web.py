#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STATE_LABELS = {
    "official": "Official public source",
    "secondary": "Secondary source",
    "reported_draft": "Reported Development",
}
GROUP_LABELS = {
    "official": "Official Sources",
    "secondary": "Secondary Sources",
    "reported_draft": "Reported Development",
}
GROUP_ORDER = ("official", "secondary", "reported_draft")

REGION_ORDER = ("Americas", "Europe", "Indo-Pacific", "Middle East", "Central Asia")

# Editorially selected milestones for the public learning path.
# Selection basis: material changes to participation, policy alignment, or implementation.
TIMELINE_IDS = ("E-001", "E-003", "E-004", "E-005", "E-006", "E-007")
TIMELINE_TITLES = {
    "E-001": "Pax Silica launches",
    "E-003": "Quantum alignment",
    "E-004": "Second Pax Silica Summit",
    "E-005": "Defense supply-chain alignment",
    "E-006": "Italy joins",
    "E-007": "Implementation expands",
}


def fmt_date(iso: str) -> str:
    y, m, d = map(int, iso.split("-"))
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    return f"{d} {months[m - 1]} {y}"


def joined_label(record: dict) -> str:
    if record.get("founding"):
        return "Founding signatory"
    joined = record.get("joined")
    if joined:
        y, m, _ = map(int, joined.split("-"))
        months = ("January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December")
        return f"Joined {months[m - 1]} {y}"
    return "Accession date not established in reviewed record"


def roster_label(record: dict) -> str:
    label = joined_label(record)

    if (
        record.get("entity_type")
        == "institution"
    ):
        return (
            "Institution · "
            + label
        )

    return label


def entity_type_label(record: dict) -> str:
    if (
        record.get("entity_type")
        == "institution"
    ):
        return "Institution"

    return "Country"


def status_label(record: dict) -> str:
    return (
        "Founding signatory"
        if record.get("founding")
        else "Declaration signatory"
    )


def render_markers(active: list[dict], map_positions: dict) -> str:
    missing = sorted(x["name"] for x in active if x["name"] not in map_positions)
    if missing:
        raise SystemExit("map metadata missing for active signatories: " + ", ".join(missing))
    rows = []
    for x in sorted(active, key=lambda r: r["name"]):
        name = x["name"]
        meta = map_positions[name]
        px = float(meta["x"])
        py = float(meta["y"])
        map_name = str(meta["map_name"])
        founding = bool(x.get("founding"))
        css = "map-node founding" if founding else "map-node"
        status = status_label(x)
        joined = joined_label(x)
        rows.append(
            f'<g aria-label="{html.escape(name, quote=True)}" class="{css}" '
            f'data-joined="{html.escape(joined, quote=True)}" '
            f'data-map-marker="{html.escape(name, quote=True)}" '
            f'data-map-name="{html.escape(map_name, quote=True)}" '
            f'data-region="{html.escape(x["region"], quote=True)}" '
            f'data-entity-type="{html.escape(entity_type_label(x), quote=True)}" '
            f'data-status="{status}" role="button" tabindex="0" '
            f'transform="translate({px:.1f} {py:.1f})">'
            '<circle class="halo" r="13"></circle><circle class="dot" r="5"></circle>'
            f'<text x="10" y="-9">{html.escape(name)}</text></g>'
        )
    return "".join(rows)


def render_roster(active: list[dict]) -> str:
    sections = []
    observed = {x["region"] for x in active}
    order = list(REGION_ORDER) + sorted(observed - set(REGION_ORDER))
    for region in order:
        members = sorted((x for x in active if x["region"] == region), key=lambda r: r["name"])
        if not members:
            continue
        buttons = []
        for x in members:
            buttons.append(
                f'<button aria-pressed="false" class="roster-person" data-roster-country="{html.escape(x["name"], quote=True)}" '
                f'data-entity-type="{html.escape(entity_type_label(x), quote=True)}" type="button">'
                f'<strong>{html.escape(x["name"])}</strong>'
                f'<small>{html.escape(roster_label(x))}</small></button>'
            )
        sections.append(
            f'<section><h3>{html.escape(region)}</h3>'
            f'<div class="roster-people">{"".join(buttons)}</div></section>'
        )
    return "".join(sections)


def render_timeline(data: dict) -> str:
    event_map = {e["id"]: e for e in data["events"]}
    missing = [eid for eid in TIMELINE_IDS if eid not in event_map]
    if missing:
        raise SystemExit("timeline event missing from canonical data: " + ", ".join(missing))
    rows = []
    for eid in TIMELINE_IDS:
        e = event_map[eid]
        if not e.get("source_ids"):
            raise SystemExit(f"timeline event {eid} lacks evidence")
        source_id = e["source_ids"][0]
        rows.append(
            f'<article class="timeline-event" data-evidence-state="{html.escape(e["state"], quote=True)}">'
            f'<time>{html.escape(fmt_date(e["date"]))}</time><div>'
            f'<h3>{html.escape(TIMELINE_TITLES.get(eid, e["title"]))}</h3>'
            f'<p>{html.escape(e["summary"])}</p>'
            f'<button class="timeline-evidence" data-open-evidence="{html.escape(source_id, quote=True)}" '
            'type="button">Evidence</button></div></article>'
        )
    return "".join(rows)


def render_evidence(sources: list[dict]) -> str:
    sections = []
    for state in GROUP_ORDER:
        group = [s for s in sources if s["state"] == state]
        if not group:
            continue
        rows = []
        for s in group:
            meta = []
            if s.get("published"):
                meta.append("Published " + fmt_date(s["published"]))
            meta.append("Reviewed " + fmt_date(s["verified_at"]))
            if s.get("review_by"):
                meta.append("Review by " + fmt_date(s["review_by"]))
            supports = "; ".join(s.get("supports", []))
            limit = s.get("note", "")
            label = STATE_LABELS[state]
            rows.append(
                f'<article class="source-record" data-evidence-state="{html.escape(state, quote=True)}" '
                f'data-source-id="{html.escape(s["id"], quote=True)}" '
                f'data-publisher="{html.escape(s["publisher"], quote=True)}">'
                '<div class="source-record-main">'
                f'<span class="state {html.escape(state, quote=True)}">{html.escape(label)}</span>'
                f'<h4>{html.escape(s["publisher"])} · {html.escape(s["title"].replace("—", ":"))}</h4></div>'
                '<div class="source-record-detail">'
                f'<p class="source-meta">{html.escape(" · ".join(meta))}</p>'
                f'<p>{html.escape(supports)}</p>'
                f'<p class="source-limit">{html.escape(limit)}</p></div>'
                '<div class="source-record-actions">'
                f'<a href="{html.escape(s["url"], quote=True)}" target="_blank" rel="noopener">Open original ↗</a>'
                '</div></article>'
            )
        sections.append(
            f'<section class="evidence-source-group {html.escape(state, quote=True)}" '
            f'data-evidence-group="{html.escape(state, quote=True)}">'
            f'<div class="evidence-group-title"><h3>{GROUP_LABELS[state]}</h3>'
            f'<span>{len(group)}</span></div>{"".join(rows)}</section>'
        )
    return "".join(sections)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="build/web")
    args = ap.parse_args()

    out = Path(args.output)
    out = out if out.is_absolute() else ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    (out / "data").mkdir(exist_ok=True)

    data = json.loads((ROOT / "data/pax-silica.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))["sources"]
    map_positions = json.loads((ROOT / "web/map-display.json").read_text(encoding="utf-8"))["positions"]
    claims = {c["id"]: c for c in data["claims"]}
    active = [x for x in data["signatories"] if x.get("status") == "active"]

    # R17 is explicitly a declaration-signatory map. Do not silently mix evidence states.
    if any(x.get("evidence_state") != "official" for x in active):
        raise SystemExit("active map contains non-official declaration membership; evolve ontology explicitly")
    if "C-001" not in claims or "C-005" not in claims:
        raise SystemExit("required public claims C-001/C-005 missing")

    source_ids = {s["id"] for s in sources}
    for sid in ("S-01", "S-02", "S-03", "S-04", "S-05", "S-07", "S-10", "S-11"):
        if sid not in source_ids:
            raise SystemExit(f"required public evidence missing: {sid}")

    philippines_intro = (
        "Pax Silica is global. "
        + claims["C-005"]["text"]
        + " Independent reporting places the planned hub in New Clark City."
    )

    repl = {
        "{{CLAIM_C001}}": html.escape(claims["C-001"]["text"]),
        "{{SNAPSHOT_DATE}}": html.escape(
            fmt_date(data["snapshot"]["verified_through"])
        ),
        "{{SIGNATORY_COUNT}}": str(len(active)),
        "{{MAP_MARKERS}}": render_markers(active, map_positions),
        "{{NETWORK_ROSTER}}": render_roster(active),
        "{{NETWORK_TIMELINE}}": render_timeline(data),
        "{{PHILIPPINES_INTRO}}": html.escape(philippines_intro),
        "{{EVIDENCE_LIST}}": render_evidence(sources),
    }

    text = (ROOT / "web/index.template.html").read_text(encoding="utf-8")
    for key, value in repl.items():
        text = text.replace(key, value)

    unresolved = re.findall(r"\{\{[A-Z0-9_]+\}\}", text)
    if unresolved:
        raise SystemExit("unresolved template token(s): " + ", ".join(sorted(set(unresolved))))

    (out / "index.html").write_text(text, encoding="utf-8", newline="\n")
    (out / "styles.css").write_bytes((ROOT / "web/styles.css").read_bytes())
    (out / "app.js").write_bytes((ROOT / "web/app.js").read_bytes())
    (out / "data/pax-silica.json").write_bytes((ROOT / "data/pax-silica.json").read_bytes())
    (out / "data/sources.json").write_bytes((ROOT / "data/sources.json").read_bytes())

    files = ("app.js", "data/pax-silica.json", "data/sources.json", "index.html", "styles.css")
    manifest = "\n".join(
        f'{hashlib.sha256((out / rel).read_bytes()).hexdigest()}  {rel}'
        for rel in files
    ) + "\n"
    (out / "WEB_MANIFEST.sha256").write_text(manifest, encoding="utf-8", newline="\n")
    print(f"PASS - built {out}")


if __name__ == "__main__":
    main()
