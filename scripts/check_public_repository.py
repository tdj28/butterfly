#!/usr/bin/env python3
"""Check tracked files for common credentials; never print matching contents.

This bounded check supplements secret scanning; it is not an exhaustive
credential detector or a history scan. Use --staged to inspect index bytes
before committing, or the default to inspect the current tracked worktree.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ENV_EXAMPLES = {".env-example", ".env.example"}
PATTERNS = {
    "provider credential": re.compile(
        rb"\b(?:sk-(?:proj-|ant-)?|hf_|ghp_|github_pat_|rpa_)[A-Za-z0-9_-]{24,}"
    ),
    "private key": re.compile(
        rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
    ),
    "AWS access identifier": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
}


def check_file(name: str, data: bytes) -> list[str]:
    """Return issue categories only, with no credential text."""
    path = Path(name)
    issues = []
    if (path.name.startswith(".env") and path.name not in ENV_EXAMPLES) or (
        path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
    ):
        issues.append("credential file must not be tracked")
    if path.name in ENV_EXAMPLES:
        for line in data.splitlines():
            line = line.lstrip()
            if re.match(rb"^(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=", line):
                if line.split(b"=", 1)[1].strip():
                    issues.append("environment template contains a nonempty value")
                    break
    issues.extend(label for label, pattern in PATTERNS.items() if pattern.search(data))
    return issues


def worktree_contents(path: Path) -> bytes | None:
    """Read tracked contents without following links, including broken links."""
    if path.is_symlink():
        return str(path.readlink()).encode()
    if not path.exists():
        return None  # A tracked deletion contributes no public contents.
    return path.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="scan index bytes")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    names = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=root
    ).decode().split("\0")
    failures = []
    scanned = 0
    for name in filter(None, names):
        if args.staged:
            data = subprocess.check_output(["git", "show", f":{name}"], cwd=root)
        else:
            data = worktree_contents(root / name)
            if data is None:
                continue
        scanned += 1
        failures.extend(f"{name}: {issue}" for issue in check_file(name, data))
    if failures:
        print("FAIL: possible public credential exposure (contents suppressed)")
        print("\n".join(failures))
        return 1
    print(f"PASS: {scanned} tracked files checked for common credential patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
