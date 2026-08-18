#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_STATES = {
    "official",
    "secondary",
    "reported_draft",
    "bn7_analysis",
    "unknown",
    "superseded",
}

ALLOWED_WORKFLOW = {
    "candidate",
    "reviewed",
    "approved",
    "published",
    "retired",
}

OFFICIAL_HOSTS = {
    "www.state.gov",
    "state.gov",
    "www.whitehouse.gov",
    "whitehouse.gov",
    "simpler.grants.gov",
    "www.comune.brindisi.it",
    "comune.brindisi.it",
}

SECONDARY_HOSTS = {
    "reuters.com",
    "www.reuters.com",
}

REPORTED_HOSTS = {
    "reuters.com",
    "www.reuters.com",
}


def iso(value: str) -> date:
    try:
        return date.fromisoformat(
            value
        )
    except Exception as exc:
        raise AssertionError(
            f"invalid ISO date: {value}"
        ) from exc


def utc_today() -> date:
    return datetime.now(
        timezone.utc
    ).date()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--as-of",
        default=None,
        help=(
            "Validation date in YYYY-MM-DD. "
            "Defaults to current UTC date."
        ),
    )

    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root. Defaults to the current repository.",
    )

    parser.add_argument(
        "--warn-days",
        "--warning-days",
        dest="warning_days",
        type=int,
        default=3,
        help=(
            "Emit a non-failing due-soon warning when a review deadline "
            "is within this many days."
        ),
    )

    parser.add_argument(
        "--github-annotations",
        action="store_true",
        help="Emit GitHub Actions warning annotations for due-soon records.",
    )

    return parser.parse_args()


