#!/usr/bin/env python3
"""Read-only EXP-481 reference audit; numerical checks live in paired_inputs."""
import argparse
import hashlib
import json
from pathlib import Path

from butterfly.paired_inputs import extract_references, load_legacy_raw
from butterfly.paired_inputs import load_references as _load_references
from butterfly._paired_startup import write_json


ROOT = Path(__file__).resolve().parents[1]


def descriptor(path):
    path = Path(path)
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def load_references(plan, root=ROOT):
    return _load_references(plan, root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    plan_path = ROOT/"experiments/manifests/EXP-481-paired-sampling-proposal.json"
    args.output_dir.mkdir(parents=True, exist_ok=False)
    write_json(args.output_dir/"started.json", {"script": descriptor(Path(__file__)), "plan": descriptor(plan_path),
        "target_trajectories_generated": 0})
    try:
        result = load_references(json.loads(plan_path.read_bytes()))
    except (Exception, KeyboardInterrupt) as error:
        write_json(args.output_dir/"failure.json", {"status": "failed", "type": type(error).__name__,
            "message": str(error), "target_trajectories_generated": 0})
        raise
    write_json(args.output_dir/"receipt.json", result)
    print(json.dumps({"passed": result["passed"], "cases": [r["candidate_id"] for r in result["cases"]],
        "receipt": descriptor(args.output_dir/"receipt.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
