import json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReleasePolishTests(unittest.TestCase):
    def build(self,out): subprocess.check_call([sys.executable,str(ROOT/"scripts/build_web.py"),"--output",out],cwd=ROOT,stdout=subprocess.DEVNULL)
    def test_lean_repository(self):
        for rel in ('CODE_OF_CONDUCT.md','CONTRIBUTING.md','.github/CODEOWNERS','CITATION.cff','RIGHTS.md','docs/GENESIS_VALIDATION.md'):
            self.assertFalse((ROOT/rel).exists(),rel)
    def test_evidence_has_dates_and_group_order(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d);text=(Path(d)/'index.html').read_text(encoding="utf-8")
            self.assertIn('PRIMARY / OFFICIAL',text);self.assertIn('SECONDARY',text);self.assertIn('REPORTED / DRAFT',text)
            self.assertIn('<b>Published</b>',text);self.assertIn('<b>Verified</b>',text);self.assertIn('<b>Review by</b>',text)
            pos=[text.index(f'id="source-{x}"') for x in ('S-01','S-05','S-11','S-04')]
            self.assertEqual(pos,sorted(pos))
    def test_flow_has_no_forced_horizontal_overflow_contract(self):
        css=(ROOT/'web/styles.css').read_text(encoding="utf-8")
        self.assertIn('.ladder{grid-template-columns:repeat(8,minmax(0,1fr))}',css)
        self.assertIn('.flow{grid-template-columns:repeat(7,minmax(0,1fr))}',css)
        self.assertNotIn('.ladder,.flow{display:grid;grid-template-columns:repeat(8,minmax(120px,1fr));gap:7px;overflow:auto',css)
    def test_tts_states_are_explicit(self):
        tpl=(ROOT/'web/index.template.html').read_text(encoding="utf-8");js=(ROOT/'web/app.js').read_text(encoding="utf-8")
        self.assertIn('id="ttsModelState">BASELINE',tpl)
        for state in ('BASELINE','MODIFIED','PREQUALIFIED'): self.assertIn(state,js)
    def test_spoken_audit_is_in_gate(self):
        gate=(ROOT/'scripts/check_repo.py').read_text(encoding="utf-8");self.assertIn('audit_readability.py',gate)

    def test_luxury_text_selection_and_philippines_scale(self):
        css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
        self.assertIn("::selection{background:rgba(241,200,107,.28);color:var(--ink)}",css)
        self.assertIn("#philippines .lead{font-size:clamp(18px,1.7vw,24px);max-width:920px}",css)
        self.assertIn("#philippines .split header h2{font-size:clamp(38px,4.4vw,58px)}",css)


    def test_github_actions_are_sha_pinned(self):
        import re
        for path in (ROOT/".github/workflows").glob("*.yml"):
            text=path.read_text(encoding="utf-8")
            refs=re.findall(r"uses:\s*([^\s#]+)",text)
            for ref in refs:
                self.assertRegex(ref,r"@[0-9a-f]{40}$",msg=f"unpinned action in {path}: {ref}")


    def test_mobile_touch_target_contract(self):
        css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
        self.assertIn("min-height:44px",css)
        self.assertIn("min-width:44px",css)

    def test_readme_front_door_closeout_contract(self):
        text=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertIn("**Explore:**",text)
        self.assertIn("[Public data](data/)",text)
        self.assertIn("[Credibility](docs/CREDIBILITY.md)",text)
        self.assertIn("Source correction",text)
        self.assertIn("Time-sensitive facts include review dates.",text)
        self.assertIn("## Related public work",text)

    def test_issue_intake_is_correction_only(self):
        config=(ROOT/".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
        self.assertEqual(config.strip(),"blank_issues_enabled: false")
        form=(ROOT/".github/ISSUE_TEMPLATE/public-source-correction.yml").read_text(encoding="utf-8")
        self.assertIn('labels: ["source-correction"]',form)

    def test_browser_uat_has_stable_required_check(self):
        text=(ROOT/".github/workflows/browser-uat.yml").read_text(encoding="utf-8")
        self.assertIn("  pull_request:\n",text)
        self.assertNotIn("  pull_request:\n    paths:",text)
        self.assertIn("name: Browser UAT required",text)
        self.assertIn("needs: chromium",text)

    def test_codeql_checkout_does_not_persist_credentials(self):
        text=(ROOT/".github/workflows/codeql.yml").read_text(encoding="utf-8")
        self.assertIn("persist-credentials: false",text)

    def test_public_boundary_has_public_surface_policy(self):
        text=(ROOT/"scripts/check_public_boundary.py").read_text(encoding="utf-8")
        self.assertIn("PUBLIC_SURFACE",text)
        self.assertIn("NONPUBLIC_DISCLOSURE_PATTERNS",text)

    def test_accessibility_resilience_closeout_contract(self):
        css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
        uat=(ROOT/"scripts/browser_uat.py").read_text(encoding="utf-8")

        self.assertIn(
            "scrollbar-gutter:stable",
            css,
        )

        self.assertIn(
            ".gradient-text{background:none;color:CanvasText;"
            "-webkit-text-fill-color:CanvasText}",
            css,
        )

        self.assertIn(
            'forced_colors="active"',
            uat,
        )

        self.assertIn(
            "forced-colors-resilience",
            uat,
        )

        self.assertIn(
            "text-spacing-reflow",
            uat,
        )

        self.assertIn(
            "bypass_csp=True",
            uat,
        )

if __name__=='__main__':unittest.main()
