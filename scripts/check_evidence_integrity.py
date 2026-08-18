#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
from pathlib import Path

DEFAULT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        default=str(
            DEFAULT_ROOT
        ),
    )

    parser.add_argument(
        "--build-html",
        default=None,
    )

    args = parser.parse_args()

    root = Path(
        args.root
    ).resolve()

    data = json.loads(
        (
            root
            / "data/pax-silica.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    sources = json.loads(
        (
            root
            / "data/sources.json"
        ).read_text(
            encoding="utf-8"
        )
    )["sources"]

    baseline = json.loads(
        (
            root
            / "data/evidence-baseline.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    build_html = (
        Path(
            args.build_html
        ).resolve()
        if args.build_html
        else
        root
        / "build/web/index.html"
    )

    page_html = (
        build_html.read_text(
            encoding="utf-8"
        )
    )

    source_map = {
        source["id"]: source
        for source in sources
    }

    assert (
        len(sources)
        >= baseline[
            "minimum_source_count"
        ]
    ), (
        "source-count regression: "
        f"{len(sources)} < "
        f"{baseline['minimum_source_count']}"
    )

    referenced = set()

    for group in (
        "claims",
        "events",
        "programs",
    ):
        for record in data[group]:
            if record.get(
                "public",
                True,
            ):
                referenced.update(
                    record.get(
                        "source_ids",
                        [],
                    )
                )

    missing = sorted(
        referenced
        - set(source_map)
    )

    assert not missing, (
        "orphan source references: "
        f"{missing}"
    )

    rendered_sources = set(
        re.findall(
            r'data-source-id="'
            r'(S-\d{2})"',
            page_html,
        )
    )

    unrendered = sorted(
        referenced
        - rendered_sources
    )

    assert not unrendered, (
        "public evidence referenced "
        "but not rendered: "
        f"{unrendered}"
    )

    canonical_states = {
        source["state"]
        for source in sources
    }

    rendered_states = set(
        re.findall(
            r'data-evidence-state="'
            r'([a-z_]+)"',
            page_html,
        )
    )

    for state in baseline[
        "required_rendered_states"
    ]:
        if (
            state
            in canonical_states
        ):
            assert (
                state
                in rendered_states
            ), (
                "rendered evidence "
                "taxonomy lost state: "
                f"{state}"
            )

    for event in data[
        "events"
    ]:
        if event.get(
            "state"
        ) in {
            "official",
            "secondary",
            "reported_draft",
        }:
            assert event.get(
                "source_ids"
            ), (
                "material event "
                "lacks source: "
                f"{event.get('id')}"
            )

    canonical_names = [
        record["name"]
        for record
        in data["signatories"]
        if record.get(
            "status"
        ) == "active"
    ]

    map_names = [
        html_lib.unescape(
            value
        )
        for value in re.findall(
            r'data-map-marker="'
            r'([^"]+)"',
            page_html,
        )
    ]

    roster_names = [
        html_lib.unescape(
            value
        )
        for value in re.findall(
            r'data-roster-country="'
            r'([^"]+)"',
            page_html,
        )
    ]

    assert (
        len(canonical_names)
        == len(set(canonical_names))
    ), (
        "duplicate canonical "
        "active signatory"
    )

    assert (
        len(map_names)
        == len(set(map_names))
    ), (
        "duplicate rendered "
        "map signatory"
    )

    assert (
        len(roster_names)
        == len(set(roster_names))
    ), (
        "duplicate rendered "
        "roster signatory"
    )

    canonical = set(
        canonical_names
    )

    rendered_map = set(
        map_names
    )

    rendered_roster = set(
        roster_names
    )

    assert (
        rendered_map
        == canonical
    ), (
        "map membership differs "
        "from canonical active "
        "signatories: "
        f"missing="
        f"{sorted(canonical-rendered_map)} "
        f"extra="
        f"{sorted(rendered_map-canonical)}"
    )

    assert (
        rendered_roster
        == canonical
    ), (
        "roster membership differs "
        "from canonical active "
        "signatories: "
        f"missing="
        f"{sorted(canonical-rendered_roster)} "
        f"extra="
        f"{sorted(rendered_roster-canonical)}"
    )

    assert (
        len(map_names)
        == len(canonical_names)
    )

    assert (
        len(roster_names)
        == len(canonical_names)
    )

    print(
        "PASS - evidence source ratchet "
        f"({len(sources)} sources)"
    )

    print(
        "PASS - public source coverage "
        f"({len(referenced)} referenced IDs)"
    )

    print(
        "PASS - rendered evidence taxonomy"
    )

    print(
        "PASS - canonical/map/roster identity "
        f"({len(canonical_names)} "
        "active signatories)"
    )


if __name__ == "__main__":
    main()
