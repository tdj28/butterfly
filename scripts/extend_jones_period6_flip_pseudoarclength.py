#!/usr/bin/env python3
"""Extend the EXP-206 period-6 flip curve by dual-parameter pseudo-arclength."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import least_squares

from butterfly import RosslerParameters, SolverConfig, augmented_flip_system, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.continue_jones_period6_flip_curve import (
    _dominant_and_neutral,
    _section_count,
    _solve_event,
)
from butterfly import barrio_rossler_section, flow_monodromy, legacy_rossler_section


SCHEMA = "butterfly.jones-period6-flip-pseudoarclength-manifest.v1"


def combine_dual_jacobians(a_jacobian, c_jacobian):
    """Combine exact fixed-c/fixed-a Jacobians into an 8-by-9 (a,c) Jacobian."""

    combined = np.zeros((8, 9), dtype=float)
    combined[:, :5] = np.asarray(a_jacobian, dtype=float)[:, :5]
    combined[:, 5] = np.asarray(c_jacobian, dtype=float)[:, 4]
    combined[:, 6:] = np.asarray(a_jacobian, dtype=float)[:, 5:]
    return combined


def _variables(row):
    return np.r_[
        np.asarray(row["initial_state"], dtype=float),
        float(row["period_time"]),
        float(row["a"]),
        float(row["c"]),
        np.asarray(row["tangent"], dtype=float),
    ]


def _dual_system(values, phase, phase_reference, solver, fixed_b):
    state_time = np.asarray(values[:4], dtype=float)
    a_value = float(values[4])
    c_value = float(values[5])
    flip_tangent = np.asarray(values[6:9], dtype=float)
    a_variables = np.r_[state_time, a_value, flip_tangent]
    c_variables = np.r_[state_time, c_value, flip_tangent]
    a_residual, a_jacobian = augmented_flip_system(
        a_variables,
        segment_count=1,
        a=None,
        c=c_value,
        phase=phase,
        phase_reference=phase_reference,
        solver=solver,
        continuation_parameter="a",
        fixed_b=fixed_b,
    )
    c_residual, c_jacobian = augmented_flip_system(
        c_variables,
        segment_count=1,
        a=a_value,
        c=None,
        phase=phase,
        phase_reference=phase_reference,
        solver=solver,
        continuation_parameter="c",
        fixed_b=fixed_b,
    )
    if np.linalg.norm(a_residual - c_residual) > 1e-8:
        raise RuntimeError("dual exact residual evaluations disagree")
    return a_residual, combine_dual_jacobians(a_jacobian, c_jacobian)


def _correct(predictor, secant, reference, manifest, solver):
    fixed_b = float(manifest["fixed_b"])
    parameters = RosslerParameters(
        a=float(reference[4]), b=fixed_b, c=float(reference[5])
    )
    phase = rossler_rhs(0.0, reference[:3], parameters)
    phase /= np.linalg.norm(phase)
    corrector = manifest["corrector"]
    guards = manifest["continuation"]
    lower = np.full(9, -np.inf)
    upper = np.full(9, np.inf)
    lower[3] = 1e-12
    lower[4], upper[4] = map(float, guards["a_guard"])
    lower[5], upper[5] = map(float, guards["c_guard"])

    def evaluate(values):
        residual, jacobian = _dual_system(
            values, phase, reference[:3], solver, fixed_b
        )
        return (
            np.r_[residual, float(np.dot(secant, values - predictor))],
            np.vstack((jacobian, secant)),
        )

    solution = least_squares(
        lambda values: evaluate(values)[0],
        predictor,
        jac=lambda values: evaluate(values)[1],
        bounds=(lower, upper),
        x_scale="jac",
        xtol=float(corrector["tolerance"]),
        ftol=float(corrector["tolerance"]),
        gtol=float(corrector["tolerance"]),
        max_nfev=int(corrector["maximum_evaluations"]),
    )
    residual, _ = evaluate(solution.x)
    return np.asarray(solution.x, dtype=float), {
        "solver_success": bool(solution.success),
        "message": str(solution.message),
        "evaluations": int(solution.nfev),
        "orbit_residual": float(np.linalg.norm(residual[:3])),
        "phase_residual": float(abs(residual[3])),
        "tangent_residual": float(np.linalg.norm(residual[4:7])),
        "normalization_residual": float(abs(residual[7])),
        "arclength_residual": float(abs(residual[8])),
    }


def _diagnose(values, correction_status, manifest, solver):
    fixed_b = float(manifest["fixed_b"])
    parameters = RosslerParameters(
        a=float(values[4]), b=fixed_b, c=float(values[5])
    )
    monodromy = flow_monodromy(
        parameters, values[:3], float(values[3]), config=solver
    )
    dominant, neutral = _dominant_and_neutral(monodromy.multipliers)
    acceptance = manifest["acceptance"]
    historical_count, historical_success = _section_count(
        parameters,
        values[:3],
        float(values[3]),
        legacy_rossler_section(parameters),
        int(acceptance["historical_phase_count"]),
        solver,
    )
    barrio_count, barrio_success = _section_count(
        parameters,
        values[:3],
        float(values[3]),
        barrio_rossler_section(parameters),
        int(acceptance["barrio_phase_count"]),
        solver,
    )
    checks = {
        "solver": correction_status["solver_success"],
        "orbit": correction_status["orbit_residual"]
        <= float(acceptance["maximum_orbit_residual"]),
        "phase": correction_status["phase_residual"]
        <= float(acceptance["maximum_phase_residual"]),
        "tangent": correction_status["tangent_residual"]
        <= float(acceptance["maximum_tangent_residual"]),
        "normalization": correction_status["normalization_residual"]
        <= float(acceptance["maximum_normalization_residual"]),
        "arclength": correction_status["arclength_residual"]
        <= float(acceptance["maximum_arclength_residual"]),
        "independent_multiplier": abs(dominant.real + 1.0)
        <= float(acceptance["maximum_independent_multiplier_residual"]),
        "real_multiplier": abs(dominant.imag)
        <= float(acceptance["maximum_multiplier_imaginary_part"]),
        "neutral": abs(neutral - 1.0)
        <= float(acceptance["maximum_neutral_multiplier_error"]),
        "historical_section": historical_success
        and historical_count == int(acceptance["historical_phase_count"]),
        "barrio_section": barrio_success
        and barrio_count == int(acceptance["barrio_phase_count"]),
    }
    return {
        "initial_state": values[:3].tolist(),
        "period_time": float(values[3]),
        "a": float(values[4]),
        "b": fixed_b,
        "c": float(values[5]),
        "tangent": values[6:9].tolist(),
        **correction_status,
        "dominant_multiplier": {
            "real": float(dominant.real),
            "imag": float(dominant.imag),
            "modulus": float(abs(dominant)),
        },
        "neutral_multiplier_error": float(abs(neutral - 1.0)),
        "historical_phase_count": historical_count,
        "barrio_phase_count": barrio_count,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _independent_control(row, manifest, solver):
    seed = {
        "a": row["a"],
        "initial_state": row["initial_state"],
        "period_time": row["period_time"],
        "tangent": row["tangent"],
    }
    corrected = _solve_event(float(row["c"]), seed, manifest, solver)
    return {
        "row_passed": corrected["passed"],
        "a_difference": abs(float(corrected["a"]) - float(row["a"])),
        "period_relative_difference": abs(
            float(corrected["period_time"]) - float(row["period_time"])
        )
        / float(row["period_time"]),
        "state_difference": float(
            np.linalg.norm(
                np.asarray(corrected["initial_state"], dtype=float)
                - np.asarray(row["initial_state"], dtype=float)
            )
        ),
        "multiplier_modulus_difference": abs(
            float(corrected["dominant_multiplier"]["modulus"])
            - float(row["dominant_multiplier"]["modulus"])
        ),
        "corrected": corrected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported flip pseudo-arclength manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    if not source_receipt.get("passed"):
        raise SystemExit("source flip curve must have passed")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("flip pseudo-arclength continuation requires clean source")

    source_rows = sorted(source_receipt["rows"], key=lambda row: row["c"])
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    continuation = manifest["continuation"]
    started = time.perf_counter()
    directions = {}
    for name, seeds in (
        ("down", (source_rows[1], source_rows[0])),
        ("up", (source_rows[-2], source_rows[-1])),
    ):
        points = [_variables(seed) for seed in seeds]
        if np.dot(points[0][6:], points[1][6:]) < 0.0:
            points[0][6:] *= -1.0
        initial_distance = float(np.linalg.norm(points[1] - points[0]))
        step_length = float(continuation["step_scale"]) * initial_distance
        rows = []
        statuses = []
        message = "completed requested steps"
        for step_index in range(int(continuation["steps_per_direction"])):
            secant = points[-1] - points[-2]
            secant /= np.linalg.norm(secant)
            predictor = points[-1] + step_length * secant
            try:
                corrected, status = _correct(
                    predictor, secant, points[-1], manifest, solver
                )
            except Exception as error:
                message = f"{type(error).__name__}: {error}"
                break
            status["step_index"] = step_index
            statuses.append(status)
            row = _diagnose(corrected, status, manifest, solver)
            if not row["passed"]:
                message = "corrected point failed acceptance checks"
                break
            points.append(corrected)
            rows.append(row)
        directions[name] = {
            "step_length": step_length,
            "rows": rows,
            "statuses": statuses,
            "message": message,
        }

    all_new_rows = directions["down"]["rows"] + directions["up"]["rows"]
    controls = []
    for name in ("down", "up"):
        rows = directions[name]["rows"]
        if rows:
            controls.append(
                {
                    "direction": name,
                    **_independent_control(rows[-1], manifest, independent_solver),
                }
            )
    acceptance = manifest["acceptance"]
    c_values = [row["c"] for row in all_new_rows]
    a_jumps = []
    c_jumps = []
    for name in ("down", "up"):
        rows = directions[name]["rows"]
        a_jumps.extend(
            abs(right["a"] - left["a"])
            for left, right in zip(rows[:-1], rows[1:], strict=True)
        )
        c_jumps.extend(
            abs(right["c"] - left["c"])
            for left, right in zip(rows[:-1], rows[1:], strict=True)
        )
    maximum_a_jump = max(a_jumps, default=float("inf"))
    maximum_c_jump = max(c_jumps, default=float("inf"))
    passed = bool(
        c_values
        and all(
            len(directions[name]["rows"])
            == int(continuation["steps_per_direction"])
            for name in ("down", "up")
        )
        and min(c_values) <= float(acceptance["required_minimum_c"])
        and max(c_values) >= float(acceptance["required_maximum_c"])
        and maximum_a_jump <= float(acceptance["maximum_adjacent_a_jump"])
        and maximum_c_jump <= float(acceptance["maximum_adjacent_c_jump"])
        and len(controls) == 2
        and all(
            control["row_passed"]
            and control["a_difference"]
            <= float(acceptance["maximum_solver_a_difference"])
            and control["period_relative_difference"]
            <= float(acceptance["maximum_solver_period_relative_difference"])
            and control["state_difference"]
            <= float(acceptance["maximum_solver_state_difference"])
            and control["multiplier_modulus_difference"]
            <= float(acceptance["maximum_solver_modulus_difference"])
            for control in controls
        )
    )
    output = {
        "schema": "butterfly.jones-period6-flip-pseudoarclength-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "directions": directions,
        "new_point_count": len(all_new_rows),
        "c_range": [min(c_values), max(c_values)] if c_values else [None, None],
        "a_range": (
            [
                min(row["a"] for row in all_new_rows),
                max(row["a"] for row in all_new_rows),
            ]
            if all_new_rows
            else [None, None]
        ),
        "maximum_adjacent_a_jump": maximum_a_jump,
        "maximum_adjacent_c_jump": maximum_c_jump,
        "independent_controls": controls,
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
                "new_point_count": len(all_new_rows),
                "c_range": output["c_range"],
                "a_range": output["a_range"],
                "direction_messages": {
                    name: directions[name]["message"] for name in directions
                },
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
