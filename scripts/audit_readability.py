#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECOND_PERSON_RE = re.compile(
    r"\b(?:you|your|yours|yourself|yourselves)\b",
    re.I,
)

WORD_RE = re.compile(
    r"\b[\w’'-]+\b"
)

SENTENCE_SPLIT_RE = re.compile(
    r"(?<=[.!?])\s+"
)


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.paras = []
        self.h2 = []
        self.stack = []

    def handle_starttag(
        self,
        tag,
        attrs,
    ):
        if tag in {
            "script",
            "style",
        }:
            self.skip += 1

        self.stack.append(tag)

    def handle_endtag(
        self,
        tag,
    ):
        if (
            tag in {
                "script",
                "style",
            }
            and self.skip
        ):
            self.skip -= 1

        if self.stack:
            self.stack.pop()

    def handle_data(
        self,
        data,
    ):
        if self.skip:
            return

        text = " ".join(
            data.split()
        )

        if not text:
            return

        if (
            self.stack
            and
            self.stack[-1]
            == "h2"
        ):
            self.h2.append(
                text
            )

        if (
            self.stack
            and
            self.stack[-1]
            == "p"
        ):
            self.paras.append(
                text
            )


def count_words(
    text: str,
) -> int:
    return len(
        WORD_RE.findall(text)
    )


def split_sentences(
    text: str,
) -> list[str]:
    return SENTENCE_SPLIT_RE.split(
        text
    )


def audit_html(
    text: str,
) -> None:
    parser = VisibleText()
    parser.feed(text)

    visible = " ".join(
        parser.h2
        + parser.paras
    )

    if SECOND_PERSON_RE.search(
        visible
    ):
        raise SystemExit(
            "spoken-language audit: "
            "second-person language found"
        )

    for heading in parser.h2:
        if (
            count_words(heading)
            > 6
        ):
            raise SystemExit(
                "spoken-language audit: "
                "long section heading: "
                + heading
            )

    for para in parser.paras:
        if para.startswith(
            "Supports:"
        ):
            continue

        for sentence in (
            split_sentences(
                para
            )
        ):
            if (
                count_words(sentence)
                > 38
            ):
                raise SystemExit(
                    "spoken-language audit: "
                    "sentence >38 words: "
                    + sentence
                )


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        subprocess.check_call(
            [
                sys.executable,
                str(
                    ROOT
                    / "scripts/build_web.py"
                ),
                "--output",
                directory,
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )

        text = (
            Path(directory)
            / "index.html"
        ).read_text(
            encoding="utf-8"
        )

        audit_html(text)

    print(
        "PASS - spoken-language audit"
    )


if __name__ == "__main__":
    main()
