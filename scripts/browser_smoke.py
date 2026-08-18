#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import (
    sync_playwright,
)

ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def canonical_active_count():
    data = json.loads(
        (
            ROOT
            / "data/pax-silica.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    return sum(
        record.get("status")
        == "active"
        for record
        in data["signatories"]
    )


def assert_section_heads_clear(
    page,
    minimum_gap=20,
):
    violations = page.locator(
        ".section-head"
    ).evaluate_all(
        """(heads, gap) => heads.map((head, index) => {
          const title = head.querySelector("h2");
          const intro = head.querySelector(":scope > .section-intro");
          if (!title || !intro) return null;
          const a = title.getBoundingClientRect();
          const b = intro.getBoundingClientRect();
          const horizontal =
            a.right + gap <= b.left ||
            b.right + gap <= a.left;
          const vertical =
            a.bottom + gap <= b.top ||
            b.bottom + gap <= a.top;
          if (horizontal || vertical) return null;
          return {
            index,
            title: (title.textContent || "").trim(),
          };
        }).filter(Boolean)""",
        minimum_gap,
    )

    assert not violations, (
        "section-header collision(s): "
        + repr(violations)
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--browser",
        required=True,
        choices=(
            "firefox",
            "webkit",
        ),
    )

    parser.add_argument(
        "--base-url",
        required=True,
    )

    parser.add_argument(
        "--evidence",
        required=True,
    )

    args = parser.parse_args()

    evidence = Path(
        args.evidence
    )

    evidence.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []
    expected_signatories = (
        canonical_active_count()
    )

    def record(
        name,
        observed,
    ):
        results.append(
            {
                "test": name,
                "pass": True,
                "observed": observed,
            }
        )

    with sync_playwright() as playwright:
        browser_type = getattr(
            playwright,
            args.browser,
        )

        browser = (
            browser_type.launch()
        )

        for width in (
            390,
            1440,
        ):
            context = (
                browser.new_context(
                    viewport={
                        "width": width,
                        "height": 900,
                    },
                    reduced_motion="reduce",
                )
            )

            page = (
                context.new_page()
            )

            page.goto(
                args.base_url,
                wait_until="networkidle",
            )

            scroll_width = (
                page.evaluate(
                    "document.documentElement"
                    ".scrollWidth"
                )
            )

            assert (
                scroll_width
                <= width + 1
            )

            assert page.locator(
                "#hero-title"
            ).is_visible()

            if width == 1440:
                assert_section_heads_clear(page)

            if width == 390:
                assert page.locator(
                    ".partner-cta"
                ).is_visible()

                assert page.locator(
                    "#networkMap"
                ).is_hidden()

                assert page.locator(
                    "#networkRoster"
                ).is_visible()

            record(
                f"reflow-{width}",
                {
                    "viewport": width,
                    "scrollWidth": scroll_width,
                },
            )

            context.close()

        context = (
            browser.new_context(
                viewport={
                    "width": 1440,
                    "height": 900,
                },
                reduced_motion="reduce",
            )
        )

        page = (
            context.new_page()
        )

        page.goto(
            args.base_url,
            wait_until="networkidle",
        )

        nav = page.locator(
            ".local-nav a"
        ).evaluate_all(
            "(els)=>els.map("
            "e=>(e.textContent||'').trim())"
        )

        assert nav == [
            "Participants",
            "Technology",
            "Capability",
            "Philippines",
            "Sustainability",
            "Readiness",
            "Resilience",
            "Sources",
        ]

        page.locator(
            '[data-network-view="roster"]'
        ).click()

        assert page.locator(
            "#networkRoster"
        ).is_visible()

        assert page.locator(
            "[data-roster-country]"
        ).count() == expected_signatories

        roster = page.locator(
            '[data-roster-country="Philippines"]'
        )

        roster.click()

        assert (
            roster.get_attribute(
                "aria-pressed"
            )
            == "true"
        )

        assert (
            "selected"
            in (
                roster.get_attribute(
                    "class"
                )
                or ""
            )
        )

        assert page.locator(
            "#countryName"
        ).inner_text() == "Philippines"

        page.locator(
            '[data-open-evidence="S-03"]'
        ).first.click()

        assert page.locator(
            "#evidenceDrawer"
        ).get_attribute(
            "aria-hidden"
        ) == "false"

        page.keyboard.press(
            "Escape"
        )

        assert page.locator(
            "#evidenceDrawer"
        ).get_attribute(
            "aria-hidden"
        ) == "true"

        record(
            "core-interactions",
            {
                "nav": nav,
                "rosterCount": expected_signatories,
                "selected": "Philippines",
                "evidenceDrawer": True,
            },
        )

        page.screenshot(
            path=str(
                evidence
                / (
                    f"{args.browser}"
                    "-smoke.png"
                )
            ),
            full_page=True,
        )

        context.close()

        nojs = (
            browser.new_context(
                viewport={
                    "width": 1024,
                    "height": 900,
                },
                java_script_enabled=False,
            )
        )

        npage = (
            nojs.new_page()
        )

        npage.goto(
            args.base_url,
            wait_until="load",
        )

        npage.locator(
            "#hero-title"
        ).wait_for(
            state="visible",
            timeout=5000,
        )

        assert npage.locator(
            "#hero-title"
        ).is_visible()

        assert npage.locator(
            ".local-nav"
        ).is_visible()

        assert npage.locator(
            "#networkRoster"
        ).is_visible()

        assert npage.locator(
            "[data-roster-country]"
        ).count() == expected_signatories

        assert npage.locator(
            "#evidence .source-record-actions a"
        ).count() >= 10

        record(
            "no-js",
            {
                "heroVisible": True,
                "navigationVisible": True,
                "rosterVisible": True,
                "rosterCount": expected_signatories,
                "evidenceLinksAvailable": True,
            },
        )

        nojs.close()
        browser.close()

    (
        evidence
        / "browser-smoke.json"
    ).write_text(
        json.dumps(
            results,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    assert all(
        result["observed"]
        is not None
        for result in results
    )

    print(
        f"PASS - {args.browser} "
        "smoke UAT "
        f"({len(results)} checks)"
    )


if __name__ == "__main__":
    main()
