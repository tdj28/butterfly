#!/usr/bin/env python3
"""Build a fresh local package of preserved EXP-481 inputs; never integrate."""
import argparse
import json
from pathlib import Path

from butterfly.paired_input_package import build_package


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_package(ROOT/"experiments/manifests/EXP-481-paired-sampling-proposal.json",
        ROOT, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
