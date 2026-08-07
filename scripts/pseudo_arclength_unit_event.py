#!/usr/bin/env python3
"""Pseudo-arclength continuation of a coupled nontrivial-unit periodic event."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from butterfly import RosslerParameters, SolverConfig, rossler_jacobian, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def event_residual(
    variables: np.ndarray,
    *,
    c: float,
    reference_state: np.ndarray,
    phase_direction: np.ndarray,
    solver: SolverConfig,
) -> tuple[np.ndarray, np.ndarray]:
    state = variables[:3]
    duration = float(variables[3])
    a = float(variables[4])
    b = float(variables[5])
    event_vector = variables[6:9]
    parameters = RosslerParameters(a=a, b=b, c=c)
    initial = np.concatenate((state, np.eye(3, dtype=np.float64).ravel()))

    def augmented_rhs(time: float, augmented: np.ndarray) -> np.ndarray:
        current = augmented[:3]
        transition = augmented[3:12].reshape(3, 3)
        return np.concatenate(
            (
                rossler_rhs(time, current, parameters),
                (rossler_jacobian(current, parameters) @ transition).ravel(),
            )
        )

    integration = solve_ivp(
        augmented_rhs,
        (0.0, duration),
        initial,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not integration.success:
        raise RuntimeError(f"event integration failed: {integration.message}")
    final = np.asarray(integration.y[:, -1], dtype=np.float64)
    final_state = final[:3]
    monodromy = final[3:12].reshape(3, 3)
    local_flow = rossler_rhs(0.0, state, parameters)
    local_flow /= np.linalg.norm(local_flow)
    residual = np.concatenate(
        (
            final_state - state,
            (float(np.dot(phase_direction, state - reference_state)),),
            (monodromy - np.eye(3)) @ event_vector,
            (float(np.dot(event_vector, event_vector) - 1.0),),
            (float(np.dot(event_vector, local_flow)),),
        )
    )
    return residual, np.linalg.eigvals(monodromy).astype(np.complex128)


def correct_event_arclength(
    predictor: np.ndarray,
    tangent: np.ndarray,
    reference: np.ndarray,
    *,
    c: float,
    solver: SolverConfig,
    tolerance: float,
    max_evaluations: int,
) -> tuple[np.ndarray, dict]:
    reference_parameters = RosslerParameters(
        a=float(reference[4]), b=float(reference[5]), c=c
    )
    phase_direction = rossler_rhs(0.0, reference[:3], reference_parameters)
    phase_direction /= np.linalg.norm(phase_direction)
    cache_variables = None
    cache_residual = None
    cache_multipliers = None

    def evaluate(variables: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        nonlocal cache_variables, cache_residual, cache_multipliers
        if cache_variables is not None and np.array_equal(variables, cache_variables):
            return cache_residual, cache_multipliers
        base_residual, multipliers = event_residual(
            variables,
            c=c,
            reference_state=reference[:3],
            phase_direction=phase_direction,
            solver=solver,
        )
        residual = np.concatenate(
            (base_residual, (float(np.dot(tangent, variables - predictor)),))
        )
        cache_variables = variables.copy()
        cache_residual = residual
        cache_multipliers = multipliers
        return residual, multipliers

    lower = np.full(9, -np.inf)
    lower[3] = 1e-12
    solution = least_squares(
        lambda variables: evaluate(variables)[0],
        predictor,
        bounds=(lower, np.full(9, np.inf)),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, multipliers = evaluate(solution.x)
    status = {
        "success": bool(solution.success and np.linalg.norm(residual[:-1]) <= 1e-8),
        "message": str(solution.message),
        "evaluations": int(solution.nfev),
        "closure_error": float(np.linalg.norm(residual[:3])),
        "phase_residual": float(abs(residual[3])),
        "eigen_residual": float(np.linalg.norm(residual[4:7])),
        "normalization_residual": float(abs(residual[7])),
        "flow_orthogonality_residual": float(abs(residual[8])),
        "arclength_residual": float(abs(residual[9])),
        "multipliers": [
            {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
            for value in multipliers
        ],
    }
    return np.asarray(solution.x, dtype=float), status


def source_variables(row: dict) -> np.ndarray:
    return np.concatenate(
        (
            np.asarray(row["initial_state"], dtype=float),
            (float(row["period_time"]), float(row["a"]), float(row["b"])),
            np.asarray(row["event_eigenvector"], dtype=float),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-curve", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.unit-event-pseudo-arclength-manifest.v1":
        raise SystemExit("unsupported event pseudo-arclength manifest")
    source_bytes = args.source_curve.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_curve_receipt_sha256"]:
        raise SystemExit("source curve hash does not match manifest")
    source_curve = json.loads(source_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("event pseudo-arclength requires clean source")

    valid_rows = [row for row in source_curve["rows"] if row["solver_success"]]
    seeds = []
    for target_a in map(float, manifest["seed_a_values"]):
        row = min(valid_rows, key=lambda candidate: abs(candidate["a"] - target_a))
        if abs(row["a"] - target_a) > 1e-12:
            raise SystemExit(f"source seed a={target_a} is unavailable")
        seeds.append(source_variables(row))
    if np.dot(seeds[0][6:9], seeds[1][6:9]) < 0.0:
        seeds[1][6:9] *= -1.0
    points = [seeds[0], seeds[1]]
    solver = SolverConfig(**manifest["solver"])
    continuation = manifest["continuation"]
    corrector = manifest["corrector"]
    step_length = float(continuation["step_scale"]) * np.linalg.norm(seeds[1] - seeds[0])
    rows = []
    statuses = []
    started = time.perf_counter()
    for step_index in range(int(continuation["steps"])):
        tangent = points[-1] - points[-2]
        tangent /= np.linalg.norm(tangent)
        predictor = points[-1] + step_length * tangent
        corrected, status = correct_event_arclength(
            predictor,
            tangent,
            points[-1],
            c=float(manifest["fixed_c"]),
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )
        status["step_index"] = step_index
        statuses.append(status)
        if not status["success"]:
            break
        if np.dot(corrected[6:9], points[-1][6:9]) < 0.0:
            corrected[6:9] *= -1.0
        points.append(corrected)
        rows.append(
            {
                "initial_state": corrected[:3].tolist(),
                "period_time": float(corrected[3]),
                "a": float(corrected[4]),
                "b": float(corrected[5]),
                "event_eigenvector": corrected[6:9].tolist(),
                **status,
            }
        )
        a_guard = list(map(float, continuation["a_guard"]))
        b_guard = list(map(float, continuation["b_guard"]))
        if not (
            a_guard[0] <= corrected[4] <= a_guard[1]
            and b_guard[0] <= corrected[5] <= b_guard[1]
        ):
            break

    a_values = np.asarray([seed[4] for seed in seeds] + [row["a"] for row in rows])
    b_values = np.asarray([seed[5] for seed in seeds] + [row["b"] for row in rows])
    a_differences = np.diff(a_values)
    b_differences = np.diff(b_values)
    a_reversals = int(np.sum(a_differences[:-1] * a_differences[1:] < 0.0))
    b_reversals = int(np.sum(b_differences[:-1] * b_differences[1:] < 0.0))
    acceptance = manifest["acceptance"]
    max_closure = max((row["closure_error"] for row in rows), default=float("inf"))
    max_eigen = max((row["eigen_residual"] for row in rows), default=float("inf"))
    max_orthogonality = max(
        (row["flow_orthogonality_residual"] for row in rows), default=float("inf")
    )
    max_arclength = max(
        (row["arclength_residual"] for row in rows), default=float("inf")
    )
    passed = bool(
        len(rows) >= int(acceptance["minimum_corrected_points"])
        and float(np.min(a_values)) <= float(acceptance["required_minimum_a"])
        and max_closure <= float(acceptance["max_closure_error"])
        and max_eigen <= float(acceptance["max_eigen_residual"])
        and max_orthogonality
        <= float(acceptance["max_flow_orthogonality_residual"])
        and max_arclength <= float(acceptance["max_arclength_residual"])
    )
    receipt = {
        "schema": "butterfly.unit-event-pseudo-arclength-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_curve_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_c": float(manifest["fixed_c"]),
        "step_length": step_length,
        "seed_variables": [seed.tolist() for seed in seeds],
        "rows": rows,
        "statuses": statuses,
        "corrected_point_count": len(rows),
        "a_range": [float(np.min(a_values)), float(np.max(a_values))],
        "b_range": [float(np.min(b_values)), float(np.max(b_values))],
        "direction_reversals_in_a": a_reversals,
        "direction_reversals_in_b": b_reversals,
        "max_closure_error": max_closure,
        "max_eigen_residual": max_eigen,
        "max_flow_orthogonality_residual": max_orthogonality,
        "max_arclength_residual": max_arclength,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "A fixed-c pseudo-arclength event curve is not yet a c-dependent surface or a validated bifurcation set.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key not in ("rows", "statuses", "seed_variables")}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
