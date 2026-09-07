#!/usr/bin/env python3
"""Generate result-free EXP-481 seed/batch tables and exact-map controls only."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

from butterfly.paired_sampling import seed_table, seed_commitment
from butterfly.seed_return_map import audit_map, MapOptions, VARIANTS

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments/manifests/EXP-481-paired-sampling-proposal.json"


def write(path, payload):
    with path.open("x") as stream:
        json.dump(payload, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def descriptor(path):
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": path.name, "bytes": path.stat().st_size, "sha256": digest}


def build_tables(plan):
    """No input artifacts or solver calls; inputs are pure declarations."""
    if (plan["schema"] != "butterfly.paired-sampling-proposal.v1"
            or plan["status"] != "numeric-proposal-unreviewed" or plan["execution_authorized"] is not False
            or plan["review"] is not None
            or plan["candidate_ids"] != ["local-a025-c083", "local-a027-c083"]
            or plan["seeds"]["count_per_case"] != 8192 or plan["collection"]["batch_size"] != 64
            or plan["seeds"]["xz_ranges"] != [[-14., -.2], [.008, .55]]
            or plan["seeds"]["generator"] != "PCG64"
            or plan["seeds"]["global_seed_ids"] != [0, 8191]
            or plan["seeds"]["holdout_ids"] != [4096, 8191]
            or plan["collection"]["profiles"] != [{"name": "rk4-001", "dt": .01}, {"name": "rk4-0005", "dt": .005}]
            or plan["analysis"]["options"] != asdict(MapOptions())
            or plan["analysis"]["variants"] != [list(v) for v in VARIANTS]):
        raise ValueError("unsupported or promoted sampling proposal")
    table = seed_table(plan["seeds"]["count_per_case"], random_seed=plan["seeds"]["random_seed"])
    if seed_commitment(table) != plan["seeds"]["ordered_table_sha256"]:
        raise ValueError("seed table differs from proposal commitment")
    rows = []
    for case in plan["candidate_ids"]:
        for profile in plan["collection"]["profiles"]:
            for batch in range(128):
                rows.append({"trial_id": f"{case}-{profile['name']}-batch-{batch:03d}",
                    "candidate_id": case, "profile": profile["name"], "dt": profile["dt"],
                    "global_seed_start": batch*64, "global_seed_stop_exclusive": (batch+1)*64,
                    "split": "calibration" if batch < 64 else "holdout"})
    if len(rows) != 512 or len({r["trial_id"] for r in rows}) != 512:
        raise ValueError("incomplete or duplicated batch plan")
    return table, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(PLAN.read_bytes())
    table, rows = build_tables(plan)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=False)
    paths = [PLAN, Path(__file__), ROOT / "python/butterfly/paired_sampling.py", ROOT / "python/butterfly/seed_return_map.py"]
    config = {"kind": "EXP-481-outcome-free-sampling-qualification", "python": platform.python_version(),
        "numpy": np.__version__, "source_sha256": {str(p.relative_to(ROOT)): descriptor(p)["sha256"] for p in paths},
        "target_trajectories": 0, "seed_commitment": seed_commitment(table), "batch_count": len(rows),
        "map_options": asdict(MapOptions()), "variants": [list(v) for v in VARIANTS],
        "synthetic_seeds_per_split": 512, "pairs_per_seed": 4,
        "calibration_rng_seed": 481101, "validation_rng_seed": 481102}
    write(output / "started.json", config)
    with (output / "seeds.npz").open("xb") as stream:
        np.savez_compressed(stream, **table)
    write(output / "batch-plan.json", {"rows": rows, "execution_authorized": False})
    calx = np.random.Generator(np.random.PCG64(481101)).random((512, 4))
    valx = np.random.Generator(np.random.PCG64(481102)).random((512, 4))
    records = []
    for name, expected, branches in (("monotone", True, 1), ("cubic", True, 3),
                                     ("stationary-inflection", True, 1), ("multivalued-holdout", False, None)):
        fn = (lambda x: .5+4*(x-.5)**3-.75*(x-.5)) if name == "cubic" else (lambda x: .2+.6*x)
        if name == "stationary-inflection":
            fn = lambda x: .5+4*(x-.5)**3
        cal = np.stack((calx, fn(calx)), axis=-1)
        val = np.stack((valx, fn(valx)), axis=-1)
        if name == "multivalued-holdout":
            val[:, :, 1] += np.where(np.arange(512) % 2, .25, -.25)[:, None]
        cids, vids = np.arange(512), np.arange(512)+10000
        raw = output / (name+".npz")
        with raw.open("xb") as stream:
            np.savez_compressed(stream, calibration=cal, validation=val, calibration_ids=cids, validation_ids=vids)
        result = audit_map(cal, val, calibration_ids=cids, validation_ids=vids)
        write(output / (name+".json"), result)
        records.append({"control": name, "expected_resolved": expected, "expected_branch_count": branches,
            "resolved": result["resolved"], "branch_count": result["branch_count"], "reason": result["reason"],
            "critical_intervals": result["critical_intervals"],
            "variant_heldout_q90_errors": [v.get("heldout_q90_error") for v in result["variants"]],
            "variant_heldout_affine_q90_errors": [v.get("heldout_affine_q90_error") for v in result["variants"]],
            "variant_bootstrap_consensus": [v.get("bootstrap_consensus") for v in result["variants"]],
            "passed": result["resolved"] == expected and result["branch_count"] == branches,
            "raw": descriptor(raw), "audit": descriptor(output / (name+".json"))})
    receipt = {"kind": config["kind"], "target_trajectories": 0, "passed": all(r["passed"] for r in records),
        "configuration": descriptor(output / "started.json"), "seed_table": descriptor(output / "seeds.npz"),
        "batch_plan": descriptor(output / "batch-plan.json"), "controls": records}
    write(output / "receipt.json", receipt)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
