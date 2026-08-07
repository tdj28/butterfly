#!/usr/bin/env python3
"""Audit Poincare recurrence periods of parents and children near flip events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from audit_double_cover_events import select_event
from qualify_separated_normal_form import correct_fixed_b, interpolate_branch


def recurrence(parameters: RosslerParameters, state: np.ndarray, period: float, solver: SolverConfig, config: dict) -> dict:
    crossings = collect_crossings(
        parameters,
        state,
        legacy_rossler_section(parameters),
        transient=0.0,
        observation_horizon=float(config["observed_orbit_periods"]) * period,
        max_crossings=int(config["max_crossings"]),
        config=solver,
    )
    result = classify_fundamental_period(
        crossings.states,
        max_period=int(config["max_period"]),
        required_repeats=int(config["required_repeats"]),
        atol=float(config["atol"]),
        rtol=float(config["rtol"]),
    )
    return {
        "integration_success": crossings.integration_success,
        "crossing_count": len(crossings.times),
        "label": result.label.value,
        "fundamental_period": result.fundamental_period,
        "recurrence_error": result.recurrence_error,
    }


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
    if manifest.get("schema") != "butterfly.flip-recurrence-identity-manifest.v1":
        raise SystemExit("unsupported recurrence identity manifest")
    paths = {
        "source_event": args.source_event,
        "source_surface": args.source_surface,
        "source_curve": args.source_curve,
        "source_branch": args.source_branch,
        "separated_branch": args.separated_branch,
        "fold_branch": args.fold_branch,
    }
    raw = {name: path.read_bytes() for name, path in paths.items()}
    for name, value in raw.items():
        if sha256_bytes(value) != manifest["source_receipt_sha256"][name]:
            raise SystemExit(f"{name} receipt hash mismatch")
    receipts = {name: json.loads(value) for name, value in raw.items()}
    source = {"commit": git_value("rev-parse", "HEAD"), "branch": git_value("branch", "--show-current"), "dirty": bool(git_value("status", "--porcelain"))}
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("recurrence identity audit requires clean source")

    event_receipts = {key: receipts[key] for key in ("source_event", "source_surface", "source_curve")}
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    mu = float(manifest["mu_offset"])
    expected = manifest["expected_periods"]
    started = time.perf_counter()
    rows = []
    for specification in manifest["events"]:
        event = select_event(specification, event_receipts)
        branch_receipt = receipts[specification["branch_source"]]
        branches = branch_receipt.get("switched_branches", branch_receipt.get("branches"))
        branch = next(row for row in branches if int(row["direction"]) == int(specification["branch_direction"]))

        parent, _ = correct_fixed_b(
            a=event["a"], b=event["b"] - mu, c=event["c"],
            initial_state=np.asarray(event["initial_state"], dtype=float), period_time=event["period_time"],
            solver=solver, tolerance=float(corrector["tolerance"]), max_evaluations=int(corrector["max_evaluations"]),
        )
        target_b = event["b"] + mu
        child_state, child_period = interpolate_branch(branch["rows"], target_b)
        child, _ = correct_fixed_b(
            a=event["a"], b=target_b, c=event["c"], initial_state=child_state, period_time=child_period,
            solver=solver, tolerance=float(corrector["tolerance"]), max_evaluations=int(corrector["max_evaluations"]),
        )
        parent_parameters = RosslerParameters(a=event["a"], b=event["b"] - mu, c=event["c"])
        child_parameters = RosslerParameters(a=event["a"], b=target_b, c=event["c"])
        parent_recurrence = recurrence(parent_parameters, parent.initial_state, parent.period_time / 2.0, solver, manifest["crossings"])
        child_recurrence = recurrence(child_parameters, child.initial_state, child.period_time, solver, manifest["crossings"])
        row = {
            "id": specification["id"],
            "event_parameters": {"a": event["a"], "b": event["b"], "c": event["c"]},
            "parent_test_b": event["b"] - mu,
            "child_test_b": target_b,
            "parent_fundamental_flow_period": parent.period_time / 2.0,
            "child_flow_period": child.period_time,
            "parent_recurrence": parent_recurrence,
            "child_recurrence": child_recurrence,
        }
        row["passed"] = bool(
            parent_recurrence["integration_success"]
            and child_recurrence["integration_success"]
            and parent_recurrence["label"] == OrbitLabel.PERIODIC.value
            and child_recurrence["label"] == OrbitLabel.PERIODIC.value
            and parent_recurrence["fundamental_period"] == int(expected["parent"])
            and child_recurrence["fundamental_period"] == int(expected["child"])
        )
        rows.append(row)

    receipt = {
        "schema": "butterfly.flip-recurrence-identity-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": {name: sha256_bytes(value) for name, value in raw.items()},
        "source": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__},
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation_limit": "Recurrence identity classifies this local flip component; locating the earlier period-5 to period-3 family switch requires a separate continuation audit.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
