#!/usr/bin/env python3
"""Trace a periodic-orbit branch through b turns with pseudo-arclength shooting."""

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

from butterfly import RosslerParameters, SolverConfig, flow_monodromy, rossler_jacobian, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def correct_arclength(
    predictor: np.ndarray,
    tangent: np.ndarray,
    reference_state: np.ndarray,
    reference_b: float,
    *,
    a: float,
    c: float,
    solver: SolverConfig,
    tolerance: float,
    max_evaluations: int,
) -> tuple[np.ndarray, dict]:
    phase_parameters = RosslerParameters(a=a, b=reference_b, c=c)
    phase_direction = rossler_rhs(0.0, reference_state, phase_parameters)
    phase_direction = phase_direction / np.linalg.norm(phase_direction)
    cache_variables = None
    cache_residual = None
    cache_jacobian = None

    def evaluate(variables: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        nonlocal cache_variables, cache_residual, cache_jacobian
        if cache_variables is not None and np.array_equal(variables, cache_variables):
            return cache_residual, cache_jacobian
        state = variables[:3]
        duration = float(variables[3])
        b = float(variables[4])
        parameters = RosslerParameters(a=a, b=b, c=c)
        initial = np.concatenate(
            (state, np.eye(3, dtype=np.float64).ravel(), np.zeros(3, dtype=np.float64))
        )

        def augmented_rhs(time: float, augmented: np.ndarray) -> np.ndarray:
            current = augmented[:3]
            jacobian = rossler_jacobian(current, parameters)
            transition = augmented[3:12].reshape(3, 3)
            sensitivity = augmented[12:15]
            return np.concatenate(
                (
                    rossler_rhs(time, current, parameters),
                    (jacobian @ transition).ravel(),
                    jacobian @ sensitivity + np.asarray((0.0, 0.0, 1.0)),
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
            raise RuntimeError(f"arclength integration failed: {integration.message}")
        final = np.asarray(integration.y[:, -1], dtype=np.float64)
        final_state = final[:3]
        transition = final[3:12].reshape(3, 3)
        sensitivity = final[12:15]
        residual = np.concatenate(
            (
                final_state - state,
                (float(np.dot(phase_direction, state - reference_state)),),
                (float(np.dot(tangent, variables - predictor)),),
            )
        )
        jacobian = np.empty((5, 5), dtype=np.float64)
        jacobian[:3, :3] = transition - np.eye(3)
        jacobian[:3, 3] = rossler_rhs(duration, final_state, parameters)
        jacobian[:3, 4] = sensitivity
        jacobian[3, :3] = phase_direction
        jacobian[3, 3:] = 0.0
        jacobian[4, :] = tangent
        cache_variables = variables.copy()
        cache_residual = residual
        cache_jacobian = jacobian
        return residual, jacobian

    solution = least_squares(
        lambda variables: evaluate(variables)[0],
        predictor,
        jac=lambda variables: evaluate(variables)[1],
        bounds=(
            np.asarray([-np.inf, -np.inf, -np.inf, 1e-12, -np.inf]),
            np.full(5, np.inf),
        ),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, _ = evaluate(solution.x)
    return np.asarray(solution.x), {
        "success": bool(solution.success and np.linalg.norm(residual[:3]) <= 1e-8),
        "message": str(solution.message),
        "evaluations": int(solution.nfev),
        "closure_error": float(np.linalg.norm(residual[:3])),
        "phase_residual": float(abs(residual[3])),
        "arclength_residual": float(abs(residual[4])),
    }


def diagnose(variables: np.ndarray, *, a: float, c: float, solver: SolverConfig) -> dict:
    state = variables[:3]
    duration = float(variables[3])
    b = float(variables[4])
    parameters = RosslerParameters(a=a, b=b, c=c)
    monodromy = flow_monodromy(parameters, state, duration, config=solver)
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    nontrivial = np.delete(monodromy.multipliers, neutral_index)
    significant = complex(nontrivial[int(np.argmax(np.abs(nontrivial)))])
    return {
        "a": a,
        "b": b,
        "c": c,
        "initial_state": state.tolist(),
        "period_time": duration,
        "closure_error": monodromy.closure_error,
        "neutral_multiplier_error": float(abs(monodromy.multipliers[neutral_index] - 1.0)),
        "significant_multiplier": {
            "real": float(significant.real),
            "imag": float(significant.imag),
            "modulus": float(abs(significant)),
        },
        "max_nontrivial_multiplier_modulus": float(np.max(np.abs(nontrivial))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--continuation-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.periodic-pseudo-arclength-manifest.v1":
        raise SystemExit("unsupported pseudo-arclength manifest")
    continuation_bytes = args.continuation_receipt.read_bytes()
    if sha256_bytes(continuation_bytes) != manifest["source_continuation_sha256"]:
        raise SystemExit("continuation receipt hash does not match manifest")
    continuation = json.loads(continuation_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("pseudo-arclength continuation requires clean source")
    family = next(
        row for row in continuation["families"] if row["id"] == manifest["family_id"]
    )
    seed_b_values = list(map(float, manifest["seed_b_values"]))
    seed_rows = [
        min(family["rows"], key=lambda row: abs(row["parameters"]["b"] - b))
        for b in seed_b_values
    ]
    if any(
        abs(row["parameters"]["b"] - b) > 1e-12
        for row, b in zip(seed_rows, seed_b_values, strict=True)
    ):
        raise RuntimeError("pseudo-arclength seeds are absent from source branch")
    points = [
        np.concatenate(
            (
                np.asarray(row["initial_state"], dtype=float),
                (float(row["period_time"]), float(row["parameters"]["b"])),
            )
        )
        for row in seed_rows
    ]
    solver = SolverConfig(**manifest["solver"])
    rows = [
        {**diagnose(point, a=family["fixed_a"], c=family["fixed_c"], solver=solver), "seed": True}
        for point in points
    ]
    statuses = []
    started = time.perf_counter()
    step_scale = float(manifest["continuation"]["step_scale"])
    for step_index in range(int(manifest["continuation"]["steps"])):
        tangent = points[-1] - points[-2]
        tangent = tangent / np.linalg.norm(tangent)
        step_length = step_scale * np.linalg.norm(points[-1] - points[-2])
        predictor = points[-1] + step_length * tangent
        corrected, status = correct_arclength(
            predictor,
            tangent,
            points[-1][:3],
            float(points[-1][4]),
            a=float(family["fixed_a"]),
            c=float(family["fixed_c"]),
            solver=solver,
            tolerance=float(manifest["corrector"]["tolerance"]),
            max_evaluations=int(manifest["corrector"]["max_evaluations"]),
        )
        status["step_index"] = step_index
        statuses.append(status)
        if not status["success"]:
            break
        points.append(corrected)
        row = diagnose(
            corrected, a=family["fixed_a"], c=family["fixed_c"], solver=solver
        )
        row["seed"] = False
        row["corrector"] = status
        rows.append(row)
        if not (
            float(manifest["continuation"]["b_guard_min"])
            <= corrected[4]
            <= float(manifest["continuation"]["b_guard_max"])
        ):
            break
    b_values = np.asarray([row["b"] for row in rows])
    differences = np.diff(b_values)
    direction_reversals = int(np.sum(differences[:-1] * differences[1:] < 0.0))
    receipt = {
        "schema": "butterfly.periodic-pseudo-arclength-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source_continuation_sha256": sha256_bytes(continuation_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "family_id": family["id"],
        "fixed_a": family["fixed_a"],
        "fixed_c": family["fixed_c"],
        "rows": rows,
        "statuses": statuses,
        "point_count": len(rows),
        "b_range": [float(np.min(b_values)), float(np.max(b_values))],
        "direction_reversals_in_b": direction_reversals,
        "max_closure_error": max(row["closure_error"] for row in rows),
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(
            len(rows) >= int(manifest["acceptance"]["minimum_points"])
            and max(row["closure_error"] for row in rows)
            <= float(manifest["acceptance"]["max_closure_error"])
        ),
        "interpretation_limit": (
            "Pseudo-arclength traces the periodic orbit branch through b turns; a "
            "coupled multiplier condition is still required for a certified fold point."
        ),
    }
    output_bytes = canonical_json(receipt)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": receipt["passed"],
                "point_count": receipt["point_count"],
                "b_range": receipt["b_range"],
                "direction_reversals_in_b": direction_reversals,
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
