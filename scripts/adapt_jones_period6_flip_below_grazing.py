#!/usr/bin/env python3
"""Adaptively continue the period-6 flip locus below the section grazing."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.continue_jones_period6_flip_curve import _solve_event
from scripts.continue_jones_period6_flip_through_grazing import (
    _extremum_count,
    _invariant_row_passes,
)
from scripts.extend_jones_period6_flip_pseudoarclength import (
    _correct,
    _diagnose,
    _variables,
)
from scripts.refine_jones_period6_flip_section_grazing import (
    _scientific_event_passes,
)


SCHEMA = "butterfly.jones-period6-flip-adaptive-below-grazing-manifest.v1"
RETURNING_SCHEMA = "butterfly.jones-period6-flip-returning-arm-manifest.v1"


def terminal_target_reached(row, acceptance, continuation):
    """Evaluate the declared terminal direction without assuming monotone c."""

    direction = continuation.get("terminal_direction", "decreasing")
    if direction == "decreasing":
        return row["c"] <= float(acceptance["required_maximum_terminal_c"])
    if direction == "increasing":
        return row["c"] >= float(acceptance["required_minimum_terminal_c"])
    raise ValueError(f"unsupported terminal_direction: {direction}")


def correction_status_passes(status, acceptance):
    """Return whether a corrector solved the exact augmented event system."""

    return bool(
        status["solver_success"]
        and status["orbit_residual"] <= float(acceptance["maximum_orbit_residual"])
        and status["phase_residual"] <= float(acceptance["maximum_phase_residual"])
        and status["tangent_residual"]
        <= float(acceptance["maximum_tangent_residual"])
        and status["normalization_residual"]
        <= float(acceptance["maximum_normalization_residual"])
        and status["arclength_residual"]
        <= float(acceptance["maximum_arclength_residual"])
    )


def adaptive_step_after_success(step, evaluations, easy_streak, continuation):
    """Apply the prospectively frozen shrink/growth policy after acceptance."""

    if evaluations >= int(continuation["hard_evaluations"]):
        return (
            max(
                float(continuation["minimum_step_length"]),
                step * float(continuation["shrink_factor"]),
            ),
            0,
        )
    if evaluations <= int(continuation["easy_evaluations"]):
        easy_streak += 1
        if easy_streak >= int(continuation["growth_after_easy_steps"]):
            return (
                min(
                    float(continuation["maximum_step_length"]),
                    step * float(continuation["growth_factor"]),
                ),
                0,
            )
        return step, easy_streak
    return step, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in {SCHEMA, RETURNING_SCHEMA}:
        raise SystemExit("unsupported adaptive below-grazing manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    if source_receipt.get("passed") or int(source_receipt.get("point_count", 0)) < 2:
        raise SystemExit("source must be a retained multi-point continuation failure")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("adaptive continuation requires clean source")

    source_rows = source_receipt["rows"]
    points = [_variables(row) for row in source_rows[-2:]]
    if np.dot(points[0][6:], points[1][6:]) < 0.0:
        points[0][6:] *= -1.0
    continuation = manifest["continuation"]
    acceptance = manifest["acceptance"]
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    step_length = float(continuation["initial_step_scale"]) * float(
        np.linalg.norm(points[1] - points[0])
    )
    step_length = min(step_length, float(continuation["maximum_step_length"]))
    initial_step_length = step_length
    rows = []
    attempts = []
    accepted_steps = []
    message = "maximum accepted-point budget exhausted"
    target_reached = False
    easy_streak = 0
    started = time.perf_counter()

    for accepted_index in range(int(continuation["maximum_accepted_points"])):
        secant = points[-1] - points[-2]
        secant /= np.linalg.norm(secant)
        accepted = False
        for retry_index in range(int(continuation["maximum_retries"]) + 1):
            predictor = points[-1] + step_length * secant
            try:
                corrected, status = _correct(
                    predictor, secant, points[-1], manifest, solver
                )
            except Exception as error:
                attempts.append(
                    {
                        "accepted_index": accepted_index,
                        "retry_index": retry_index,
                        "step_length": step_length,
                        "accepted": False,
                        "error": f"{type(error).__name__}: {error}",
                    }
                )
                status = None
            if status is not None:
                attempt = {
                    **status,
                    "accepted_index": accepted_index,
                    "retry_index": retry_index,
                    "step_length": step_length,
                    "candidate_a": float(corrected[4]),
                    "candidate_c": float(corrected[5]),
                    "accepted": False,
                }
                if correction_status_passes(status, acceptance):
                    try:
                        row = _diagnose(corrected, status, manifest, solver)
                        row["extremum_partitioned"] = _extremum_count(row, solver)
                        row["invariant_passed"] = _invariant_row_passes(row)
                        row["jump_passed"] = bool(
                            abs(row["a"] - source_rows[-1]["a"])
                            <= float(acceptance["maximum_adjacent_a_jump"])
                            and abs(row["c"] - source_rows[-1]["c"])
                            <= float(acceptance["maximum_adjacent_c_jump"])
                        ) if not rows else bool(
                            abs(row["a"] - rows[-1]["a"])
                            <= float(acceptance["maximum_adjacent_a_jump"])
                            and abs(row["c"] - rows[-1]["c"])
                            <= float(acceptance["maximum_adjacent_c_jump"])
                        )
                        row["passed"] = bool(
                            row["invariant_passed"]
                            and row["jump_passed"]
                            and row["barrio_phase_count"]
                            == int(acceptance["barrio_phase_count"])
                            and row["extremum_partitioned"]["count"]
                            == int(acceptance["historical_extremum_count"])
                            and row["extremum_partitioned"][
                                "maximum_section_residual"
                            ]
                            <= float(acceptance["maximum_section_residual"])
                        )
                    except Exception as error:
                        attempt["diagnostic_error"] = f"{type(error).__name__}: {error}"
                        row = None
                    if row is not None and row["passed"]:
                        attempt["accepted"] = True
                        attempts.append(attempt)
                        points.append(corrected)
                        rows.append(row)
                        accepted_steps.append(step_length)
                        step_length, easy_streak = adaptive_step_after_success(
                            step_length,
                            int(status["evaluations"]),
                            easy_streak,
                            continuation,
                        )
                        accepted = True
                        break
                    if row is not None:
                        attempt["failed_checks"] = [
                            name for name, value in row["checks"].items() if not value
                        ]
                        attempt["invariant_passed"] = row["invariant_passed"]
                        attempt["jump_passed"] = row["jump_passed"]
                        attempt["historical_extremum_count"] = row[
                            "extremum_partitioned"
                        ]["count"]
                        attempt["barrio_phase_count"] = row["barrio_phase_count"]
                attempts.append(attempt)
            step_length *= float(continuation["shrink_factor"])
            easy_streak = 0
            if step_length < float(continuation["minimum_step_length"]):
                message = "minimum adaptive step exhausted"
                break
        if not accepted:
            if message != "minimum adaptive step exhausted":
                message = "maximum retry budget exhausted"
            break
        if (
            len(rows) >= int(continuation["minimum_accepted_points"])
            and terminal_target_reached(rows[-1], acceptance, continuation)
        ):
            target_reached = True
            message = "terminal c target reached"
            break

    independent = None
    if rows:
        terminal = rows[-1]
        corrected = _solve_event(
            terminal["c"],
            {
                "a": terminal["a"],
                "initial_state": terminal["initial_state"],
                "period_time": terminal["period_time"],
                "tangent": terminal["tangent"],
            },
            manifest,
            independent_solver,
        )
        corrected["extremum_partitioned"] = _extremum_count(
            {
                "a": corrected["a"],
                "b": corrected["b"],
                "c": corrected["c"],
                "initial_state": corrected["initial_state"],
                "period_time": corrected["period_time"],
            },
            independent_solver,
        )
        independent = {
            "corrected": corrected,
            "scientific_event_passed": _scientific_event_passes(corrected),
            "a_difference": abs(corrected["a"] - terminal["a"]),
            "period_relative_difference": abs(
                corrected["period_time"] - terminal["period_time"]
            ) / terminal["period_time"],
            "state_difference": float(
                np.linalg.norm(
                    np.asarray(corrected["initial_state"], dtype=float)
                    - np.asarray(terminal["initial_state"], dtype=float)
                )
            ),
            "multiplier_modulus_difference": abs(
                corrected["dominant_multiplier"]["modulus"]
                - terminal["dominant_multiplier"]["modulus"]
            ),
        }

    c_differences = np.diff(
        [source_rows[-2]["c"], source_rows[-1]["c"]]
        + [row["c"] for row in rows]
    )
    c_reversals = int(
        np.sum(c_differences[1:] * c_differences[:-1] < 0.0)
    ) if len(c_differences) >= 2 else 0
    independent_passed = bool(
        independent is not None
        and independent["scientific_event_passed"]
        and independent["corrected"]["barrio_phase_count"]
        == int(acceptance["barrio_phase_count"])
        and independent["corrected"]["extremum_partitioned"]["count"]
        == int(acceptance["historical_extremum_count"])
        and independent["a_difference"]
        <= float(acceptance["maximum_solver_a_difference"])
        and independent["period_relative_difference"]
        <= float(acceptance["maximum_solver_period_relative_difference"])
        and independent["state_difference"]
        <= float(acceptance["maximum_solver_state_difference"])
        and independent["multiplier_modulus_difference"]
        <= float(acceptance["maximum_solver_modulus_difference"])
    )
    passed = bool(
        target_reached
        and len(rows) >= int(continuation["minimum_accepted_points"])
        and all(row["passed"] for row in rows)
        and independent_passed
    )
    output = {
        "schema": manifest.get(
            "receipt_schema",
            "butterfly.jones-period6-flip-adaptive-below-grazing-receipt.v1",
        ),
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
        "initial_step_length": initial_step_length,
        "accepted_step_lengths": accepted_steps,
        "rows": rows,
        "attempts": attempts,
        "message": message,
        "target_reached": target_reached,
        "point_count": len(rows),
        "c_range": [min(row["c"] for row in rows), max(row["c"] for row in rows)]
        if rows else [None, None],
        "a_range": [min(row["a"] for row in rows), max(row["a"] for row in rows)]
        if rows else [None, None],
        "c_projection_reversals": c_reversals,
        "independent_radau": independent,
        "independent_passed": independent_passed,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(json.dumps({
        "output": str(args.output),
        "sha256": sha256_bytes(output_bytes),
        "passed": passed,
        "point_count": len(rows),
        "c_range": output["c_range"],
        "a_range": output["a_range"],
        "c_projection_reversals": c_reversals,
        "message": message,
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