def validate(
    as_of: date,
    root: Path = ROOT,
    warning_days: int = 3,
    github_annotations: bool = False,
) -> None:
    if warning_days < 0:
        raise AssertionError("warning_days must be non-negative")
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

    freshness_errors: list[str] = []
    freshness_warnings: list[str] = []

    def check_review_deadline(
        kind: str,
        identifier: str,
        review_by: date,
    ) -> None:
        days_remaining = (
            review_by
            - as_of
        ).days

        if days_remaining < 0:
            freshness_errors.append(
                f"stale {kind} {identifier}: "
                f"review_by {review_by.isoformat()} "
                f"< as_of {as_of.isoformat()}"
            )
            return

        if days_remaining <= warning_days:
            freshness_warnings.append(
                f"due soon {kind} {identifier}: "
                f"review_by {review_by.isoformat()} "
                f"({days_remaining} day(s) remaining)"
            )

    ids = [
        source["id"]
        for source in sources
    ]

    assert (
        len(ids)
        == len(set(ids))
    ), "duplicate source ID"

    source_map = {
        source["id"]: source
        for source in sources
    }

    snapshot = iso(
        data["snapshot"][
            "verified_through"
        ]
    )

    for source in sources:
        sid = source["id"]

        assert (
            source["state"]
            in ALLOWED_STATES
        )

        assert source["url"].startswith(
            "https://"
        ), f"non-HTTPS source {sid}"

        host = (
            urlsplit(
                source["url"]
            ).hostname
            or ""
        ).lower()

        if source["state"] == "official":
            assert (
                host in OFFICIAL_HOSTS
            ), (
                "official source on "
                f"unapproved host: "
                f"{sid} {host}"
            )

        if source["state"] == "secondary":
            assert (
                host in SECONDARY_HOSTS
            ), (
                "secondary source on "
                f"unapproved host: "
                f"{sid} {host}"
            )

        if (
            source["state"]
            == "reported_draft"
        ):
            assert (
                host in REPORTED_HOSTS
            ), (
                "reported/draft source "
                "on unapproved host: "
                f"{sid} {host}"
            )

        verified_at = iso(
            source["verified_at"]
        )

        if source.get("published"):
            assert (
                verified_at
                >= iso(source["published"])
            ), (
                "verified before "
                f"publication: {sid}"
            )

        if source.get("review_by"):
            review_by = iso(
                source["review_by"]
            )

            assert (
                review_by >= snapshot
            ), (
                "source review deadline "
                "predates snapshot: "
                f"{sid}"
            )

            check_review_deadline(
                "source",
                sid,
                review_by,
            )

    for group in (
        "signatories",
        "claims",
        "events",
        "programs",
    ):
        for record in data[group]:
            for sid in record.get(
                "source_ids",
                [],
            ):
                assert (
                    sid in source_map
                ), (
                    f"orphan source {sid} "
                    f"in {group}"
                )

            if (
                record.get("state")
                and
                group != "signatories"
            ):
                assert (
                    record["state"]
                    in ALLOWED_STATES
                )

            if record.get(
                "workflow_state"
            ):
                assert (
                    record[
                        "workflow_state"
                    ]
                    in ALLOWED_WORKFLOW
                )

            for key in (
                "date",
                "verified_at",
                "review_by",
                "joined",
                "close_date",
            ):
                if record.get(key):
                    iso(record[key])

            if record.get(
                "review_by"
            ):
                review_by = iso(
                    record["review_by"]
                )

                assert (
                    review_by >= snapshot
                ), (
                    "record review deadline "
                    "predates snapshot: "
                    f"{record.get('id')}"
                )

                check_review_deadline(
                    "record",
                    str(record.get("id")),
                    review_by,
                )

    def source_states(record):
        return {
            source_map[sid]["state"]
            for sid in record.get(
                "source_ids",
                [],
            )
        }

    for claim in data["claims"]:
        states = source_states(
            claim
        )

        if (
            claim["state"]
            == "official"
        ):
            assert "official" in states, (
                "official claim lacks "
                "official source: "
                f"{claim['id']}"
            )

        if (
            claim["state"]
            == "reported_draft"
        ):
            assert (
                "reported_draft"
                in states
            )

    for event in data["events"]:
        states = source_states(
            event
        )

        if (
            event["state"]
            == "official"
        ):
            assert "official" in states, (
                "official event lacks "
                "official source: "
                f"{event['id']}"
            )

        if (
            event["state"]
            == "reported_draft"
        ):
            assert (
                "reported_draft"
                in states
            )

    for program in data["programs"]:
        assert (
            "official"
            in source_states(program)
        ), (
            "program lacks "
            "official source: "
            f"{program['id']}"
        )

    for signatory in data[
        "signatories"
    ]:
        evidence_state = (
            signatory.get(
                "evidence_state"
            )
        )

        assert evidence_state in {
            "official",
            "secondary",
        }, (
            "signatory "
            "evidence_state missing: "
            f"{signatory['name']}"
        )

        states = source_states(
            signatory
        )

        if (
            evidence_state
            == "official"
        ):
            assert (
                "official" in states
            )

        if (
            evidence_state
            == "secondary"
        ):
            assert (
                "secondary" in states
            )

    active = [
        signatory
        for signatory
        in data["signatories"]
        if signatory.get(
            "status"
        ) == "active"
    ]

    active_names = [
        signatory["name"]
        for signatory in active
    ]

    minimum_active = int(
        baseline[
            "minimum_active_signatory_count"
        ]
    )

    assert (
        len(active)
        >= minimum_active
    ), (
        "active signatory count "
        "fell below evidence baseline: "
        f"{len(active)} < "
        f"{minimum_active}"
    )

    assert (
        len(active_names)
        == len(set(active_names))
    ), (
        "duplicate active "
        "signatory name"
    )

    assert sum(
        bool(
            signatory.get(
                "founding"
            )
        )
        for signatory in active
    ) == 7, (
        "expected 7 founders"
    )

    for warning in freshness_warnings:
        if (
            github_annotations
            or
            os.getenv("GITHUB_ACTIONS")
            == "true"
        ):
            print(
                "::warning "
                "title=Pax Silica freshness::"
                + warning
            )
        else:
            print(
                "WARN - "
                + warning
            )

    if freshness_errors:
        raise AssertionError(
            "freshness failures:\n- "
            + "\n- ".join(
                freshness_errors
            )
        )

    print(
        "PASS - data integrity"
    )

    print(
        "PASS - freshness as of "
        + as_of.isoformat()
    )

    print(
        "PASS - source credibility"
    )


def main() -> None:
    args = parse_args()

    as_of = (
        iso(args.as_of)
        if args.as_of
        else utc_today()
    )

    validate(
        as_of,
        root=Path(args.root).resolve(),
        warning_days=args.warning_days,
        github_annotations=args.github_annotations,
    )


if __name__ == "__main__":
    main()
