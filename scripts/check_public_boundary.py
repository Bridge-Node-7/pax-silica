#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
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

ALLOWED_TOP_LEVEL = {
    ".editorconfig", ".gitattributes", ".github", ".gitignore",
    "CHANGELOG.md", "LICENSE", "Makefile", "NOTICE", "README.md", "SECURITY.md", "VERSION",
    "data", "docs", "requirements-browser.lock", "scripts", "tests", "web",
}

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
        re.compile(r"https?://[^/\s:@]+:[^@\s/]+@"),
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

BLOCKED_PHRASE_SHA256 = {
    3: {
        "489e3a239dc51f08dde0280697a5c6a00602936e4847cadc6b39cddbb6959210",
        "3e3997740857444c6cd70a1bea75d6476ed7aa2bbb2bdfffca708e1a13ebc8f3",
    },
    4: {
        "e7b1efdf2fb28d3ec109c059d85ba09f657bb4a55f62793ac911615df311d51b",
        "07a7854bcc7e4ccb039c5ff7f8525682b54a78e3a97434aa99948ffad38a5321",
    },
    2: {
        "12361854c309ea67db7e9e6eaac270f29cf9eb92088e3e9d695181ba45aa1b0a",
        "b75f9c5876a1f6ebd56993bb114ca7eb996badc15835c06339d4f857b8d81257",
        "89fb5eb081fefd1530c92f8aca80428fbcfd2da53a11c5377756bd5d1f9b7943",
        "0713116b5b2257db70cea0fee2fad4e78f6e09dcea21d4919523ffac59ada992",
        "f581ccde225c15a68ce5225b2687030b59fe621db4e339fe3967512a7b3916e4",
        "fb12102dfa45c1b045667b06cce765131a2398b2c6be5396becf70021e870e3a",
        "ea6f3fe30543a65b491e4a8dfb733ea5cd7209e02fc58f0be1d7ecd5c3e56945",
        "8e858f72f77bd859b20ef267454f249f35b34cb304b4917f6d7d8efed7ddba04",
        "e2dc63993d16fe1fb1ed51b5955b6bfd9f9c216bf31e796fa4a10f6245ce1e34",
        "2be21a13a27625e69f047fc5fc3571c3dd361e36addd3d94dba160b22b5d055c",
    },
}

BIDI_AND_INVISIBLE = {
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
    "\u2066", "\u2067", "\u2068", "\u2069",
    "\u200b", "\u200c", "\u200d", "\ufeff",
}

CONFUSABLE_ASCII = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y", "і": "i", "һ": "h",
    "Α": "A", "Β": "B", "Ε": "E", "Η": "H", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T", "Χ": "X", "Υ": "Y",
})

EXCLUDE_PARTS = {".git", "build", "__pycache__", ".venv", "venv", "dist", ".mypy_cache", ".pytest_cache"}


def normalize_for_scan(text: str) -> str:
    return unicodedata.normalize("NFKC", text).translate(CONFUSABLE_ASCII)


def secret_labels(text: str) -> set[str]:
    scan_text = normalize_for_scan(text)
    return {label for regex, label in SECRET_PATTERNS if regex.search(scan_text)}


def blocked_phrase_hash_hits(text: str) -> int:
    tokens = re.findall(r"[a-z0-9-]+", normalize_for_scan(text).lower())
    hits = 0
    for width, blocked in BLOCKED_PHRASE_SHA256.items():
        if len(tokens) < width:
            continue
        for i in range(len(tokens) - width + 1):
            phrase = " ".join(tokens[i:i + width])
            digest = hashlib.sha256(phrase.encode("utf-8")).hexdigest()
            if digest in blocked:
                hits += 1
    return hits


def tracked_candidate_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if EXCLUDE_PARTS & set(p.parts):
            continue
        yield p


def main() -> None:
    errors = []

    if ROOT == DEFAULT_ROOT:
        unexpected = sorted(
            p.name for p in ROOT.iterdir()
            if p.name not in ALLOWED_TOP_LEVEL and p.name not in EXCLUDE_PARTS
        )
        if unexpected:
            errors.append("unexpected top-level public artifact(s): " + ", ".join(unexpected))

    for path in tracked_candidate_files():
        if path.resolve() == SELF or path.suffix.lower() not in TEXT_EXT:
            continue

        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        scan_text = normalize_for_scan(text)

        for regex, label in SECRET_PATTERNS:
            if regex.search(scan_text):
                errors.append(f"{rel}: {label}")

        emails = set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I))
        bad = emails - ALLOWED_EMAILS
        if bad:
            errors.append(f"{rel}: unapproved email(s) {sorted(bad)}")

        if blocked_phrase_hash_hits(text):
            errors.append(f"{rel}: restricted release-surface content")

        for ch in BIDI_AND_INVISIBLE:
            if ch in text:
                errors.append(f"{rel}: unsafe invisible/bidirectional character U+{ord(ch):04X}")

        for ch in text:
            if unicodedata.bidirectional(ch) in {"RLO", "LRO", "RLE", "LRE", "PDF"}:
                errors.append(f"{rel}: unsafe bidi control U+{ord(ch):04X}")
                break

    if errors:
        raise SystemExit("\n".join(sorted(set(errors))))

    print("PASS - public boundary")

if __name__ == "__main__":
    main()
