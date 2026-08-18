#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

TEXT_EXT = {
    ".md",
    ".json",
    ".py",
    ".html",
    ".css",
    ".js",
    ".yml",
    ".yaml",
    ".txt",
}

WINDOWS_USER_PATH_RE = re.compile(
    r"[A-Za-z]:\\{1,2}Users\\{1,2}[^\\\r\n]+"
)

SECRET_PATTERNS = [
    (
        re.compile(
            r"AKIA[0-9A-Z]{16}"
        ),
        "AWS key",
    ),
    (
        re.compile(
            r"-----BEGIN "
            r"(?:RSA |EC |OPENSSH )?"
            r"PRIVATE KEY-----"
        ),
        "private key",
    ),
    (
        re.compile(
            r"github_pat_"
            r"[A-Za-z0-9_]{20,}"
        ),
        "GitHub token",
    ),
    (
        re.compile(
            r"ghp_[A-Za-z0-9]{30,}"
        ),
        "GitHub token",
    ),
    (
        re.compile(
            r"sk-[A-Za-z0-9_-]{20,}"
        ),
        "API secret",
    ),
    (
        WINDOWS_USER_PATH_RE,
        "Windows user path",
    ),
    (
        re.compile(
            r"/home/[^/\s]+/"
        ),
        "home path",
    ),
]

ALLOWED_EMAILS = {
    "contact@bridgenode7.com"
}

PUBLIC_SURFACE = (
    "README.md",
    "CHANGELOG.md",
    "NOTICE",
    "PROJECT_FACTS.json",
    "docs/CREDIBILITY.md",
    "docs/INTELLIGENCE_MODEL.md",
    "docs/MAINTENANCE.md",
    "docs/RELEASE_ENGINEERING.md",
    "docs/SOURCE_STATES.md",
    "docs/VISUAL_CONTRACT.md",
)

NONPUBLIC_DISCLOSURE_PATTERNS = [
    (
        re.compile(
            r"\b(?:credential|"
            r"service account|"
            r"private key|"
            r"access token)"
            r"(?:s|ing| configuration|"
            r" architecture)?\b",
            re.I,
        ),
        "sensitive configuration language",
    ),
    (
        re.compile(
            r"\b(?:roadmap|next release|"
            r"next update|future activation|"
            r"activation sequence)\b",
            re.I,
        ),
        "future-plan language",
    ),
    (
        re.compile(
            r"\b(?:scan|monitoring)\s+"
            r"(?:timestamp|cadence|schedule)\b",
            re.I,
        ),
        "operational telemetry language",
    ),
    (
        re.compile(
            r"\b(?:prompt orchestration|"
            r"control plane|"
            r"internal operator)\b",
            re.I,
        ),
        "internal operating language",
    ),
]


def secret_labels(
    text: str,
) -> set[str]:
    return {
        label
        for regex, label
        in SECRET_PATTERNS
        if regex.search(text)
    }


def iter_text_files():
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or
            ".git" in path.parts
            or
            path.suffix.lower()
            not in TEXT_EXT
            or
            path.resolve()
            == Path(__file__).resolve()
        ):
            continue

        yield path


def main() -> None:
    errors = []

    for path in iter_text_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for label in sorted(
            secret_labels(text)
        ):
            errors.append(
                f"{path.relative_to(ROOT)}: "
                f"{label}"
            )

        emails = set(
            re.findall(
                r"[A-Z0-9._%+-]+"
                r"@[A-Z0-9.-]+"
                r"\.[A-Z]{2,}",
                text,
                re.I,
            )
        )

        bad = (
            emails
            - ALLOWED_EMAILS
        )

        if bad:
            errors.append(
                f"{path.relative_to(ROOT)}: "
                "unapproved email(s) "
                f"{sorted(bad)}"
            )

    for rel in PUBLIC_SURFACE:
        path = ROOT / rel

        if not path.is_file():
            errors.append(
                f"{rel}: "
                "missing public surface"
            )
            continue

        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for regex, label in (
            NONPUBLIC_DISCLOSURE_PATTERNS
        ):
            if regex.search(text):
                errors.append(
                    f"{rel}: {label}"
                )

    if errors:
        raise SystemExit(
            "\n".join(errors)
        )

    print(
        "PASS - public boundary"
    )


if __name__ == "__main__":
    main()
