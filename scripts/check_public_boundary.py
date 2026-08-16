#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

TEXT_EXT = {
    ".md", ".json", ".py", ".html", ".css",
    ".js", ".yml", ".yaml", ".txt"
}

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS key"),
    (
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?"
            r"PRIVATE KEY-----"
        ),
        "private key",
    ),
    (
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
        "GitHub token",
    ),
    (
        re.compile(r"ghp_[A-Za-z0-9]{30,}"),
        "GitHub token",
    ),
    (
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        "API secret",
    ),
    (
        re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\\\r\n]+"),
        "Windows user path",
    ),
    (
        re.compile(r"/home/[^/\s]+/"),
        "home path",
    ),
]

ALLOWED_EMAILS = {"contact@bridgenode7.com"}

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
            r"\b(?:credential|service account|private key|access token)"
            r"(?:s|ing| configuration| architecture)?\b",
            re.I,
        ),
        "sensitive configuration language",
    ),
    (
        re.compile(
            r"\b(?:roadmap|next release|next update|future activation|"
            r"activation sequence)\b",
            re.I,
        ),
        "future-plan language",
    ),
    (
        re.compile(
            r"\b(?:scan|monitoring)\s+(?:timestamp|cadence|schedule)\b",
            re.I,
        ),
        "operational telemetry language",
    ),
    (
        re.compile(
            r"\b(?:prompt orchestration|control plane|internal operator)\b",
            re.I,
        ),
        "internal operating language",
    ),
]

def iter_text_files():
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or ".git" in path.parts
            or path.suffix.lower() not in TEXT_EXT
            or path.resolve() == Path(__file__).resolve()
        ):
            continue
        yield path

def main():
    errors = []

    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")

        for rx, label in SECRET_PATTERNS:
            if rx.search(text):
                errors.append(
                    f"{path.relative_to(ROOT)}: {label}"
                )

        emails = set(
            re.findall(
                r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
                text,
                re.I,
            )
        )
        bad = emails - ALLOWED_EMAILS
        if bad:
            errors.append(
                f"{path.relative_to(ROOT)}: "
                f"unapproved email(s) {sorted(bad)}"
            )

    for rel in PUBLIC_SURFACE:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"{rel}: missing public surface")
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for rx, label in NONPUBLIC_DISCLOSURE_PATTERNS:
            if rx.search(text):
                errors.append(f"{rel}: {label}")

    if errors:
        raise SystemExit("\n".join(errors))

    print("PASS - public boundary")

if __name__ == "__main__":
    main()
