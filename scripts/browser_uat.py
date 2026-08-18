#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS = (320, 390, 768, 1024, 1440, 1920)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--evidence", required=True)
    args = ap.parse_args()

    evidence = Path(args.evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    results = []

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
            record(f"reflow-{width}", {"viewport": width, "scrollWidth": scroll_width})
            context.close()

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
        record("navigation", {"labels": nav, "hrefs": nav_hrefs})

        # Network map and roster.
        marker = page.locator('[data-map-marker="Philippines"]')
        marker.focus()
        page.keyboard.press("Enter")
        assert page.locator("#countryName").inner_text() == "Philippines"
        page.locator('[data-network-view="roster"]').click()
        assert page.locator("#networkRoster").is_visible()
        assert page.locator("[data-roster-country]").count() == 25
        roster_ph = page.locator('[data-roster-country="Philippines"]')
        roster_ph.click()
        assert roster_ph.get_attribute("aria-pressed") == "true"
        assert "selected" in (roster_ph.get_attribute("class") or "")
        assert page.locator("#countryName").inner_text() == "Philippines"
        assert page.locator(".timeline-event").count() == 6
        assert page.locator(".timeline-evidence").count() == 6
        record("participants", {"country": "Philippines", "timelineEvents": 6, "rosterVisible": True})

        # Core learning interactions.
        page.locator('[data-layer="semiconductors"]').click()
        assert page.locator("#layerName").inner_text() == "Semiconductors"
        page.locator('[data-actor="research"]').click()
        assert page.locator("#actorName").inner_text() == "Research & Qualification"
        page.locator('[data-stage="engineering"]').click()
        assert page.locator('[data-stage="engineering"]').get_attribute("aria-pressed") == "true"
        page.locator('[data-p="profits"]').click()
        assert page.locator("#pName").inner_text() == "Profits"
        page.locator('[data-ready="operating"]').click()
        assert page.locator("#readyName").inner_text() == "Operating"
        assert page.locator(".readiness-current-pill").inner_text() == "Announced"
        record("learning-interactions", {
            "technology": "Semiconductors",
            "capability": "Research & Qualification",
            "philippines": "Engineering",
            "sustainability": "Profits",
            "readinessExplored": "Operating",
            "readinessCurrent": "Announced",
        })

        # Supply Resilience is intentionally explanatory, not model theater.
        resilience = page.locator("#switching").inner_text()
        for label in ("Disruption","Replacement","Proof","Usable Supply"):
            assert label in resilience
        assert page.locator("#switching button,#switching input").count() == 0
        assert "202" not in resilience
        record("resilience", {"interactiveControls": 0, "public202Model": False})

        # Evidence taxonomy and drawer.
        assert page.locator("#evidence .source-record").count() >= 10
        groups = page.locator("#evidence [data-evidence-group]").evaluate_all(
            "(els)=>els.map(e=>e.getAttribute('data-evidence-group'))"
        )
        assert {"official","secondary","reported_draft"} <= set(groups)
        assert "Reported Development" in page.locator("#evidence").inner_text()
        page.locator('[data-open-evidence="S-03"]').first.click()
        assert page.locator("#evidenceDrawer").get_attribute("aria-hidden") == "false"
        assert page.locator("#drawerRecord").inner_text() == "S-03"
        page.keyboard.press("Escape")
        assert page.locator("#evidenceDrawer").get_attribute("aria-hidden") == "true"
        record("evidence", {"groups": groups, "drawerRecord": "S-03"})

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
        assert mpage.locator(".partner-cta").is_visible()
        mpage.screenshot(path=str(evidence / "mobile-full.png"), full_page=True)
        record("mobile", {"mapHidden": True, "rosterVisible": True})
        mobile.close()

        # JavaScript disabled: public record still exists.
        nojs = browser.new_context(viewport={"width": 1024, "height": 900}, java_script_enabled=False)
        npage = nojs.new_page()
        npage.goto(args.base_url, wait_until="domcontentloaded")
        assert npage.locator(".noscript-fallback").is_visible()
        assert npage.locator("#networkRoster").is_visible()
        assert npage.locator("[data-roster-country]").count() == 25
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
