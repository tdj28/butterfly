#!/usr/bin/env python3
"""Continue EXP-205's period-6 flip event as a fixed-b curve in (a,c)."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from types import SimpleNamespace
import time

import numpy as np
import scipy
from scipy.optimize import least_squares

from butterfly import (
    RosslerParameters,
    SolverConfig,
    augmented_flip_system,
    barrio_rossler_section,
    collect_crossings,
    flow_monodromy,
    legacy_rossler_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period6-flip-curve-manifest.v1"


def _dominant_and_neutral(multipliers):
    values = np.asarray(multipliers, dtype=np.complex128)
    neutral_index = int(np.argmin(np.abs(values - 1.0)))
    transverse = np.delete(values, neutral_index)
    dominant = complex(transverse[int(np.argmax(np.abs(transverse)))])
    return dominant, complex(values[neutral_index])


def _initial_tangent(parameters, state, period_time, solver):
    monodromy = flow_monodromy(parameters, state, period_time, config=solver)
    values, vectors = np.linalg.eig(monodromy.monodromy)
    index = int(np.argmin(np.abs(values + 1.0)))
    vector = vectors[:, index]
    if np.max(np.abs(vector.imag)) > 1e-7:
        raise RuntimeError("nearest flip eigenvector is not real")
    tangent = np.asarray(vector.real, dtype=float)
    tangent /= np.linalg.norm(tangent)
    return tangent


def _section_count(parameters, state, period_time, section, expected, solver):
    correction = SimpleNamespace(initial_state=state, period_time=period_time)
    crossings = collect_crossings(
        parameters,
        correction.initial_state,
        section,
        transient=0.0,
        observation_horizon=correction.period_time * (1.0 + 1e-7),
        max_crossings=expected + 6,
        config=solver,
    )
    keep = (crossings.times > correction.period_time * 1e-7) & (
        crossings.times <= correction.period_time * (1.0 + 1e-7)
    )
    return int(np.count_nonzero(keep)), bool(crossings.integration_success)


def _solve_event(c, seed, manifest, solver):
    fixed_b = float(manifest["fixed_b"])
    state = np.asarray(seed["initial_state"], dtype=float)
    period_time = float(seed["period_time"])
    seed_a = float(seed["a"])
    parameters = RosslerParameters(a=seed_a, b=fixed_b, c=float(c))
    tangent = np.asarray(seed.get("tangent", ()), dtype=float)
    if tangent.shape != (3,):
        tangent = _initial_tangent(parameters, state, period_time, solver)
    phase_reference = state.copy()
    phase = rossler_rhs(0.0, phase_reference, parameters)
    phase /= np.linalg.norm(phase)
    initial = np.r_[state, period_time, seed_a, tangent]
    a_guard = list(map(float, manifest["a_guard"]))
    lower = np.full(8, -np.inf)
    upper = np.full(8, np.inf)
    lower[3] = 1e-12
    lower[4], upper[4] = a_guard

    def evaluate(values):
        return augmented_flip_system(
            values,
            segment_count=1,
            a=None,
            c=float(c),
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
            continuation_parameter="a",
            fixed_b=fixed_b,
        )

    corrector = manifest["corrector"]
    solution = least_squares(
        lambda values: evaluate(values)[0],
        initial,
        jac=lambda values: evaluate(values)[1],
        bounds=(lower, upper),
        x_scale="jac",
        xtol=float(corrector["tolerance"]),
        ftol=float(corrector["tolerance"]),
        gtol=float(corrector["tolerance"]),
        max_nfev=int(corrector["maximum_evaluations"]),
    )
    residual, _ = evaluate(solution.x)
    state = np.asarray(solution.x[:3], dtype=float)
    period_time = float(solution.x[3])
    a = float(solution.x[4])
    tangent = np.asarray(solution.x[5:8], dtype=float)
    parameters = RosslerParameters(a=a, b=fixed_b, c=float(c))
    monodromy = flow_monodromy(parameters, state, period_time, config=solver)
    dominant, neutral = _dominant_and_neutral(monodromy.multipliers)
    acceptance = manifest["acceptance"]
    historical_count, historical_success = _section_count(
        parameters,
        state,
        period_time,
        legacy_rossler_section(parameters),
        int(acceptance["historical_phase_count"]),
        solver,
    )
    barrio_count, barrio_success = _section_count(
        parameters,
        state,
        period_time,
        barrio_rossler_section(parameters),
        int(acceptance["barrio_phase_count"]),
        solver,
    )
    checks = {
        "solver": bool(solution.success),
        "orbit": float(np.linalg.norm(residual[:3]))
        <= float(acceptance["maximum_orbit_residual"]),
        "phase": abs(float(residual[3]))
        <= float(acceptance["maximum_phase_residual"]),
        "tangent": float(np.linalg.norm(residual[4:7]))
        <= float(acceptance["maximum_tangent_residual"]),
        "normalization": abs(float(residual[7]))
        <= float(acceptance["maximum_normalization_residual"]),
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
        "a": a,
        "b": fixed_b,
        "c": float(c),
        "initial_state": state.tolist(),
        "period_time": period_time,
        "tangent": tangent.tolist(),
        "residuals": {
            "orbit": float(np.linalg.norm(residual[:3])),
            "phase": abs(float(residual[3])),
            "tangent": float(np.linalg.norm(residual[4:7])),
            "normalization": abs(float(residual[7])),
            "independent_multiplier": float(dominant.real + 1.0),
            "neutral_multiplier_error": float(abs(neutral - 1.0)),
        },
        "dominant_multiplier": {
            "real": float(dominant.real),
            "imag": float(dominant.imag),
            "modulus": float(abs(dominant)),
        },
        "historical_phase_count": historical_count,
        "barrio_phase_count": barrio_count,
        "evaluations": int(solution.nfev),
        "checks": checks,
        "passed": all(checks.values()),
        "message": str(solution.message),
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
        raise SystemExit("unsupported Jones period-6 flip-curve manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("flip-curve continuation requires clean source")
    source_receipt = json.loads(source_bytes)
    source_event = next(
        row for row in source_receipt["results"] if row["id"] == manifest["source_event_id"]
    )
    best = source_event["best_evaluation"]
    center_seed = {
        "a": best["a"],
        "initial_state": best["correction"]["initial_state"],
        "period_time": best["correction"]["period_time"],
    }
    solver = SolverConfig(**manifest["solver"])
    c_values = sorted(map(float, manifest["c_values"]))
    center_c = float(source_event["c"])
    if center_c not in c_values:
        raise SystemExit("source-event c is absent from the continuation grid")
    started = time.perf_counter()
    center = _solve_event(center_c, center_seed, manifest, solver)
    rows_by_c = {center_c: center}
    direction_status = {}
    for direction, targets in (
        ("down", sorted((c for c in c_values if c < center_c), reverse=True)),
        ("up", sorted(c for c in c_values if c > center_c)),
    ):
        previous = center
        completed = True
        message = "completed"
        for target_c in targets:
            try:
                row = _solve_event(target_c, previous, manifest, solver)
            except Exception as error:
                completed = False
                message = f"{type(error).__name__}: {error}"
                break
            rows_by_c[target_c] = row
            previous = row
            if not row["passed"]:
                completed = False
                message = "point failed acceptance checks"
                break
        direction_status[direction] = {"completed": completed, "message": message}
    rows = [rows_by_c[c] for c in c_values if c in rows_by_c]
    adjacent_a_jumps = [
        abs(float(right["a"]) - float(left["a"]))
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]
    acceptance = manifest["acceptance"]
    maximum_jump = max(adjacent_a_jumps, default=0.0)
    passed = bool(
        len(rows) == int(acceptance["required_points"])
        and all(row["passed"] for row in rows)
        and maximum_jump <= float(acceptance["maximum_adjacent_a_jump"])
        and all(status["completed"] for status in direction_status.values())
    )
    output = {
        "schema": "butterfly.jones-period6-flip-curve.v1",
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
        "rows": rows,
        "point_count": len(rows),
        "direction_status": direction_status,
        "c_range": [min(row["c"] for row in rows), max(row["c"] for row in rows)],
        "a_range": [min(row["a"] for row in rows), max(row["a"] for row in rows)],
        "maximum_adjacent_a_jump": maximum_jump,
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
                "point_count": len(rows),
                "c_range": output["c_range"],
                "a_range": output["a_range"],
                "maximum_adjacent_a_jump": maximum_jump,
                "direction_status": direction_status,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
