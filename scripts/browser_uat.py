#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS = (320, 390, 768, 1024, 1440, 1920)
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
            heading: {left:a.left,right:a.right,top:a.top,bottom:a.bottom},
            intro: {left:b.left,right:b.right,top:b.top,bottom:b.bottom},
          };
        }).filter(Boolean)""",
        minimum_gap,
    )

    assert not violations, (
        "section-header collision(s): "
        + repr(violations)
    )


def exercise_controls(
    page,
    selector,
    output_selector,
):
    controls = page.locator(selector)
    observed = []

    assert controls.count() > 0

    for index in range(
        controls.count()
    ):
        control = controls.nth(index)
        control.scroll_into_view_if_needed()
        control.click()

        assert (
            control.get_attribute(
                "aria-pressed"
            )
            == "true"
        )

        assert page.locator(
            selector
            + '[aria-pressed="true"]'
        ).count() == 1

        value = page.locator(
            output_selector
        ).inner_text().strip()

        assert value
        observed.append(value)

    assert (
        len(observed)
        == len(set(observed))
    ), (
        selector,
        observed,
    )

    return observed

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--evidence", required=True)
    args = ap.parse_args()

    evidence = Path(args.evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    results = []
    expected_signatories = (
        canonical_active_count()
    )

    def record(name, observed):
        results.append({"test": name, "pass": True, "observed": observed})

    with sync_playwright() as p:
        launch_kwargs = {}
        if Path("/usr/bin/chromium").exists():
            launch_kwargs["executable_path"] = "/usr/bin/chromium"
            launch_kwargs["args"] = ["--no-sandbox", "--disable-dev-shm-usage"]
        browser = p.chromium.launch(**launch_kwargs)

        # Responsive reflow contract.
        for width in WIDTHS:
            context = browser.new_context(
                viewport={"width": width, "height": 900},
                reduced_motion="reduce",
            )
            page = context.new_page()
            page.goto(args.base_url, wait_until="networkidle")
            scroll_width = page.evaluate("document.documentElement.scrollWidth")
            assert scroll_width <= width + 1, (width, scroll_width)
            if width in (1024, 1440, 1920):
                assert_section_heads_clear(page)
            record(f"reflow-{width}", {"viewport": width, "scrollWidth": scroll_width})
            context.close()

        record(
            "section-head-geometry",
            {"viewports": [1024, 1440, 1920]},
        )

        context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        page = context.new_page()
        page.goto(args.base_url, wait_until="networkidle")

        hero = page.locator(".hero").inner_text()
        assert "Pax Silica" in hero
        assert "Bridge Node 7 transforms public evidence into intelligence for industrial capability." in hero
        assert "Latest official signal" not in hero
        assert "Verified through" not in hero
        record("hero", {"fakeLiveMetadata": False})

        # Validate semantic navigation labels from textContent. The visual
        # treatment intentionally uses CSS text-transform: uppercase, so
        # innerText is presentation-dependent and is not the right contract.
        nav_links = page.locator(".local-nav a")
        nav = nav_links.evaluate_all("(els)=>els.map(e=>(e.textContent||'').trim())")
        nav_hrefs = nav_links.evaluate_all("(els)=>els.map(e=>e.getAttribute('href'))")
        expected_nav = ["Participants","Technology","Capability","Philippines","Sustainability","Readiness","Resilience","Sources"]
        expected_hrefs = ["#network","#technology","#capability","#philippines","#four-p","#readiness","#switching","#evidence"]
        assert nav == expected_nav, nav
        assert nav_hrefs == expected_hrefs, nav_hrefs

        for index, href in enumerate(
            nav_hrefs
        ):
            link = nav_links.nth(index)
            link.click()
            page.wait_for_timeout(80)

            target = page.locator(href)
            assert target.count() == 1

            assert target.evaluate(
                """(el) => {
                  const r = el.getBoundingClientRect();
                  return r.bottom > 0 && r.top < window.innerHeight;
                }"""
            )

        record("navigation", {"labels": nav, "hrefs": nav_hrefs})

        # Network map and roster.
        marker = page.locator('[data-map-marker="Philippines"]')
        marker.focus()
        page.keyboard.press("Enter")
        assert page.locator("#countryName").inner_text() == "Philippines"
        page.locator('[data-network-view="roster"]').click()
        assert page.locator("#networkRoster").is_visible()
        assert page.locator("[data-roster-country]").count() == expected_signatories
        roster_controls = page.locator(
            "[data-roster-country]"
        )

        roster_names = []

        for index in range(
            roster_controls.count()
        ):
            roster = roster_controls.nth(index)
            name = roster.get_attribute(
                "data-roster-country"
            )

            assert name
            roster.click()

            assert (
                roster.get_attribute(
                    "aria-pressed"
                )
                == "true"
            )

            assert page.locator(
                '[data-roster-country][aria-pressed="true"]'
            ).count() == 1

            assert (
                page.locator(
                    "#countryName"
                ).inner_text()
                == name
            )

            expected_entity = (
                "Institution"
                if name
                == "European Union"
                else "Country"
            )

            assert (
                page.locator(
                    "#countryEntity"
                ).inner_text()
                == expected_entity
            )

            roster_names.append(name)

        assert (
            len(roster_names)
            == expected_signatories
        )

        assert page.locator(
            ".timeline-event"
        ).count() == 6

        assert page.locator(
            ".timeline-evidence"
        ).count() == 6

        record(
            "participants",
            {
                "rosterCount": len(roster_names),
                "entityTypesVerified": True,
                "timelineEvents": 6,
                "rosterVisible": True,
            },
        )

        # Exercise every state that shares the public interaction renderers.
        layers = exercise_controls(
            page,
            ".layer",
            "#layerName",
        )

        actors = exercise_controls(
            page,
            ".actor",
            "#actorName",
        )

        pathways = exercise_controls(
            page,
            ".path-stage",
            "#pathAdds",
        )

        sustainability = exercise_controls(
            page,
            ".p-card",
            "#pName",
        )

        readiness = exercise_controls(
            page,
            ".ready-stage",
            "#readyName",
        )

        assert (
            page.locator(
                ".readiness-current-pill"
            ).inner_text()
            == "Announced"
        )

        record(
            "learning-interactions",
            {
                "technologyStates": len(layers),
                "capabilityStates": len(actors),
                "philippinesStates": len(pathways),
                "sustainabilityStates": len(sustainability),
                "readinessStates": len(readiness),
                "readinessCurrent": "Announced",
            },
        )

        # Supply Resilience is intentionally explanatory, not model theater.
        resilience = page.locator("#switching").inner_text()
        for label in ("Disruption","Replacement","Proof","Usable Supply"):
            assert label in resilience
        assert page.locator("#switching button,#switching input").count() == 0
        assert "202" not in resilience
        record("resilience", {"interactiveControls": 0, "public202Model": False})

        # Evidence taxonomy, every drawer trigger, and focus restoration.
        assert page.locator("#evidence .source-record").count() >= 10
        groups = page.locator("#evidence [data-evidence-group]").evaluate_all(
            "(els)=>els.map(e=>e.getAttribute('data-evidence-group'))"
        )
        assert {"official","secondary","reported_draft"} <= set(groups)
        assert "Reported Development" in page.locator("#evidence").inner_text()

        triggers = page.locator(
            "[data-open-evidence]"
        )

        assert triggers.count() > 0

        trigger_ids = []

        for index in range(
            triggers.count()
        ):
            trigger = triggers.nth(index)
            source_id = (
                trigger.get_attribute(
                    "data-open-evidence"
                )
            )

            assert source_id
            trigger_ids.append(source_id)

            trigger.scroll_into_view_if_needed()
            trigger.click()

            assert page.locator(
                "#evidenceDrawer"
            ).get_attribute(
                "aria-hidden"
            ) == "false"

            assert page.locator(
                "#drawerRecord"
            ).inner_text() == source_id

            page.keyboard.press("Escape")

            assert page.locator(
                "#evidenceDrawer"
            ).get_attribute(
                "aria-hidden"
            ) == "true"

            assert trigger.evaluate(
                "(el)=>document.activeElement===el"
            )

        record(
            "evidence",
            {
                "groups": groups,
                "drawerTriggers": len(trigger_ids),
                "focusRestored": True,
            },
        )

        disclosures = page.locator(
            "details.credibility-note"
        )

        assert disclosures.count() >= 3

        for index in range(
            disclosures.count()
        ):
            detail = disclosures.nth(index)
            summary = detail.locator(
                "summary"
            )

            summary.click()

            assert (
                detail.get_attribute(
                    "open"
                )
                is not None
            )

            summary.click()

            assert (
                detail.get_attribute(
                    "open"
                )
                is None
            )

        record(
            "disclosures",
            {
                "count": disclosures.count(),
            },
        )

        # Closing balance.
        cards = page.locator(".bn7-links-equal > a")
        assert cards.count() == 3
        boxes = [cards.nth(i).bounding_box() for i in range(3)]
        tops = [round(x["y"], 1) for x in boxes]
        heights = [round(x["height"], 1) for x in boxes]
        assert max(tops) - min(tops) < 2
        assert max(heights) - min(heights) < 2
        record("closing", {"tops": tops, "heights": heights})

        # Spoken/public language contract.
        visible = page.locator("body").inner_text()
        assert not re.search(r"\b(?:you|your|yours|yourself|yourselves)\b", visible, re.I)
        assert "—" not in visible
        record("language", {"secondPerson": 0, "emDash": 0})

        # Active navigation should expose location semantics.
        page.locator("#four-p").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        current = page.locator('.local-nav a[aria-current="location"]').all_inner_texts()
        assert current
        record("aria-current", {"current": current})

        page.screenshot(path=str(evidence / "desktop-full.png"), full_page=True)

        # Mobile contract: roster first, no overflow.
        mobile = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        mpage = mobile.new_page()
        mpage.goto(args.base_url, wait_until="networkidle")
        assert mpage.evaluate("document.documentElement.scrollWidth") <= 391
        assert mpage.locator("#networkMap").is_hidden()
        assert mpage.locator("#networkRoster").is_visible()
        assert mpage.locator("[data-roster-country]").count() == expected_signatories
        assert mpage.locator(".partner-cta").is_visible()

        target_selector = ",".join(
            (
                ".partner-cta",
                ".enter",
                ".local-nav a",
                "[data-network-view]",
                "[data-roster-country]",
                ".layer",
                ".actor",
                ".path-stage",
                ".p-card",
                ".ready-stage",
                ".timeline-evidence",
                ".source-record-actions a",
                "details.credibility-note summary",
                ".credibility-note .text-button",
                ".bn7-links-equal>a",
            )
        )

        targets = mpage.locator(
            target_selector
        )

        checked_targets = []

        for index in range(
            targets.count()
        ):
            target = targets.nth(index)

            if not target.is_visible():
                continue

            box = target.bounding_box()

            assert box is not None
            assert box["width"] >= 43.5, (
                target.evaluate(
                    "(el)=>el.outerHTML"
                ),
                box,
            )
            assert box["height"] >= 43.5, (
                target.evaluate(
                    "(el)=>el.outerHTML"
                ),
                box,
            )

            checked_targets.append(
                target.evaluate(
                    "(el)=>el.tagName + ':' + "
                    "(el.textContent || '').trim().slice(0,40)"
                )
            )

        assert checked_targets

        mobile_drawer_triggers = mpage.locator(
            "[data-open-evidence]"
        )

        drawer_trigger = None

        for index in range(
            mobile_drawer_triggers.count()
        ):
            candidate = mobile_drawer_triggers.nth(index)

            if candidate.is_visible():
                drawer_trigger = candidate
                break

        assert drawer_trigger is not None, (
            "no visible mobile evidence trigger available"
        )

        drawer_source_id = drawer_trigger.get_attribute(
            "data-open-evidence"
        )

        assert drawer_source_id

        drawer_trigger.scroll_into_view_if_needed()
        drawer_trigger.click()

        assert mpage.locator(
            "#evidenceDrawer"
        ).get_attribute(
            "aria-hidden"
        ) == "false"

        assert mpage.locator(
            "#drawerRecord"
        ).inner_text() == drawer_source_id

        for selector in (
            "#drawerClose",
            "#drawerLink",
        ):
            box = mpage.locator(
                selector
            ).bounding_box()

            assert box is not None
            assert box["width"] >= 43.5, (
                selector,
                box,
            )
            assert box["height"] >= 43.5, (
                selector,
                box,
            )

        mpage.keyboard.press("Escape")

        mpage.screenshot(path=str(evidence / "mobile-full.png"), full_page=True)
        record(
            "mobile",
            {
                "mapHidden": True,
                "rosterVisible": True,
                "rosterCount": expected_signatories,
                "targetFloor": 44,
                "targetsChecked": len(checked_targets) + 2,
            },
        )
        mobile.close()

        # JavaScript disabled: public record still exists.
        nojs = browser.new_context(viewport={"width": 1024, "height": 900}, java_script_enabled=False)
        npage = nojs.new_page()
        npage.goto(args.base_url, wait_until="domcontentloaded")
        assert npage.locator(".noscript-fallback").is_visible()
        assert npage.locator("#networkRoster").is_visible()
        assert npage.locator("[data-roster-country]").count() == expected_signatories
        assert npage.locator("#evidence .source-record-actions a").count() >= 10
        record("javascript-disabled", {"fallbackVisible": True})
        nojs.close()

        # Forced colors.
        fc = browser.new_context(viewport={"width": 1024, "height": 900}, forced_colors="active")
        fpage = fc.new_page()
        fpage.goto(args.base_url, wait_until="networkidle")
        assert fpage.locator("#hero-title").is_visible()
        assert fpage.locator(".local-nav").is_visible()
        record("forced-colors-resilience", {"heroVisible": True, "navVisible": True})
        fc.close()

        # WCAG text-spacing stress with CSP bypass confined to the test context.
        spacing = browser.new_context(viewport={"width": 390, "height": 844}, bypass_csp=True)
        spage = spacing.new_page()
        spage.goto(args.base_url, wait_until="networkidle")
        spage.add_style_tag(content="*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}")
        assert spage.evaluate("document.documentElement.scrollWidth") <= 391
        record("text-spacing-reflow", {"scrollWidth": spage.evaluate("document.documentElement.scrollWidth")})
        spacing.close()

        context.close()
        browser.close()

    (evidence / "browser-uat.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    assert all(r["observed"] is not None for r in results)
    print(f"PASS - Browser UAT ({len(results)} checks)")


if __name__ == "__main__":
    main()
