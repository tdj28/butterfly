#!/usr/bin/env python3
"""Audit divisor closure and phase-invariant identity of recovered PIM UPOs."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from butterfly import RosslerParameters, SolverConfig, flow_monodromy, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _proper_repeat_factors(lag):
    return tuple(factor for factor in range(2, lag + 1) if lag % factor == 0)


def _normalized_orbit(parameters, state, period, solver, scales, samples):
    result = solve_ivp(
        lambda current_time, current_state: rossler_rhs(
            current_time, current_state, parameters
        ),
        (0.0, period),
        state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
        dense_output=True,
    )
    if not result.success:
        raise RuntimeError(f"dense orbit integration failed: {result.message}")
    times = np.linspace(0.0, period, samples, endpoint=False)
    return np.asarray(result.sol(times).T, dtype=float) / scales, result.sol


def _phase_invariant_rms(left, right):
    return min(
        float(np.sqrt(np.mean((left - np.roll(right, shift, axis=0)) ** 2)))
        for shift in range(len(left))
    )


def _continuous_phase_invariant_rms(
    left,
    right_solution,
    right_period,
    scales,
    *,
    shift_tolerance,
):
    phases = np.linspace(0.0, 1.0, len(left), endpoint=False)

    def rms(shift):
        right = np.asarray(
            right_solution(((phases + shift) % 1.0) * right_period).T,
            dtype=float,
        ) / scales
        return float(np.sqrt(np.mean((left - right) ** 2)))

    coarse = np.asarray([rms(index / len(left)) for index in range(len(left))])
    best = int(np.argmin(coarse))
    spacing = 1.0 / len(left)
    refined = minimize_scalar(
        lambda shift: rms(shift % 1.0),
        bounds=(best / len(left) - spacing, best / len(left) + spacing),
        method="bounded",
        options={"xatol": shift_tolerance},
    )
    return float(refined.fun), float(refined.x % 1.0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--predecessor-receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.pim-upo-primitivity-audit-manifest.v1":
        raise SystemExit("unsupported UPO primitivity manifest")
    receipt_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(receipt_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source_receipt = json.loads(receipt_bytes)
    predecessor_hash = None
    if "predecessor_receipt_sha256" in manifest:
        if args.predecessor_receipt is None:
            raise SystemExit("predecessor receipt is required by the manifest")
        predecessor_bytes = args.predecessor_receipt.read_bytes()
        predecessor_hash = sha256_bytes(predecessor_bytes)
        if predecessor_hash != manifest["predecessor_receipt_sha256"]:
            raise SystemExit("predecessor receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["reference_solver"])
    acceptance = manifest["acceptance"]
    scales = np.asarray(manifest["identity"]["coordinate_scales"], dtype=float)
    samples = int(manifest["identity"]["phase_samples"])
    case_rows = []
    started = time.perf_counter()
    for source_case in source_receipt["cases"]:
        parameters = RosslerParameters(**source_case["parameters"])
        audited = []
        for recovery_index, recovery in enumerate(source_case["recoveries"]):
            if not recovery["accepted"]:
                continue
            lag = int(recovery["seed"]["lag"])
            state = np.asarray(recovery["correction"]["initial_state"], dtype=float)
            period = float(recovery["correction"]["period_time"])
            divisor_rows = []
            passing = []
            for repeat_factor in _proper_repeat_factors(lag):
                candidate_period = period / repeat_factor
                result = flow_monodromy(
                    parameters, state, candidate_period, config=solver
                )
                passed = bool(
                    result.success
                    and result.closure_error
                    <= float(acceptance["maximum_divisor_flow_closure"])
                )
                divisor_rows.append(
                    {
                        "repeat_factor": repeat_factor,
                        "candidate_fundamental_lag": lag // repeat_factor,
                        "candidate_period_time": candidate_period,
                        "flow_closure_error": result.closure_error,
                        "passed": passed,
                    }
                )
                if passed:
                    passing.append(repeat_factor)
            repeat_factor = max(passing, default=1)
            fundamental_lag = lag // repeat_factor
            fundamental_period = period / repeat_factor
            orbit, dense_solution = _normalized_orbit(
                parameters, state, fundamental_period, solver, scales, samples
            )
            audited.append(
                {
                    "source_recovery_index": recovery_index,
                    "state_key": recovery["state_key"],
                    "reported_lag": lag,
                    "repeat_factor": repeat_factor,
                    "fundamental_lag": fundamental_lag,
                    "reported_period_time": period,
                    "fundamental_period_time": fundamental_period,
                    "primitive_as_reported": repeat_factor == 1,
                    "divisor_tests": divisor_rows,
                    "orbit": orbit,
                    "dense_solution": dense_solution,
                }
            )

        families = []
        for audit_index, row in enumerate(audited):
            family_id = None
            identity_rms = None
            for family in families:
                representative = audited[family["representative_audit_index"]]
                period_scale = max(
                    abs(row["fundamental_period_time"]),
                    abs(representative["fundamental_period_time"]),
                    np.finfo(float).eps,
                )
                period_error = abs(
                    row["fundamental_period_time"]
                    - representative["fundamental_period_time"]
                ) / period_scale
                if (
                    row["fundamental_lag"] == representative["fundamental_lag"]
                    and period_error
                    <= float(acceptance["maximum_relative_period_difference"])
                ):
                    if "phase_shift_tolerance" in manifest["identity"]:
                        rms, phase_shift = _continuous_phase_invariant_rms(
                            row["orbit"],
                            representative["dense_solution"],
                            representative["fundamental_period_time"],
                            scales,
                            shift_tolerance=float(
                                manifest["identity"]["phase_shift_tolerance"]
                            ),
                        )
                    else:
                        rms = _phase_invariant_rms(
                            row["orbit"], representative["orbit"]
                        )
                        phase_shift = None
                    if rms <= float(acceptance["maximum_phase_invariant_rms"]):
                        family_id = family["id"]
                        identity_rms = rms
                        row["phase_shift_to_representative"] = phase_shift
                        family["member_audit_indices"].append(audit_index)
                        break
            if family_id is None:
                family_id = f"{source_case['id']}-upo-{len(families) + 1:02d}"
                identity_rms = 0.0
                families.append(
                    {
                        "id": family_id,
                        "fundamental_lag": row["fundamental_lag"],
                        "fundamental_period_time": row["fundamental_period_time"],
                        "representative_audit_index": audit_index,
                        "member_audit_indices": [audit_index],
                    }
                )
            row["orbit_family_id"] = family_id
            row["phase_invariant_rms_to_representative"] = identity_rms
        for row in audited:
            del row["orbit"]
            del row["dense_solution"]
        case_rows.append(
            {
                "id": source_case["id"],
                "parameters": source_case["parameters"],
                "accepted_source_recoveries": len(audited),
                "primitive_as_reported_count": sum(
                    row["primitive_as_reported"] for row in audited
                ),
                "double_or_higher_cover_count": sum(
                    not row["primitive_as_reported"] for row in audited
                ),
                "unique_primitive_orbit_family_count": len(families),
                "unique_fundamental_lags": sorted(
                    {family["fundamental_lag"] for family in families}
                ),
                "audits": audited,
                "families": families,
                "passed": len(families)
                >= int(acceptance["minimum_unique_primitive_families_per_case"]),
            }
        )
    receipt = {
        "schema": "butterfly.pim-upo-primitivity-audit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(receipt_bytes),
        "predecessor_receipt_sha256": predecessor_hash,
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "cases": case_rows,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(case["passed"] for case in case_rows),
        "scientific_scope": "finite UPO identity audit, not manifold continuation",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
