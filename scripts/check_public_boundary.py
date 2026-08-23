#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import re
import unicodedata

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(
    os.getenv("BN7_SCAN_ROOT", str(DEFAULT_ROOT))
).resolve()
SELF = Path(__file__).resolve()

TEXT_EXT = {
    ".md", ".json", ".py", ".html", ".css", ".js",
    ".yml", ".yaml", ".txt", ".cff",
}

FORBIDDEN_FILES = {
    "ROADMAP.md",
    "PROJECT_FACTS.json",
    "MANIFEST.json",
}
FORBIDDEN_PREFIXES = (
    "analysis/",
    "intelligence/",
    "governance/",
)

ALLOWED_EMAILS = {"contact@bridgenode7.com"}

SECRET_PATTERNS = (
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub token"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "API secret"),
    (re.compile(r"[A-Za-z]:\\{1,2}Users\\{1,2}[^\\\r\n]+"), "Windows user path"),
    (re.compile(r"/home/[^/\s]+/"), "home path"),

    (
        re.compile(
            r"(?i)\b(?:api[_-]?key|client[_-]?secret|"
            r"access[_-]?token|password|passwd)"
            r"\s*[:=]\s*[\"']?"
            r"[A-Za-z0-9_./+=-]{20,}"
        ),
        "credential assignment",
    ),
    (
        re.compile(
            r"https?://[^/\s:@]+:[^@\s/]+@"
        ),
        "credential-bearing URL",
    ),
    (
        re.compile(
            r"(?i)https?://[^\s?#]+[?&]"
            r"(?:token|api[_-]?key|access[_-]?token|secret)="
            r"[^&#\s]{12,}"
        ),
        "credential-bearing URL",
    ),
)

DISCLOSURE_PATTERNS = (
    (re.compile(r"\bActual Upgrade Payload\b", re.I), "implementation-payload language"),
    (re.compile(r"\bfuture AI-assisted intelligence workflows\b", re.I), "future-plan language"),
    (re.compile(r"\bLive intelligence operations\b", re.I), "future-plan language"),
    (re.compile(r"\bcontrolled intelligence research artifacts\b", re.I), "private-capability disclosure"),
    (re.compile(r"\b(?:internal|private)\s+(?:strategy|roadmap|operator|playbook|reasoning)\b", re.I),
     "internal operating disclosure"),
)

BIDI_AND_INVISIBLE = {
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
    "\u2066", "\u2067", "\u2068", "\u2069",
    "\u200b", "\u200c", "\u200d", "\ufeff",
}


CONFUSABLE_ASCII = str.maketrans({
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "х": "x",
    "у": "y",
    "і": "i",
    "һ": "h",
    "Α": "A",
    "Β": "B",
    "Ε": "E",
    "Η": "H",
    "Ι": "I",
    "Κ": "K",
    "Μ": "M",
    "Ν": "N",
    "Ο": "O",
    "Ρ": "P",
    "Τ": "T",
    "Χ": "X",
    "Υ": "Y",
})


def normalize_for_scan(text: str) -> str:
    return unicodedata.normalize(
        "NFKC",
        text,
    ).translate(
        CONFUSABLE_ASCII
    )


def secret_labels(text: str) -> set[str]:
    scan_text = normalize_for_scan(
        text
    )

    return {
        label
        for regex, label in SECRET_PATTERNS
        if regex.search(scan_text)
    }

def tracked_candidate_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if ".git" in p.parts or "build" in p.parts or "__pycache__" in p.parts:
            continue
        yield p

def main() -> None:
    errors = []

    for rel in sorted(FORBIDDEN_FILES):
        if (ROOT / rel).exists():
            errors.append(f"{rel}: unnecessary public artifact")

    for prefix in FORBIDDEN_PREFIXES:
        base = ROOT / prefix.rstrip("/")
        if base.exists():
            errors.append(f"{prefix}: unnecessary public operating surface")

    for path in tracked_candidate_files():
        if path.resolve() == SELF or path.suffix.lower() not in TEXT_EXT:
            continue

        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        scan_text = normalize_for_scan(text)

        for regex, label in SECRET_PATTERNS:
            if regex.search(scan_text):
                errors.append(f"{rel}: {label}")

        emails = set(
            re.findall(
                r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
                text,
                re.I,
            )
        )
        bad = emails - ALLOWED_EMAILS
        if bad:
            errors.append(f"{rel}: unapproved email(s) {sorted(bad)}")

        for regex, label in DISCLOSURE_PATTERNS:
            if regex.search(scan_text):
                errors.append(f"{rel}: {label}")

        for ch in BIDI_AND_INVISIBLE:
            if ch in text:
                errors.append(
                    f"{rel}: unsafe invisible/bidirectional character U+{ord(ch):04X}"
                )

        for ch in text:
            if unicodedata.bidirectional(ch) in {"RLO", "LRO", "RLE", "LRE", "PDF"}:
                errors.append(
                    f"{rel}: unsafe bidi control U+{ord(ch):04X}"
                )
                break

    if errors:
        raise SystemExit("\n".join(sorted(set(errors))))

    print("PASS - public boundary")

if __name__ == "__main__":
    main()
