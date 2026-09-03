#!/usr/bin/env python3
"""Compare new 256-return PIM controls with frozen 128-return references."""
from __future__ import annotations

import argparse
import io
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, barrio_rossler_section
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from qualify_censored_pim_saddle_controls import _run_profile
from qualify_pim_saddle_controls import (
    _combined_critical_spans,
    _cycle_reference,
)


def _compare_reference(coordinate_row, reference):
    if (
        coordinate_row["source_minimum"] is None
        or coordinate_row["source_maximum"] is None
        or not coordinate_row["robust_oracle"]["resolved"]
    ):
        return {
            "resolved": False,
            "critical_point_intervals": [],
            "normalized_spans": [],
            "maximum_normalized_span": 1e300,
        }
    return _combined_critical_spans(coordinate_row, reference)


def _run_case(case, manifest, solver):
    fixed = manifest["fixed_parameters"]
    parameters = RosslerParameters(
        a=float(case["a"]), b=float(fixed["b"]), c=float(fixed["c"])
    )
    section = barrio_rossler_section(parameters)
    cycle_crossings, cycle_classification = _cycle_reference(
        parameters, section, manifest, solver
    )
    stable_period = int(case["stable_period"])
    cycle = cycle_crossings.states[-stable_period:]
    profile, states = _run_profile(
        case,
        manifest["target_profile"],
        manifest,
        solver,
        parameters,
        section,
        cycle,
    )
    horizon_comparison = {
        coordinate["name"]: _compare_reference(
            profile["coordinates"][coordinate["name"]],
            case["horizon_128_reference"][coordinate["name"]],
        )
        for coordinate in manifest["coordinates"]
    }
    passed = (
        cycle_classification.fundamental_period == stable_period
        and profile["passed"]
        and all(
            row["resolved"]
            and row["maximum_normalized_span"]
            <= float(
                manifest["acceptance"]["maximum_128_256_critical_span"]
            )
            for row in horizon_comparison.values()
        )
    )
    return (
        {
            "id": case["id"],
            "parameters": asdict(parameters),
            "expected_saddle_branch_count": int(
                case["expected_saddle_branch_count"]
            ),
            "stable_cycle_classification": asdict(cycle_classification),
            "target_profile": profile,
            "horizon_128_256_comparison": horizon_comparison,
            "passed": passed,
        },
        states,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states-output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.censored-pim-extension-manifest.v1":
        raise SystemExit("unsupported censor-aware PIM extension manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["reference_solver"])
    cases = []
    arrays = {}
    started = time.perf_counter()
    for case in manifest["cases"]:
        row, states = _run_case(case, manifest, solver)
        cases.append(row)
        for line_id, values in states.items():
            arrays[
                f"{case['id']}__{manifest['target_profile']['id']}__{line_id}"
            ] = values
    state_buffer = io.BytesIO()
    np.savez_compressed(state_buffer, **arrays)
    state_bytes = state_buffer.getvalue()
    atomic_write(args.states_output, state_bytes)
    receipt = {
        "schema": "butterfly.censored-pim-extension-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "reference_receipt": manifest["reference_receipt"],
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "lifetime_workers": int(manifest["pim"]["lifetime_workers"]),
        },
        "states_artifact": str(args.states_output),
        "states_artifact_bytes": len(state_bytes),
        "states_artifact_sha256": sha256_bytes(state_bytes),
        "cases": cases,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(case["passed"] for case in cases),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True), flush=True)
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
