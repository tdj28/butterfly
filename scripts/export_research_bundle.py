#!/usr/bin/env python3
"""Export or inventory the exact, frozen public core-data allowlist."""

import argparse
import json
from pathlib import Path

try:
    from scripts.research_bundle import build_archive, inventory
except ModuleNotFoundError:
    from research_bundle import build_archive, inventory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new .tar.gz file (omit for inventory only)")
    parser.add_argument("--allow-dirty", action="store_true", help="local draft only; records dirty=true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output is None:
        result, _ = inventory(root)
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(build_archive(root, args.output, allow_dirty=args.allow_dirty), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
