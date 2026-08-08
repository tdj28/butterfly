#!/usr/bin/env python3
"""Continue primitive PIM-seeded UPOs across the local a bracket."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from audit_pim_upo_primitivity import (
    _continuous_phase_invariant_rms,
    _normalized_orbit,
    _proper_repeat_factors,
)
from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _source_recovery(receipt, case_id, recovery_index):
    case = next(row for row in receipt["cases"] if row["id"] == case_id)
    recovery = case["recoveries"][recovery_index]
    if not recovery["accepted"]:
        raise ValueError("declared source recovery is not accepted")
    return case, recovery


def _complex_rows(values):
    return [
        {
            "real": float(value.real),
            "imag": float(value.imag),
            "modulus": float(abs(value)),
        }
        for value in values
    ]


def _crossing_count(
    parameters,
    state,
    period,
    solver,
    maximum_crossings,
    *,
    phase_fraction=0.0,
):
    if not 0.0 <= phase_fraction < 1.0:
        raise ValueError("phase_fraction must lie in [0,1)")
    section = barrio_rossler_section(parameters)
    window_start = period * phase_fraction
    crossings = collect_crossings(
        parameters,
        state,
        section,
        transient=window_start,
        observation_horizon=period * (1.0 + 1e-8),
        max_crossings=maximum_crossings,
        config=solver,
    )
    keep = (crossings.times > window_start + period * 1e-7) & (
        crossings.times <= window_start + period * (1.0 + 1e-8)
    )
    return int(np.count_nonzero(keep)), bool(crossings.integration_success)


def _audit_orbit(
    parameters,
    state,
    period,
    lag,
    solver,
    acceptance,
    section_count_policy,
):
    monodromy = flow_monodromy(parameters, state, period, config=solver)
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    nontrivial = np.delete(monodromy.multipliers, neutral_index)
    crossings, crossing_success = _crossing_count(
        parameters,
        state,
        period,
        solver,
        lag + 4,
        phase_fraction=float(section_count_policy.get("phase_fraction", 0.0)),
    )
    divisor_rows = []
    for repeat_factor in _proper_repeat_factors(lag):
        candidate = flow_monodromy(
            parameters, state, period / repeat_factor, config=solver
        )
        divisor_rows.append(
            {
                "repeat_factor": repeat_factor,
                "candidate_lag": lag // repeat_factor,
                "closure_error": candidate.closure_error,
            }
        )
    minimum_divisor_closure = min(
        (row["closure_error"] for row in divisor_rows), default=float("inf")
    )
    neutral_error = float(abs(monodromy.multipliers[neutral_index] - 1.0))
    maximum_transverse = float(np.max(np.abs(nontrivial)))
    checks = {
        "monodromy_integration": monodromy.success,
        "flow_closure": monodromy.closure_error
        <= float(acceptance["maximum_flow_closure"]),
        "neutral_multiplier": neutral_error
        <= float(acceptance["maximum_neutral_multiplier_error"]),
        "primitive_identity": minimum_divisor_closure
        >= float(acceptance["minimum_proper_divisor_closure"]),
        "transverse_instability": maximum_transverse
        >= 1.0 + float(acceptance["minimum_instability_margin"]),
    }
    if bool(section_count_policy.get("gate", True)):
        checks["crossing_identity"] = crossing_success and crossings == int(
            section_count_policy.get("expected_crossings", lag)
        )
    return {
        "flow_closure_error": monodromy.closure_error,
        "multipliers": _complex_rows(monodromy.multipliers),
        "neutral_multiplier_error": neutral_error,
        "maximum_nontrivial_multiplier_modulus": maximum_transverse,
        "one_period_section_crossing_count": crossings,
        "section_count_integration_success": crossing_success,
        "section_count_window_start_fraction": float(
            section_count_policy.get("phase_fraction", 0.0)
        ),
        "minimum_proper_divisor_closure": minimum_divisor_closure,
        "proper_divisor_tests": divisor_rows,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _continuation_values(start, stop, step):
    direction = 1.0 if stop >= start else -1.0
    count = int(round(abs(stop - start) / step))
    values = [start + direction * step * index for index in range(count + 1)]
    values[-1] = stop
    return values


def _parameter_match(values, target, tolerance):
    errors = [abs(float(value) - float(target)) for value in values]
    maximum_error = max(errors, default=float("inf"))
    return bool(maximum_error <= float(tolerance)), float(maximum_error)


def _run_branch(branch, source_receipt, manifest, solver):
    source_case, recovery = _source_recovery(
        source_receipt,
        branch["source_case_id"],
        int(branch["source_recovery_index"]),
    )
    lag = int(branch["fundamental_lag"])
    state = np.asarray(recovery["correction"]["initial_state"], dtype=float)
    period = float(recovery["correction"]["period_time"])
    b = float(source_case["parameters"]["b"])
    c = float(source_case["parameters"]["c"])
    rows = []
    failure = None
    for index, a in enumerate(
        _continuation_values(
            float(branch["a_start"]),
            float(branch["a_stop"]),
            float(branch["a_step"]),
        )
    ):
        parameters = RosslerParameters(a=float(a), b=b, c=c)
        if index:
            correction = correct_periodic_orbit(
                parameters,
                state,
                period,
                config=solver,
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
                tolerance=float(manifest["corrector"]["tolerance"]),
            )
            if not correction.success:
                failure = {
                    "a": float(a),
                    "reason": "periodic correction failed",
                    "message": correction.message,
                    "closure_error": correction.closure_error,
                }
                break
            state = correction.initial_state
            period = correction.period_time
            correction_row = {
                "closure_error": correction.closure_error,
                "phase_residual": correction.phase_residual,
                "correction_norm": correction.correction_norm,
                "evaluations": correction.evaluations,
            }
        else:
            correction_row = {
                "closure_error": float(recovery["correction"]["closure_error"]),
                "phase_residual": float(recovery["correction"]["phase_residual"]),
                "correction_norm": 0.0,
                "evaluations": 0,
            }
        audit = _audit_orbit(
            parameters,
            state,
            period,
            lag,
            solver,
            manifest["acceptance"],
            manifest.get("section_count", {}),
        )
        row = {
            "a": float(a),
            "b": b,
            "c": c,
            "fundamental_lag": lag,
            "initial_state": state.tolist(),
            "period_time": period,
            "correction": correction_row,
            "audit": audit,
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "branch": branch["id"],
                    "a": a,
                    "lag": lag,
                    "period": period,
                    "passed": audit["passed"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        if not audit["passed"]:
            failure = {"a": float(a), "reason": "orbit identity audit failed"}
            break
    return {
        "id": branch["id"],
        "fundamental_lag": lag,
        "source_case_id": branch["source_case_id"],
        "source_recovery_index": int(branch["source_recovery_index"]),
        "rows": rows,
        "failure": failure,
        "reached_target": bool(rows and rows[-1]["a"] == float(branch["a_stop"])),
        "passed": failure is None
        and bool(rows)
        and rows[-1]["a"] == float(branch["a_stop"]),
    }


def _shared_identity(branches, manifest, solver):
    declared = manifest["shared_family_identity"]
    left = next(
        branch for branch in branches if branch["id"] == declared["left_branch_id"]
    )
    right = next(
        branch for branch in branches if branch["id"] == declared["right_branch_id"]
    )
    target_a = float(declared["comparison_a"])
    left_row = min(left["rows"], key=lambda row: abs(row["a"] - target_a))
    right_row = min(right["rows"], key=lambda row: abs(row["a"] - target_a))
    exact_parameter_match = left_row["a"] == target_a and right_row["a"] == target_a
    parameter_match, maximum_parameter_error = _parameter_match(
        (left_row["a"], right_row["a"]),
        target_a,
        float(declared.get("parameter_match_tolerance", 0.0)),
    )
    period_scale = max(left_row["period_time"], right_row["period_time"])
    relative_period = (
        abs(left_row["period_time"] - right_row["period_time"]) / period_scale
    )
    parameters = RosslerParameters(a=target_a, b=left_row["b"], c=left_row["c"])
    scales = np.asarray(declared["coordinate_scales"], dtype=float)
    left_orbit, _left_solution = _normalized_orbit(
        parameters,
        np.asarray(left_row["initial_state"]),
        left_row["period_time"],
        solver,
        scales,
        int(declared["phase_samples"]),
    )
    _right_orbit, right_solution = _normalized_orbit(
        parameters,
        np.asarray(right_row["initial_state"]),
        right_row["period_time"],
        solver,
        scales,
        int(declared["phase_samples"]),
    )
    rms, phase_shift = _continuous_phase_invariant_rms(
        left_orbit,
        right_solution,
        right_row["period_time"],
        scales,
        shift_tolerance=float(declared["phase_shift_tolerance"]),
    )
    same_family = bool(
        relative_period
        <= float(manifest["acceptance"]["maximum_shared_relative_period_difference"])
        and rms <= float(manifest["acceptance"]["maximum_shared_phase_invariant_rms"])
    )
    classification_policy = declared.get("classification")
    if classification_policy is None:
        classification = "same" if same_family else "not-qualified-as-same"
        passed = bool(parameter_match and same_family)
    else:
        distinct_family = bool(
            relative_period
            >= float(
                classification_policy[
                    "minimum_distinct_relative_period_difference"
                ]
            )
            or rms
            >= float(classification_policy["minimum_distinct_phase_invariant_rms"])
        )
        if same_family:
            classification = "same"
        elif distinct_family:
            classification = "distinct"
        else:
            classification = "inconclusive"
        passed = bool(parameter_match and classification != "inconclusive")
    return {
        "comparison_a": target_a,
        "exact_parameter_match": exact_parameter_match,
        "parameter_match": parameter_match,
        "maximum_parameter_error": maximum_parameter_error,
        "relative_period_difference": relative_period,
        "phase_invariant_rms": rms,
        "phase_shift": phase_shift,
        "classification": classification,
        "passed": passed,
    }


def _section_count_summary(branches, manifest):
    policy = manifest.get("section_count", {})
    expected = int(policy.get("expected_crossings", 0))
    rows = [row for branch in branches for row in branch["rows"]]
    if not policy or bool(policy.get("gate", True)):
        return {
            "separate_qualification": False,
            "passed": True,
        }
    counts = [row["audit"]["one_period_section_crossing_count"] for row in rows]
    integrations = [
        row["audit"]["section_count_integration_success"] for row in rows
    ]
    return {
        "separate_qualification": True,
        "window_start_fraction": float(policy["phase_fraction"]),
        "expected_crossings": expected,
        "evaluated_points": len(rows),
        "observed_counts": sorted(set(counts)),
        "all_integrations_succeeded": bool(all(integrations)),
        "passed": bool(
            rows
            and all(integrations)
            and all(count == expected for count in counts)
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--identity-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.a-upo-continuation-manifest.v1":
        raise SystemExit("unsupported a-UPO continuation manifest")
    source_bytes = args.source_receipt.read_bytes()
    identity_bytes = args.identity_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source UPO receipt hash mismatch")
    if sha256_bytes(identity_bytes) != manifest["identity_receipt_sha256"]:
        raise SystemExit("identity audit receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    source_receipt = json.loads(source_bytes)
    solver = SolverConfig(**manifest["reference_solver"])
    started = time.perf_counter()
    branches = [
        _run_branch(branch, source_receipt, manifest, solver)
        for branch in manifest["branches"]
    ]
    shared_identity = _shared_identity(branches, manifest, solver)
    section_count_summary = _section_count_summary(branches, manifest)
    receipt = {
        "schema": "butterfly.a-upo-continuation-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "identity_receipt_sha256": sha256_bytes(identity_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "branches": branches,
        "shared_family_identity": shared_identity,
        "section_count_summary": section_count_summary,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(branch["passed"] for branch in branches)
        and shared_identity["passed"]
        and section_count_summary["passed"],
        "scientific_scope": (
            "finite natural UPO continuation, not a manifold event or TBA curve"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {key: value for key, value in receipt.items() if key != "branches"},
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
