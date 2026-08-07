#!/usr/bin/env python3
"""Check the paper's citation, BibTeX, and referee-required-source contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
BIB_PATH = PAPER_DIR / "references.bib"
REQUIRED_PATH = PAPER_DIR / "required-citations.txt"

BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
CITE_RE = re.compile(r"\\cite\w*\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}")


def bib_keys(text: str) -> set[str]:
    return set(BIB_KEY_RE.findall(text))


def citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in CITE_RE.finditer(text):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def required_keys(text: str) -> set[str]:
    return {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def main() -> int:
    bibliography = bib_keys(BIB_PATH.read_text(encoding="utf-8"))
    required = required_keys(REQUIRED_PATH.read_text(encoding="utf-8"))
    tex = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(PAPER_DIR.rglob("*.tex"))
    )
    cited = citation_keys(tex)

    failures: list[str] = []
    missing_from_bib = cited - bibliography
    if missing_from_bib:
        failures.append(
            "cited but absent from references.bib: " + ", ".join(sorted(missing_from_bib))
        )

    required_bib_missing = required - bibliography
    if required_bib_missing:
        failures.append(
            "required but absent from references.bib: "
            + ", ".join(sorted(required_bib_missing))
        )

    required_cite_missing = required - cited
    if required_cite_missing:
        failures.append(
            "required but not cited in manuscript: "
            + ", ".join(sorted(required_cite_missing))
        )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: "
        f"{len(bibliography)} BibTeX entries, {len(cited)} cited keys, "
        f"{len(required)} required citations present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
