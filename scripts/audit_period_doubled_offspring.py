#!/usr/bin/env python3
"""Audit parent and offspring fundamental periods beyond qualified flip events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, flow_monodromy
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from audit_double_cover_events import select_event
from qualify_separated_normal_form import correct_fixed_b, interpolate_branch


def transverse_modulus(monodromy: object) -> float:
    neutral = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    return float(np.max(np.abs(np.delete(monodromy.multipliers, neutral))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-event", type=Path, required=True)
    parser.add_argument("--source-surface", type=Path, required=True)
    parser.add_argument("--source-curve", type=Path, required=True)
    parser.add_argument("--source-branch", type=Path, required=True)
    parser.add_argument("--separated-branch", type=Path, required=True)
    parser.add_argument("--fold-branch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period-doubled-offspring-audit-manifest.v1":
        raise SystemExit("unsupported offspring audit manifest")

    paths = {
        "source_event": args.source_event,
        "source_surface": args.source_surface,
        "source_curve": args.source_curve,
        "source_branch": args.source_branch,
        "separated_branch": args.separated_branch,
        "fold_branch": args.fold_branch,
    }
    raw_receipts = {name: path.read_bytes() for name, path in paths.items()}
    for name, raw in raw_receipts.items():
        if sha256_bytes(raw) != manifest["source_receipt_sha256"][name]:
            raise SystemExit(f"{name} receipt hash does not match manifest")
    receipts = {name: json.loads(raw) for name, raw in raw_receipts.items()}

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("offspring audit requires clean source")

    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    acceptance = manifest["acceptance"]
    mu = float(manifest["mu_offset"])
    event_receipts = {
        key: receipts[key] for key in ("source_event", "source_surface", "source_curve")
    }
    started = time.perf_counter()
    rows = []

    for specification in manifest["events"]:
        event = select_event(specification, event_receipts)
        target_b = float(event["b"]) + mu
        branch_receipt = receipts[specification["branch_source"]]
        branches = branch_receipt.get("switched_branches", branch_receipt.get("branches"))
        branch = next(
            candidate
            for candidate in branches
            if int(candidate["direction"]) == int(specification["branch_direction"])
        )

        parent_correction, _ = correct_fixed_b(
            a=float(event["a"]),
            b=target_b,
            c=float(event["c"]),
            initial_state=np.asarray(event["initial_state"], dtype=float),
            period_time=float(event["period_time"]),
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )
        child_seed_state, child_seed_period = interpolate_branch(branch["rows"], target_b)
        child_correction, child_full = correct_fixed_b(
            a=float(event["a"]),
            b=target_b,
            c=float(event["c"]),
            initial_state=child_seed_state,
            period_time=child_seed_period,
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )

        parameters = RosslerParameters(
            a=float(event["a"]), b=target_b, c=float(event["c"])
        )
        parent_half = flow_monodromy(
            parameters,
            parent_correction.initial_state,
            parent_correction.period_time / 2.0,
            config=solver,
        )
        parent_full = flow_monodromy(
            parameters,
            parent_correction.initial_state,
            parent_correction.period_time,
            config=solver,
        )
        child_half = flow_monodromy(
            parameters,
            child_correction.initial_state,
            child_correction.period_time / 2.0,
            config=solver,
        )
        parent_half_modulus = transverse_modulus(parent_half)
        child_full_modulus = transverse_modulus(child_full)

        row = {
            "id": specification["id"],
            "parameters": {
                "a": float(event["a"]),
                "b": target_b,
                "c": float(event["c"]),
            },
            "mu": mu,
            "parent_stored_period": parent_correction.period_time,
            "parent_fundamental_period": parent_correction.period_time / 2.0,
            "parent_full_closure": parent_full.closure_error,
            "parent_half_closure": parent_half.closure_error,
            "parent_half_transverse_modulus": parent_half_modulus,
            "child_period": child_correction.period_time,
            "child_full_closure": child_full.closure_error,
            "child_half_closure": child_half.closure_error,
            "child_full_transverse_modulus": child_full_modulus,
            "period_ratio_child_to_parent_fundamental": child_correction.period_time
            / (parent_correction.period_time / 2.0),
        }
        row["passed"] = bool(
            row["parent_full_closure"] <= float(acceptance["max_full_closure"])
            and row["parent_half_closure"]
            <= float(acceptance["max_parent_half_closure"])
            and row["child_full_closure"] <= float(acceptance["max_full_closure"])
            and row["child_half_closure"]
            >= float(acceptance["minimum_child_half_closure"])
            and row["parent_half_transverse_modulus"]
            >= float(acceptance["minimum_unstable_parent_modulus"])
            and row["child_full_transverse_modulus"]
            <= float(acceptance["maximum_stable_child_modulus"])
            and abs(row["period_ratio_child_to_parent_fundamental"] - 2.0)
            <= float(acceptance["maximum_period_ratio_distance_to_two"])
        )
        rows.append(row)

    receipt = {
        "schema": "butterfly.period-doubled-offspring-audit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": {
            name: sha256_bytes(raw) for name, raw in raw_receipts.items()
        },
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation_limit": "Off-event parent/child period and stability identities confirm the local period-doubling classification at three points; global uniformity and interval validation remain open.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
