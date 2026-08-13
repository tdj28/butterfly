#!/usr/bin/env python3
"""Switch period-12 branches from separated EXP-206 period-6 flip events."""

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
    barrio_rossler_section,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    integrate_flip_segment,
    legacy_rossler_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period6-flip-branch-switch-manifest.v1"


def _extended_a_jacobian(variables, *, b, c, phase_direction, solver):
    state = np.asarray(variables[:3], dtype=float)
    duration = float(variables[3])
    a = float(variables[4])
    parameters = RosslerParameters(a=a, b=float(b), c=float(c))
    endpoint, transition, sensitivity, *_ = integrate_flip_segment(
        state,
        np.zeros(3),
        duration,
        parameters,
        solver,
        continuation_parameter="a",
    )
    jacobian = np.empty((4, 5), dtype=float)
    jacobian[:3, :3] = transition - np.eye(3)
    jacobian[:3, 3] = rossler_rhs(duration, endpoint, parameters)
    jacobian[:3, 4] = sensitivity
    jacobian[3, :3] = phase_direction
    jacobian[3, 3:] = 0.0
    return endpoint, jacobian


def _correct_arclength(
    predictor,
    tangent,
    reference,
    *,
    b,
    c,
    a_guard,
    solver,
    corrector,
):
    phase_parameters = RosslerParameters(a=float(reference[4]), b=float(b), c=float(c))
    phase = rossler_rhs(0.0, np.asarray(reference[:3], dtype=float), phase_parameters)
    phase /= np.linalg.norm(phase)

    def evaluate(variables):
        endpoint, jacobian = _extended_a_jacobian(
            variables, b=b, c=c, phase_direction=phase, solver=solver
        )
        residual = np.r_[
            endpoint - variables[:3],
            np.dot(phase, variables[:3] - reference[:3]),
            np.dot(variables - predictor, tangent),
        ]
        full_jacobian = np.empty((5, 5), dtype=float)
        full_jacobian[:4] = jacobian
        full_jacobian[4] = tangent
        return residual, full_jacobian

    lower = np.full(5, -np.inf)
    upper = np.full(5, np.inf)
    lower[3] = 1e-12
    lower[4], upper[4] = a_guard
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
        "success": bool(solution.success and np.linalg.norm(residual[:4]) <= 1e-8),
        "evaluations": int(solution.nfev),
        "residual_norm": float(np.linalg.norm(residual)),
        "message": str(solution.message),
    }


def _section_count(parameters, state, period_time, section, expected, solver):
    correction = SimpleNamespace(initial_state=state, period_time=period_time)
    crossings = collect_crossings(
        parameters,
        correction.initial_state,
        section,
        transient=0.0,
        observation_horizon=correction.period_time * (1.0 + 1e-7),
        max_crossings=expected + 8,
        config=solver,
    )
    keep = (crossings.times > correction.period_time * 1e-7) & (
        crossings.times <= correction.period_time * (1.0 + 1e-7)
    )
    return int(np.count_nonzero(keep)), bool(crossings.integration_success)


def _diagnose(variables, *, b, c, solver, acceptance):
    state = np.asarray(variables[:3], dtype=float)
    period_time = float(variables[3])
    a = float(variables[4])
    parameters = RosslerParameters(a=a, b=float(b), c=float(c))
    monodromy = flow_monodromy(parameters, state, period_time, config=solver)
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    transverse = np.delete(monodromy.multipliers, neutral_index)
    dominant = complex(transverse[int(np.argmax(np.abs(transverse)))])
    historical_count, historical_success = _section_count(
        parameters,
        state,
        period_time,
        legacy_rossler_section(parameters),
        int(acceptance["historical_child_phase_count"]),
        solver,
    )
    barrio_count, barrio_success = _section_count(
        parameters,
        state,
        period_time,
        barrio_rossler_section(parameters),
        int(acceptance["barrio_child_phase_count"]),
        solver,
    )
    return {
        "a": a,
        "b": float(b),
        "c": float(c),
        "initial_state": state.tolist(),
        "period_time": period_time,
        "closure_error": monodromy.closure_error,
        "dominant_multiplier": {
            "real": float(dominant.real),
            "imag": float(dominant.imag),
            "modulus": float(abs(dominant)),
        },
        "neutral_multiplier_error": float(abs(monodromy.multipliers[neutral_index] - 1.0)),
        "historical_phase_count": historical_count,
        "barrio_phase_count": barrio_count,
        "historical_integration_success": historical_success,
        "barrio_integration_success": barrio_success,
    }


