import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

VALIDATOR = (
    ROOT
    / "scripts/validate_data.py"
)


class HardeningV027Tests(
    unittest.TestCase
):
    def fixture(
        self,
        directory,
    ):
        root = Path(directory)

        shutil.copytree(
            ROOT / "data",
            root / "data",
        )

        return root

    def set_deadlines(
        self,
        root,
    ):
        data_path = (
            root
            / "data/pax-silica.json"
        )

        source_path = (
            root
            / "data/sources.json"
        )

        data = json.loads(
            data_path.read_text(
                encoding="utf-8"
            )
        )

        source_doc = json.loads(
            source_path.read_text(
                encoding="utf-8"
            )
        )

        for source in source_doc[
            "sources"
        ]:
            if source.get(
                "review_by"
            ):
                source[
                    "review_by"
                ] = "2099-01-01"

        for group in (
            "claims",
            "programs",
        ):
            for record in data[group]:
                if record.get(
                    "review_by"
                ):
                    record[
                        "review_by"
                    ] = "2099-01-01"

        source_map = {
            item["id"]: item
            for item
            in source_doc["sources"]
        }

        claim_map = {
            item["id"]: item
            for item
            in data["claims"]
        }

        program_map = {
            item["id"]: item
            for item
            in data["programs"]
        }

        source_map["S-06"][
            "review_by"
        ] = "2030-01-20"

        claim_map["C-004"][
            "review_by"
        ] = "2030-01-20"

        program_map["P-001"][
            "review_by"
        ] = "2030-01-20"

        source_map["S-09"][
            "review_by"
        ] = "2030-01-22"

        claim_map["C-006"][
            "review_by"
        ] = "2030-01-22"

        data_path.write_text(
            json.dumps(
                data,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        source_path.write_text(
            json.dumps(
                source_doc,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def run_validator(
        self,
        root,
        as_of,
    ):
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--root",
                str(root),
                "--as-of",
                as_of,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_due_soon_warns_without_failure(
        self,
    ):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(d)
            self.set_deadlines(root)

            result = self.run_validator(
                root,
                "2030-01-18",
            )

            output = (
                result.stdout
                + result.stderr
            )

            self.assertEqual(
                result.returncode,
                0,
                output,
            )

            for item in (
                "source S-06",
                "record C-004",
                "record P-001",
            ):
                self.assertIn(
                    "due soon " + item,
                    output,
                )

            self.assertNotIn(
                "due soon source S-09",
                output,
            )

    def test_before_warning_window_is_fresh(
        self,
    ):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(d)
            self.set_deadlines(root)

            result = self.run_validator(
                root,
                "2030-01-16",
            )

            output = (
                result.stdout
                + result.stderr
            )

            self.assertEqual(
                result.returncode,
                0,
                output,
            )

            self.assertNotIn(
                "due soon",
                output,
            )

            self.assertNotIn(
                "stale",
                output.lower(),
            )

    def test_due_today_warns_without_failure(
        self,
    ):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(d)
            self.set_deadlines(root)

            result = self.run_validator(
                root,
                "2030-01-20",
            )

            output = (
                result.stdout
                + result.stderr
            )

            self.assertEqual(
                result.returncode,
                0,
                output,
            )

            for item in (
                "source S-06",
                "record C-004",
                "record P-001",
            ):
                self.assertIn(
                    "due soon " + item,
                    output,
                )

            self.assertIn(
                "(0 day(s) remaining)",
                output,
            )

    def test_all_stale_records_report_together(
        self,
    ):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(d)
            self.set_deadlines(root)

            result = self.run_validator(
                root,
                "2030-01-23",
            )

            output = (
                result.stdout
                + result.stderr
            )

            self.assertNotEqual(
                result.returncode,
                0,
            )

            self.assertIn(
                "freshness failures",
                output,
            )

            for item in (
                "source S-06",
                "source S-09",
                "record C-004",
                "record C-006",
                "record P-001",
            ):
                self.assertIn(
                    item,
                    output,
                )

    def test_active_signatory_floor_allows_growth(
        self,
    ):
        with tempfile.TemporaryDirectory() as d:
            root = self.fixture(d)

            data_path = (
                root
                / "data/pax-silica.json"
            )

            source_path = (
                root
                / "data/sources.json"
            )

            data = json.loads(
                data_path.read_text(
                    encoding="utf-8"
                )
            )

            sources = json.loads(
                source_path.read_text(
                    encoding="utf-8"
                )
            )

            for source in sources[
                "sources"
            ]:
                if source.get(
                    "review_by"
                ):
                    source[
                        "review_by"
                    ] = "2099-01-01"

            for group in (
                "claims",
                "programs",
            ):
                for record in data[group]:
                    if record.get(
                        "review_by"
                    ):
                        record[
                            "review_by"
                        ] = "2099-01-01"

            data["signatories"].append(
                {
                    "name": (
                        "Future Signatory Fixture"
                    ),
                    "region": "Americas",
                    "status": "active",
                    "source_ids": [
                        "S-01"
                    ],
                    "evidence_state": (
                        "official"
                    ),
                }
            )

            data_path.write_text(
                json.dumps(
                    data,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            source_path.write_text(
                json.dumps(
                    sources,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_validator(
                root,
                "2030-01-01",
            )

            self.assertEqual(
                result.returncode,
                0,
                result.stdout
                + result.stderr,
            )

    def test_public_signatory_semantics_and_seer(
        self,
    ):
        template = (
            ROOT
            / "web/index.template.html"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "Declaration signatories "
            "have joined",
            template,
        )

        self.assertIn(
            "Select a signatory",
            template,
        )

        self.assertNotIn(
            "Participating nations "
            "have joined",
            template,
        )

        self.assertNotIn(
            "Select a country "
            "to reveal",
            template,
        )

        self.assertIn(
            "https://bschool."
            "pepperdine.edu/seer/",
            template,
        )

        self.assertIn(
            "Pepperdine SEER",
            template,
        )

        self.assertIn(
            "Entity type",
            template,
        )

        self.assertIn(
            "Signatory</span>",
            template,
        )

        self.assertNotIn(
            ">Participant</span>",
            template,
        )

    def test_visual_css_removes_known_collision_trigger(
        self,
    ):
        css = (
            ROOT
            / "web/styles.css"
        ).read_text(
            encoding="utf-8"
        )

        self.assertNotIn(
            ".global-nav .nav-cta",
            css,
        )

        self.assertNotIn(
            "  .nav-cta{",
            css,
        )

        self.assertIn(
            ".section-head>div"
            "{min-width:0}",
            css,
        )

        self.assertIn(
            "#four-p .section-head h2"
            "{font-size:clamp("
            "42px,4.6vw,72px);"
            "text-wrap:balance}",
            css,
        )

        self.assertNotIn(
            "#four-p .section-head h2"
            "{font-size:clamp("
            "42px,4.6vw,72px);"
            "white-space:nowrap}",
            css,
        )

        self.assertNotIn(
            "#four-p .section-head"
            "{grid-template-columns:",
            css,
        )

        self.assertIn(
            "button{cursor:pointer;"
            "min-width:44px;"
            "min-height:44px}",
            css,
        )

    def test_maintenance_wiring_is_explicit(
        self,
    ):
        workflow = (
            ROOT
            / ".github/workflows/freshness.yml"
        ).read_text(
            encoding="utf-8"
        )

        builder = (
            ROOT
            / "scripts/build_web.py"
        ).read_text(
            encoding="utf-8"
        )

        app = (
            ROOT
            / "web/app.js"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "--warn-days 3 "
            "--github-annotations",
            workflow,
        )

        self.assertNotIn(
            "MAP_POSITIONS",
            builder,
        )

        self.assertIn(
            "web/map-display.json",
            builder,
        )

        self.assertIn(
            "countryEntity",
            app,
        )


if __name__ == "__main__":
    unittest.main()
