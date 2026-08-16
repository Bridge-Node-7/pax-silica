#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--base-url",default="http://127.0.0.1:8765/");ap.add_argument("--evidence",default="build/browser-uat");args=ap.parse_args()
    out=Path(args.evidence);out.mkdir(parents=True,exist_ok=True);results=[]
    with sync_playwright() as p:
        exe=os.environ.get("PAX_SILICA_CHROMIUM");browser=p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        for width,height in [(320,800),(390,844),(768,1024),(1024,900),(1440,1000),(1680,1000)]:
            page=browser.new_page(viewport={"width":width,"height":height},reduced_motion="reduce");page.goto(args.base_url,wait_until="networkidle")
            docw=page.evaluate("document.documentElement.scrollWidth");assert docw<=width,(width,docw);results.append({"test":f"reflow-{width}","pass":True,"observed":docw})
            for sel in (".ladder",".flow"):
                el=page.locator(sel);sw=el.evaluate("e=>e.scrollWidth");cw=el.evaluate("e=>e.clientWidth");assert sw<=cw+1,(width,sel,sw,cw)
            results.append({"test":f"flows-{width}","pass":True});page.screenshot(path=str(out/f"{width}.png"),full_page=True);page.close()
        page=browser.new_page(viewport={"width":1280,"height":900});page.goto(args.base_url,wait_until="networkidle")
        nodes=page.locator("[data-layer]");assert nodes.count()==7
        for i in range(7): nodes.nth(i).click();assert nodes.nth(i).get_attribute("aria-pressed")=="true"
        results.append({"test":"strategic-stack","pass":True})
        filters=page.locator(".filters [data-region]");assert filters.count()==6;filters.filter(has_text="Europe").click();visible=page.locator(".member:not([hidden])").count();assert visible==9;assert page.locator(".member[aria-pressed]").count()==0
        results += [{"test":"regional-filter","pass":True,"europe_visible":visible},{"test":"member-semantics","pass":True}]
        assert page.locator("#ttsTotal").inner_text()=="202";assert page.locator("#ttsModelState").inner_text()=="BASELINE"
        page.locator("#in0").fill("0");assert page.locator("#ttsTotal").inner_text()=="199";assert page.locator("#ttsModelState").inner_text()=="MODIFIED"
        page.locator("#prequalify").click();assert page.locator("#ttsTotal").inner_text()=="109";assert page.locator("#ttsModelState").inner_text()=="PREQUALIFIED"
        page.locator("#resetTTS").click();assert page.locator("#ttsTotal").inner_text()=="202";assert page.locator("#ttsModelState").inner_text()=="BASELINE";results.append({"test":"time-to-switch-state-machine","pass":True})
        groups=page.locator("[data-evidence-group]");assert groups.count()>=3;assert groups.nth(0).get_attribute("data-evidence-group")=="official";assert groups.nth(1).get_attribute("data-evidence-group")=="secondary";assert groups.nth(2).get_attribute("data-evidence-group")=="reported_draft";results.append({"test":"evidence-group-order","pass":True})
        official_ids=page.locator('[data-evidence-group="official"] .evidence-card code').all_inner_texts();assert official_ids[:4]==["S-01","S-05","S-11","S-04"],official_ids;results.append({"test":"evidence-official-order","pass":True})
        s06=page.locator("#source-S-06");assert "Review by" in s06.inner_text();assert "Aug 20, 2026" in s06.inner_text();results.append({"test":"evidence-dates","pass":True})
        source=page.locator('[data-source="S-01"]').first
        drawer=page.locator("#drawer")
        assert drawer.get_attribute("inert") is not None
        assert page.evaluate("""() => { const b=document.querySelector('#drawerClose'); b.focus(); return document.activeElement !== b; }""")
        source.click()
        assert drawer.get_attribute("inert") is None
        assert drawer.get_attribute("role")=="dialog"
        assert drawer.get_attribute("aria-modal")=="true"
        assert drawer.get_attribute("aria-hidden")=="false"
        assert "Verified" in page.locator("#drawerDates").inner_text()
        assert page.locator("#main").get_attribute("inert") is not None
        assert page.locator(".site-nav").get_attribute("inert") is not None
        assert "drawer-open" in (page.locator("body").get_attribute("class") or "")
        assert page.locator("#drawerClose").evaluate("el=>el===document.activeElement")
        page.keyboard.press("Shift+Tab")
        assert page.locator("#drawerLink").evaluate("el=>el===document.activeElement")
        page.keyboard.press("Tab")
        assert page.locator("#drawerClose").evaluate("el=>el===document.activeElement")
        results += [
            {"test":"evidence-drawer-dates","pass":True},
            {"test":"drawer-modal-semantics","pass":True},
            {"test":"drawer-background-inert","pass":True},
            {"test":"drawer-focus-trap","pass":True},
            {"test":"drawer-scroll-lock","pass":True},
        ]
        page.keyboard.press("Escape")
        assert drawer.get_attribute("aria-hidden")=="true"
        assert drawer.get_attribute("inert") is not None
        assert page.locator("#main").get_attribute("inert") is None
        assert "drawer-open" not in (page.locator("body").get_attribute("class") or "")
        assert source.evaluate("el=>el===document.activeElement")
        results.append({"test":"drawer-focus-return","pass":True})
        page2=browser.new_page(viewport={"width":1280,"height":900},reduced_motion="reduce");page2.goto(args.base_url,wait_until="networkidle");page2.keyboard.press("Tab");assert page2.evaluate("document.activeElement && document.activeElement.getAttribute('href')")=="#main";page2.close();results.append({"test":"keyboard-entry","pass":True})
        forced=browser.new_page(viewport={"width":1280,"height":900},forced_colors="active",reduced_motion="reduce")
        forced.goto(args.base_url,wait_until="networkidle")
        assert forced.evaluate("matchMedia('(forced-colors: active)').matches")
        hero_color=forced.locator(".gradient-text").evaluate("el=>getComputedStyle(el).color")
        assert hero_color not in ("rgba(0, 0, 0, 0)","transparent"),hero_color
        assert forced.locator(".gradient-text").is_visible()
        forced.screenshot(path=str(out/"forced-colors.png"),full_page=True)
        forced.close()
        results.append({"test":"forced-colors-resilience","pass":True,"hero_color":hero_color})

        spacing=browser.new_page(viewport={"width":390,"height":844},reduced_motion="reduce")
        spacing.goto(args.base_url,wait_until="networkidle")
        spacing.add_style_tag(content="*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}")
        spacing_width=spacing.evaluate("document.documentElement.scrollWidth")
        assert spacing_width<=390,(spacing_width,390)
        assert spacing.locator("h1").is_visible()
        assert spacing.locator("#evidence").is_visible()
        spacing.screenshot(path=str(out/"text-spacing-390.png"),full_page=True)
        spacing.close()
        results.append({"test":"text-spacing-reflow","pass":True,"observed":spacing_width})
        mobile=browser.new_page(viewport={"width":390,"height":844},reduced_motion="reduce");mobile.goto(args.base_url,wait_until="networkidle")
        cols=mobile.locator(".members").evaluate("el=>getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length")
        assert cols==2,cols
        details=mobile.locator(".evidence-details").first
        assert details.is_visible()
        assert mobile.locator(".evidence-note").first.is_hidden()
        assert mobile.locator(".evidence-supports").first.is_hidden()
        details.click()
        assert mobile.locator("#drawer").get_attribute("inert") is None
        assert mobile.locator("#drawerSupports").inner_text().strip()
        assert mobile.locator("#drawerNote").inner_text().strip()
        mobile.keyboard.press("Escape")
        assert mobile.locator("#drawer").get_attribute("inert") is not None
        results += [{"test":"mobile-network-density","pass":True},{"test":"mobile-evidence-progressive-disclosure","pass":True},{"test":"closed-drawer-inert","pass":True}]
        for selector in (".filters button",".source",".tts button","#drawerClose"):
            loc=mobile.locator(selector)
            for i in range(loc.count()):
                box=loc.nth(i).bounding_box();assert box and box["height"]>=44-0.5,(selector,i,box)
                if selector==".source": assert box["width"]>=44-0.5,(selector,i,box)
        for i in range(mobile.locator(".control input").count()):
            box=mobile.locator(".control input").nth(i).bounding_box();assert box and box["height"]>=44-0.5,("range",i,box)
        mobile.close();results.append({"test":"mobile-touch-targets","pass":True})
        browser.close()
    (out/"results.json").write_text(json.dumps(results,indent=2)+"\n", encoding="utf-8");print(f"PASS - browser UAT {len(results)} checks")
if __name__=="__main__":main()