def _parent_variables(event, a, *, b, c, solver, corrector):
    parameters = RosslerParameters(a=float(a), b=float(b), c=float(c))
    correction = correct_periodic_orbit(
        parameters,
        event["initial_state"],
        float(event["period_time"]),
        config=solver,
        max_evaluations=int(corrector["maximum_evaluations"]),
        tolerance=float(corrector["tolerance"]),
    )
    if not correction.success:
        raise RuntimeError("primary period-6 correction failed")
    return np.r_[correction.initial_state, 2.0 * correction.period_time, float(a)]


def _primary_distance(variables, primary_rows):
    ordered = sorted(primary_rows, key=lambda row: float(row[4]))
    a_values = np.asarray([row[4] for row in ordered], dtype=float)
    primary = np.empty(5, dtype=float)
    for index in range(4):
        primary[index] = np.interp(
            variables[4], a_values, [row[index] for row in ordered]
        )
    primary[4] = variables[4]
    return float(np.linalg.norm(variables - primary))


def _switch_event(event, manifest, solver):
    b = float(manifest["fixed_b"])
    c = float(event["c"])
    event_a = float(event["a"])
    event_variables = np.r_[
        event["initial_state"], 2.0 * float(event["period_time"]), event_a
    ]
    parameters = RosslerParameters(a=event_a, b=b, c=c)
    phase = rossler_rhs(0.0, event_variables[:3], parameters)
    phase /= np.linalg.norm(phase)
    _, jacobian = _extended_a_jacobian(
        event_variables, b=b, c=c, phase_direction=phase, solver=solver
    )
    _, singular_values, right_vectors = np.linalg.svd(jacobian, full_matrices=True)
    null_basis = right_vectors[-2:].T
    primary_offset = float(manifest["primary_a_offset"])
    primary_rows = [
        _parent_variables(
            event,
            event_a + offset,
            b=b,
            c=c,
            solver=solver,
            corrector=manifest["corrector"],
        )
        for offset in (-primary_offset, 0.0, primary_offset)
    ]
    observed_primary = primary_rows[-1] - primary_rows[0]
    observed_primary /= np.linalg.norm(observed_primary)
    primary_tangent = null_basis @ (null_basis.T @ observed_primary)
    primary_tangent /= np.linalg.norm(primary_tangent)
    secondary_tangent = null_basis[:, 0] - primary_tangent * float(
        np.dot(primary_tangent, null_basis[:, 0])
    )
    if np.linalg.norm(secondary_tangent) < 1e-8:
        secondary_tangent = null_basis[:, 1] - primary_tangent * float(
            np.dot(primary_tangent, null_basis[:, 1])
        )
    secondary_tangent /= np.linalg.norm(secondary_tangent)

    continuation = manifest["continuation"]
    a_guard = [
        event_a + float(continuation["a_guard_offsets"][0]),
        event_a + float(continuation["a_guard_offsets"][1]),
    ]
    branches = []
    for direction in (-1, 1):
        tangent = direction * secondary_tangent
        predictor = event_variables + float(continuation["step_length"]) * tangent
        corrected, status = _correct_arclength(
            predictor,
            tangent,
            event_variables,
            b=b,
            c=c,
            a_guard=a_guard,
            solver=solver,
            corrector=manifest["corrector"],
        )
        points = [event_variables]
        rows = []
        statuses = [status]
        if status["success"]:
            points.append(corrected)
            rows.append(
                _diagnose(
                    corrected,
                    b=b,
                    c=c,
                    solver=solver,
                    acceptance=manifest["acceptance"],
                )
            )
        for _ in range(1, int(continuation["steps_per_direction"])):
            if len(points) < 2:
                break
            tangent = points[-1] - points[-2]
            tangent /= np.linalg.norm(tangent)
            predictor = points[-1] + float(continuation["step_length"]) * tangent
            corrected, status = _correct_arclength(
                predictor,
                tangent,
                points[-1],
                b=b,
                c=c,
                a_guard=a_guard,
                solver=solver,
                corrector=manifest["corrector"],
            )
            statuses.append(status)
            if not status["success"]:
                break
            points.append(corrected)
            rows.append(
                _diagnose(
                    corrected,
                    b=b,
                    c=c,
                    solver=solver,
                    acceptance=manifest["acceptance"],
                )
            )
        branches.append(
            {
                "direction": direction,
                "point_count": len(rows),
                "rows": rows,
                "statuses": statuses,
                "endpoint_distance_from_doubled_primary": _primary_distance(
                    points[-1], primary_rows
                ),
                "maximum_a_separation": max(
                    (abs(row["a"] - event_a) for row in rows), default=0.0
                ),
            }
        )
    acceptance = manifest["acceptance"]
    all_rows = [row for branch in branches for row in branch["rows"]]
    passed = bool(
        singular_values[-1] <= float(acceptance["maximum_small_singular_value"])
        and abs(float(np.dot(primary_tangent, secondary_tangent)))
        <= float(acceptance["maximum_tangent_dot"])
        and all(
            branch["point_count"] >= int(acceptance["minimum_points_per_direction"])
            and branch["endpoint_distance_from_doubled_primary"]
            >= float(acceptance["minimum_endpoint_distance"])
            and branch["maximum_a_separation"]
            >= float(acceptance["minimum_a_separation"])
            for branch in branches
        )
        and all(
            row["closure_error"] <= float(acceptance["maximum_closure_error"])
            and row["historical_phase_count"]
            == int(acceptance["historical_child_phase_count"])
            and row["barrio_phase_count"]
            == int(acceptance["barrio_child_phase_count"])
            and row["historical_integration_success"]
            and row["barrio_integration_success"]
            for row in all_rows
        )
    )
    return {
        "c": c,
        "event_a": event_a,
        "event_variables": event_variables.tolist(),
        "shooting_singular_values": singular_values.tolist(),
        "primary_tangent": primary_tangent.tolist(),
        "secondary_tangent": secondary_tangent.tolist(),
        "absolute_tangent_dot": abs(float(np.dot(primary_tangent, secondary_tangent))),
        "primary_rows": [row.tolist() for row in primary_rows],
        "branches": branches,
        "passed": passed,
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
        raise SystemExit("unsupported Jones period-6 branch-switch manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("period-6 branch switching requires clean source")
    receipt = json.loads(source_bytes)
    lookup = {float(row["c"]): row for row in receipt["rows"]}
    solver = SolverConfig(**manifest["solver"])
    started = time.perf_counter()
    events = [
        _switch_event(lookup[float(c)], manifest, solver)
        for c in manifest["event_c_values"]
    ]
    passed = bool(
        len(events) == int(manifest["acceptance"]["required_events"])
        and all(event["passed"] for event in events)
    )
    output = {
        "schema": "butterfly.jones-period6-flip-branch-switch.v1",
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
        "events": events,
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
                "events": [
                    {
                        "c": event["c"],
                        "passed": event["passed"],
                        "branches": [
                            {
                                "direction": branch["direction"],
                                "points": branch["point_count"],
                                "distance": branch["endpoint_distance_from_doubled_primary"],
                                "a_separation": branch["maximum_a_separation"],
                            }
                            for branch in event["branches"]
                        ],
                    }
                    for event in events
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
