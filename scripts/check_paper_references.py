#!/usr/bin/env python3
"""Check citations and local assets reachable from the manuscript entry point.

This checks the repository's literal LaTeX input/includegraphics conventions;
it is not a TeX interpreter and does not replace a full manuscript build.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
CITE_RE = re.compile(r"\\cite\w*\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}")
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
GRAPHICS_RE = re.compile(r"\\includegraphics\*?\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}")


def strip_comments(text: str) -> str:
    """Remove TeX line comments while preserving escaped percent signs."""
    lines = []
    for line in text.splitlines():
        for index, character in enumerate(line):
            if character != "%":
                continue
            preceding = index
            while preceding > 0 and line[preceding - 1] == "\\":
                preceding -= 1
            if (index - preceding) % 2 == 0:
                line = line[:index]
                break
        lines.append(line)
    return "\n".join(lines)


def bib_keys(text: str) -> set[str]:
    return set(BIB_KEY_RE.findall(text))


def citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in CITE_RE.finditer(strip_comments(text)):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def required_keys(text: str) -> set[str]:
    return {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def manuscript_sources(paper_dir: Path) -> tuple[dict[Path, str], list[str]]:
    """Follow inputs relative to the manuscript build directory, as LaTeX does."""
    sources: dict[Path, str] = {}
    failures: list[str] = []
    pending = [paper_dir / "manuscript.tex"]
    seen: set[Path] = set()
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        if not path.is_file():
            failures.append(f"missing manuscript source: {path}")
            continue
        text = strip_comments(path.read_text(encoding="utf-8"))
        sources[path] = text
        for filename in INPUT_RE.findall(text):
            child = paper_dir / filename.strip()
            if not child.suffix:
                child = child.with_suffix(".tex")
            pending.append(child)
    return sources, failures


def check_paper(paper_dir: Path) -> tuple[list[str], dict[str, int]]:
    bib_text = (paper_dir / "references.bib").read_text(encoding="utf-8")
    bibliography = bib_keys(bib_text)
    required = required_keys(
        (paper_dir / "required-citations.txt").read_text(encoding="utf-8")
    )
    sources, failures = manuscript_sources(paper_dir)
    tex = "\n".join(sources.values())
    cited = citation_keys(tex)

    duplicates = sorted(
        key for key, count in Counter(BIB_KEY_RE.findall(bib_text)).items() if count > 1
    )
    if duplicates:
        failures.append("duplicate BibTeX keys: " + ", ".join(duplicates))

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

    graphics = set(GRAPHICS_RE.findall(tex))
    for filename in sorted(graphics):
        path = paper_dir / filename.strip()
        candidates = [path] if path.suffix else [
            path.with_suffix(suffix) for suffix in (".pdf", ".png", ".jpg", ".jpeg")
        ]
        if not any(candidate.is_file() for candidate in candidates):
            failures.append(f"missing manuscript figure: {filename}")

    return failures, {
        "bibliography": len(bibliography),
        "cited": len(cited),
        "required": len(required),
        "sources": len(sources),
        "figures": len(graphics),
    }


def main() -> int:
    try:
        failures, counts = check_paper(PAPER_DIR)
    except OSError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: "
        f"{counts['bibliography']} BibTeX entries, {counts['cited']} cited keys, "
        f"{counts['required']} required citations present; "
        f"{counts['sources']} manuscript sources and {counts['figures']} figures present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
