import importlib.util
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


def load_module(
    name,
    relative,
):
    spec = (
        importlib.util
        .spec_from_file_location(
            name,
            ROOT / relative,
        )
    )

    module = (
        importlib.util
        .module_from_spec(spec)
    )

    spec.loader.exec_module(
        module
    )

    return module


class HardeningV026Tests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.readability = (
            load_module(
                "audit_readability_v026",
                "scripts/"
                "audit_readability.py",
            )
        )

        cls.boundary = (
            load_module(
                "public_boundary_v026",
                "scripts/"
                "check_public_boundary.py",
            )
        )

    def test_second_person_is_rejected(self):
        html = (
            "<h2>Good Heading</h2>"
            "<p>This helps "
            + "you"
            + " understand.</p>"
        )

        with self.assertRaises(
            SystemExit
        ):
            self.readability.audit_html(
                html
            )

    def test_long_heading_is_rejected(self):
        html = (
            "<h2>"
            "One Two Three Four "
            "Five Six Seven"
            "</h2>"
        )

        with self.assertRaises(
            SystemExit
        ):
            self.readability.audit_html(
                html
            )

    def test_long_sentence_is_rejected(self):
        sentence = (
            " ".join(
                ["word"] * 39
            )
            + "."
        )

        html = (
            "<h2>Good Heading</h2>"
            "<p>"
            + sentence
            + "</p>"
        )

        with self.assertRaises(
            SystemExit
        ):
            self.readability.audit_html(
                html
            )

    def test_public_boundary_path_contract(self):
        slash = chr(92)

        ordinary = (
            "C:"
            + slash
            + "Users"
            + slash
            + "Lucky"
            + slash
            + "file.txt"
        )

        serialized = (
            "C:"
            + slash * 2
            + "Users"
            + slash * 2
            + "Lucky"
            + slash * 2
            + "file.txt"
        )

        unix_home = (
            "/"
            + "home"
            + "/Lucky/"
            + "file.txt"
        )

        benign = (
            "The C: drive "
            "contains project files."
        )

        self.assertIn(
            "Windows user path",
            self.boundary.secret_labels(
                ordinary
            ),
        )

        self.assertIn(
            "Windows user path",
            self.boundary.secret_labels(
                serialized
            ),
        )

        self.assertIn(
            "home path",
            self.boundary.secret_labels(
                unix_home
            ),
        )

        self.assertNotIn(
            "Windows user path",
            self.boundary.secret_labels(
                benign
            ),
        )

    def test_roster_mutation_fails_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            build = (
                Path(directory)
                / "build"
            )

            subprocess.check_call(
                [
                    sys.executable,
                    str(
                        ROOT
                        / "scripts/"
                        "build_web.py"
                    ),
                    "--output",
                    str(build),
                ],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
            )

            html_path = (
                build
                / "index.html"
            )

            page = (
                html_path
                .read_text(
                    encoding="utf-8"
                )
            )

            marker = (
                'data-roster-country="'
                'Argentina"'
            )

            self.assertIn(
                marker,
                page,
            )

            mutated = page.replace(
                marker,
                'data-roster-country="'
                'Argentina MUTATED"',
                1,
            )

            mutation = (
                Path(directory)
                / "mutated.html"
            )

            mutation.write_text(
                mutated,
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(
                        ROOT
                        / "scripts/"
                        "check_evidence_integrity.py"
                    ),
                    "--root",
                    str(ROOT),
                    "--build-html",
                    str(mutation),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(
                result.returncode,
                0,
            )

            self.assertIn(
                "roster",
                (
                    result.stdout
                    + result.stderr
                ).lower(),
            )


if __name__ == "__main__":
    unittest.main()
