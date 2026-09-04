#!/usr/bin/env python3
"""Check release SHA-256 and all member hashes; optionally extract safely."""

import argparse
import json
from pathlib import Path

try:
    from scripts.research_bundle import extract_archive, read_archive
except ModuleNotFoundError:
    from research_bundle import extract_archive, read_archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256", required=True, help="trusted archive checksum published with the release")
    parser.add_argument("--extract", type=Path, help="new directory; existing destinations are refused")
    args = parser.parse_args()
    if args.extract is None:
        index, _ = read_archive(args.archive, expected_sha256=args.sha256)
    else:
        index = extract_archive(args.archive, args.extract, expected_sha256=args.sha256)
    print(json.dumps({"verified": True, "bundle_id": index["bundle_id"], "files": len(index["files"]), "source": index["source"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
