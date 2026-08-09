#!/usr/bin/env python3
"""Continue the first Jones-path period-2 child to its next real flip."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import (
    RosslerParameters,
    SolverConfig,
    correct_periodic_orbit,
    flow_monodromy,
    rossler_equilibria,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms


def _interpolate_branch(rows: list[dict], target_c: float) -> tuple[np.ndarray, float]:
    ordered = sorted(rows, key=lambda row: float(row["parameters"]["c"]))
    c_values = np.asarray([row["parameters"]["c"] for row in ordered], dtype=float)
    if not c_values[0] <= target_c <= c_values[-1]:
        raise ValueError("continuation start lies outside the source child branch")
    state = np.asarray(
        [
            np.interp(target_c, c_values, [row["initial_state"][index] for row in ordered])
            for index in range(3)
        ],
        dtype=float,
    )
    period = float(np.interp(target_c, c_values, [row["period_time"] for row in ordered]))
    return state, period


def _dominant_nontrivial(monodromy: object) -> complex:
    neutral = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    values = np.delete(monodromy.multipliers, neutral)
    return complex(values[int(np.argmax(np.abs(values)))])


def _half_period_closure(
    parameters: RosslerParameters,
    state: np.ndarray,
    period: float,
    solver: SolverConfig,
) -> float:
    result = solve_ivp(
        lambda time, current: rossler_rhs(time, current, parameters),
        (0.0, 0.5 * period),
        state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not result.success:
        raise RuntimeError(f"half-period integration failed: {result.message}")
    return float(np.linalg.norm(result.y[:, -1] - state))


def _winding(
    parameters: RosslerParameters,
    state: np.ndarray,
    period: float,
    solver: SolverConfig,
    samples: int,
) -> float:
    result = solve_ivp(
        lambda time, current: rossler_rhs(time, current, parameters),
        (0.0, period),
        state,
        t_eval=np.linspace(0.0, period, samples),
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not result.success:
        raise RuntimeError(f"winding integration failed: {result.message}")
    centered = result.y.T - rossler_equilibria(parameters)[0]
    angles = np.unwrap(np.arctan2(centered[:, 1], centered[:, 0]))
    return float((angles[-1] - angles[0]) / (2.0 * np.pi))


def first_real_minus_one_bracket(rows: list[dict], maximum_imaginary: float):
    for left, right in zip(rows[:-1], rows[1:], strict=True):
        left_multiplier = left["dominant_nontrivial_multiplier"]
        right_multiplier = right["dominant_nontrivial_multiplier"]
        if max(abs(left_multiplier["imag"]), abs(right_multiplier["imag"])) > maximum_imaginary:
            continue
        left_residual = float(left_multiplier["real"]) + 1.0
        right_residual = float(right_multiplier["real"]) + 1.0
        if left_residual == 0.0 or right_residual == 0.0 or left_residual * right_residual < 0.0:
            return {
                "c": [left["parameters"]["c"], right["parameters"]["c"]],
                "multipliers": [left_multiplier, right_multiplier],
                "residuals": [left_residual, right_residual],
            }
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period2-c-to-flip-manifest.v1":
        raise SystemExit("unsupported period-2 c continuation manifest")
    receipt_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(receipt_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    receipt = json.loads(receipt_bytes)
    branch = next(
        row
        for row in receipt["branches"]
        if int(row["direction"]) == int(manifest["source_direction"])
    )
    continuation = manifest["continuation"]
    c_values = np.linspace(
        float(continuation["start_c"]),
        float(continuation["end_c"]),
        int(continuation["maximum_points"]),
    )
    seed_state, seed_period = _interpolate_branch(branch["rows"], float(c_values[0]))
    a = float(manifest["fixed_a"])
    b = float(manifest["fixed_b"])
    solver = SolverConfig(**manifest["reference_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    corrector = manifest["corrector"]
    acceptance = manifest["acceptance"]
    rows = []
    independent_rows = []
    status_rows = []
    bracket = None
    bracket_index = None
    started = time.perf_counter()
    state = seed_state
    period = seed_period
    stride = int(manifest["independent_check_stride"])
    for index, c in enumerate(c_values):
        parameters = RosslerParameters(a=a, b=b, c=float(c))
        orbit = correct_periodic_orbit(
            parameters,
            state,
            period,
            config=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["maximum_evaluations"]),
        )
        status_rows.append(
            {
                "index": index,
                "c": float(c),
                "success": orbit.success,
                "message": orbit.message,
                "evaluations": orbit.evaluations,
                "correction_norm": orbit.correction_norm,
            }
        )
        if not orbit.success:
            break
        monodromy = flow_monodromy(
            parameters, orbit.initial_state, orbit.period_time, config=solver
        )
        neutral = monodromy.multipliers[
            int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
        ]
        dominant = _dominant_nontrivial(monodromy)
        row = {
            "index": index,
            "parameters": {"a": a, "b": b, "c": float(c)},
            "initial_state": orbit.initial_state.tolist(),
            "period_time": orbit.period_time,
            "closure_error": monodromy.closure_error,
            "phase_residual": orbit.phase_residual,
            "neutral_multiplier_error": float(abs(neutral - 1.0)),
            "dominant_nontrivial_multiplier": {
                "real": float(dominant.real),
                "imag": float(dominant.imag),
                "modulus": float(abs(dominant)),
            },
            "half_period_closure": _half_period_closure(
                parameters, orbit.initial_state, orbit.period_time, solver
            ),
            "winding_number": _winding(
                parameters,
                orbit.initial_state,
                orbit.period_time,
                solver,
                int(manifest["orbit_sample_count"]),
            ),
        }
        rows.append(row)
        state = orbit.initial_state
        period = orbit.period_time
        bracket = first_real_minus_one_bracket(
            rows, float(acceptance["maximum_bracket_multiplier_imaginary"])
        )
        if bracket is not None and bracket_index is None:
            bracket_index = index
        if index % stride == 0 or bracket_index == index:
            independent_orbit = correct_periodic_orbit(
                parameters,
                orbit.initial_state,
                orbit.period_time,
                config=independent_solver,
                tolerance=float(corrector["tolerance"]),
                max_evaluations=int(corrector["maximum_evaluations"]),
            )
            independent_monodromy = flow_monodromy(
                parameters,
                independent_orbit.initial_state,
                independent_orbit.period_time,
                config=independent_solver,
            )
            reference_dense = dense_orbit(orbit, parameters, solver)
            independent_dense = dense_orbit(
                independent_orbit, parameters, independent_solver
            )
            identity = phase_aligned_rms(
                (orbit, reference_dense),
                (independent_orbit, independent_dense),
                phase_samples=int(manifest["comparison"]["phase_samples"]),
                coarse_shifts=int(manifest["comparison"]["coarse_shifts"]),
                shift_tolerance=float(manifest["comparison"]["shift_tolerance"]),
            )
            independent_dominant = _dominant_nontrivial(independent_monodromy)
            independent_rows.append(
                {
                    "index": index,
                    "c": float(c),
                    "closure_error": independent_monodromy.closure_error,
                    "orbit_identity": identity,
                    "dominant_nontrivial_multiplier": {
                        "real": float(independent_dominant.real),
                        "imag": float(independent_dominant.imag),
                        "modulus": float(abs(independent_dominant)),
                    },
                    "reference_multiplier_difference": float(
                        abs(independent_dominant - dominant)
                    ),
                }
            )
        if bracket_index is not None and index >= bracket_index + int(
            continuation["post_bracket_points"]
        ):
            break
    passed = bool(
        len(rows) >= int(acceptance["minimum_points"])
        and bracket is not None
        and max(row["closure_error"] for row in rows)
        <= float(acceptance["maximum_closure_error"])
        and max(row["neutral_multiplier_error"] for row in rows)
        <= float(acceptance["maximum_neutral_multiplier_error"])
        and min(row["half_period_closure"] for row in rows)
        >= float(acceptance["minimum_half_period_closure"])
        and max(abs(row["winding_number"] - 2.0) for row in rows)
        <= float(acceptance["maximum_winding_error"])
        and len(independent_rows) >= int(acceptance["minimum_independent_checks"])
        and max(row["closure_error"] for row in independent_rows)
        <= float(acceptance["maximum_independent_closure_error"])
        and max(row["orbit_identity"]["rms"] for row in independent_rows)
        <= float(acceptance["maximum_independent_identity_rms"])
        and max(row["reference_multiplier_difference"] for row in independent_rows)
        <= float(acceptance["maximum_independent_multiplier_difference"])
    )
    output = {
        "schema": "butterfly.period2-c-to-flip-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(receipt_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "rows": rows,
        "statuses": status_rows,
        "independent_radau": independent_rows,
        "first_real_minus_one_bracket": bracket,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "scientific_scope": (
            "primitive period-2 continuation and first -1 bracket; not an exact "
            "period-2-to-4 event, switched child, or symbolic ordering"
        ),
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "passed": passed,
                "point_count": len(rows),
                "c_range": [rows[0]["parameters"]["c"], rows[-1]["parameters"]["c"]]
                if rows
                else None,
                "first_real_minus_one_bracket": bracket,
                "independent_check_count": len(independent_rows),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
