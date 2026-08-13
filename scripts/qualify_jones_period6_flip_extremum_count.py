#!/usr/bin/env python3
"""Qualify the EXP-213 grazing with extremum-partitioned section counts."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    legacy_rossler_section,
    rossler_equilibria,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.continue_jones_period6_flip_curve import _section_count, _solve_event
from scripts.refine_jones_period6_flip_section_grazing import (
    _scientific_event_passes,
    nearest_y_extremum,
)


SCHEMA = "butterfly.jones-period6-flip-extremum-count-manifest.v1"


def extremum_partitioned_legacy_count(parameters, state, period_time, solver):
    equilibrium = rossler_equilibria(parameters)[0]

    def y_extremum(_time, point):
        return point[0] + parameters.a * point[1]

    y_extremum.direction = 0
    y_extremum.terminal = False
    integration = solve_ivp(
        lambda time_value, point: rossler_rhs(time_value, point, parameters),
        (0.0, period_time),
        state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
        events=y_extremum,
        dense_output=True,
    )
    if not integration.success:
        raise RuntimeError(f"extremum-partition integration failed: {integration.message}")
    extrema = np.asarray(integration.t_events[0], dtype=float)
    extrema = extrema[(extrema > period_time * 1e-9) & (extrema < period_time * (1.0 - 1e-9))]
    boundaries = np.r_[0.0, extrema, period_time]
    roots = []
    for left, right in zip(boundaries[:-1], boundaries[1:], strict=True):
        left_value = float(integration.sol(left)[1] - equilibrium[1])
        right_value = float(integration.sol(right)[1] - equilibrium[1])
        if left_value * right_value >= 0.0:
            continue
        root = float(
            brentq(
                lambda time_value: float(integration.sol(time_value)[1] - equilibrium[1]),
                left,
                right,
                xtol=1e-13,
                rtol=1e-14,
            )
        )
        point = np.asarray(integration.sol(root), dtype=float)
        if point[0] < equilibrium[0]:
            roots.append(
                {
                    "time": root,
                    "state": point.tolist(),
                    "section_residual": float(point[1] - equilibrium[1]),
                    "gate_margin": float(equilibrium[0] - point[0]),
                }
            )
    return {
        "count": len(roots),
        "roots": roots,
        "extremum_count": int(len(extrema)),
        "maximum_section_residual": max(
            (abs(root["section_residual"]) for root in roots), default=0.0
        ),
    }


def evaluate(c_value, seed, manifest, solver):
    event = _solve_event(c_value, seed, manifest, solver)
    parameters = RosslerParameters(
        a=float(event["a"]), b=float(manifest["fixed_b"]), c=float(c_value)
    )
    standard_count, standard_success = _section_count(
        parameters,
        np.asarray(event["initial_state"], dtype=float),
        float(event["period_time"]),
        legacy_rossler_section(parameters),
        8,
        solver,
    )
    barrio_count, barrio_success = _section_count(
        parameters,
        np.asarray(event["initial_state"], dtype=float),
        float(event["period_time"]),
        barrio_rossler_section(parameters),
        8,
        solver,
    )
    return {
        "c": c_value,
        "event": event,
        "grazing": nearest_y_extremum(
            parameters,
            np.asarray(event["initial_state"], dtype=float),
            float(event["period_time"]),
            solver,
        ),
        "standard_historical_count": standard_count,
        "standard_historical_success": standard_success,
        "extremum_partitioned": extremum_partitioned_legacy_count(
            parameters,
            np.asarray(event["initial_state"], dtype=float),
            float(event["period_time"]),
            solver,
        ),
        "barrio_count": barrio_count,
        "barrio_success": barrio_success,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--grazing-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported extremum-count manifest")
    grazing_bytes = args.grazing_receipt.read_bytes()
    if sha256_bytes(grazing_bytes) != manifest["grazing_receipt_sha256"]:
        raise SystemExit("grazing receipt hash mismatch")
    grazing_receipt = json.loads(grazing_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("extremum-count qualification requires clean source")
    center_c = float(grazing_receipt["c_estimate"])
    seed = grazing_receipt["best_evaluation"]
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    started = time.perf_counter()
    rows = [
        evaluate(center_c + float(offset), seed, manifest, solver)
        for offset in manifest["signed_c_offsets"]
    ]
    control_offsets = {float(value) for value in manifest["independent_control_offsets"]}
    controls = [
        {
            "offset": float(offset),
            "reference": next(
                row for row in rows if float(row["c"]) == center_c + float(offset)
            ),
            "independent": evaluate(
                center_c + float(offset), seed, manifest, independent_solver
            ),
        }
        for offset in manifest["independent_control_offsets"]
        if float(offset) in control_offsets
    ]
    acceptance = manifest["acceptance"]

    def row_passes(row, offset):
        expected = (
            int(acceptance["lower_c_extremum_count"])
            if float(offset) < 0.0
            else int(acceptance["upper_c_extremum_count"])
        )
        sign_ok = (
            row["grazing"]["signed_y_clearance"] > 0.0
            if float(offset) < 0.0
            else row["grazing"]["signed_y_clearance"] < 0.0
        )
        return bool(
            _scientific_event_passes(row["event"])
            and row["extremum_partitioned"]["count"] == expected
            and row["barrio_success"]
            and row["barrio_count"] == int(acceptance["barrio_count"])
            and sign_ok
            and row["extremum_partitioned"]["maximum_section_residual"]
            <= float(acceptance["maximum_section_residual"])
        )

    for offset, row in zip(manifest["signed_c_offsets"], rows, strict=True):
        row["passed"] = row_passes(row, offset)
    control_summaries = []
    for control in controls:
        offset = control["offset"]
        reference = control["reference"]
        independent = control["independent"]
        control_summaries.append(
            {
                "offset": offset,
                "reference_count": reference["extremum_partitioned"]["count"],
                "independent_count": independent["extremum_partitioned"]["count"],
                "reference_barrio_count": reference["barrio_count"],
                "independent_barrio_count": independent["barrio_count"],
                "a_difference": abs(
                    float(reference["event"]["a"]) - float(independent["event"]["a"])
                ),
                "period_relative_difference": abs(
                    float(reference["event"]["period_time"])
                    - float(independent["event"]["period_time"])
                )
                / float(reference["event"]["period_time"]),
                "clearance_difference": abs(
                    float(reference["grazing"]["signed_y_clearance"])
                    - float(independent["grazing"]["signed_y_clearance"])
                ),
                "independent_scientific_event_passed": _scientific_event_passes(
                    independent["event"]
                ),
            }
        )
    passed = bool(
        all(row["passed"] for row in rows)
        and len(control_summaries) == int(acceptance["required_independent_controls"])
        and all(
            control["reference_count"] == control["independent_count"]
            and control["reference_barrio_count"] == control["independent_barrio_count"]
            and control["a_difference"] <= float(acceptance["maximum_solver_a_difference"])
            and control["period_relative_difference"]
            <= float(acceptance["maximum_solver_period_relative_difference"])
            and control["clearance_difference"]
            <= float(acceptance["maximum_solver_clearance_difference"])
            and control["independent_scientific_event_passed"]
            for control in control_summaries
        )
    )
    output = {
        "schema": "butterfly.jones-period6-flip-extremum-count-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "grazing_receipt_sha256": sha256_bytes(grazing_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "center_c": center_c,
        "rows": rows,
        "independent_controls": control_summaries,
        "standard_mismatch_count": sum(
            row["standard_historical_count"] != row["extremum_partitioned"]["count"]
            for row in rows
        ),
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": passed,
                "row_count": len(rows),
                "standard_mismatch_count": output["standard_mismatch_count"],
                "count_pairs": [
                    [
                        row["standard_historical_count"],
                        row["extremum_partitioned"]["count"],
                    ]
                    for row in rows
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
