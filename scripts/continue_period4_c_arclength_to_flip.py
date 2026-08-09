#!/usr/bin/env python3
"""Pseudo-arclength continuation of the Jones-path period-4 child."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, correct_periodic_orbit, flow_monodromy
from butterfly.periodic_c import correct_arclength_c
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms
from continue_period2_c_arclength_to_flip import _diagnose, _variables
from continue_period2_c_to_flip import _dominant_nontrivial, first_real_minus_one_bracket


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period4-c-arclength-to-flip-manifest.v1":
        raise SystemExit("unsupported period-4 c pseudo-arclength manifest")
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
    if receipt.get("schema") != "butterfly.period2-c-flip-switch-receipt.v1":
        raise SystemExit("source receipt is not a period-4 switch")
    source_branch = next(
        branch
        for branch in receipt["branches"]
        if int(branch["direction"]) == int(manifest["source_direction"])
    )
    if len(source_branch["rows"]) < 2:
        raise SystemExit("source branch has fewer than two points")
    points = [_variables(row) for row in source_branch["rows"][-2:]]
    a = float(manifest["fixed_a"])
    b = float(manifest["fixed_b"])
    solver = SolverConfig(**manifest["reference_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    continuation = manifest["continuation"]
    acceptance = manifest["acceptance"]
    rows = [
        _diagnose(
            points[-1],
            a=a,
            b=b,
            solver=solver,
            orbit_sample_count=int(manifest["orbit_sample_count"]),
        )
    ]
    statuses = []
    independent_rows = []
    bracket = None
    bracket_index = None
    step_length = float(continuation["initial_step_length"])
    started = time.perf_counter()
    for step_index in range(int(continuation["maximum_steps"])):
        tangent = points[-1] - points[-2]
        tangent /= np.linalg.norm(tangent)
        retries = 0
        accepted = False
        while retries <= int(continuation["maximum_retries_per_step"]):
            predictor = points[-1] + step_length * tangent
            corrected, status = correct_arclength_c(
                predictor,
                tangent,
                points[-1][:3],
                float(points[-1][4]),
                a=a,
                b=b,
                solver=solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            )
            statuses.append(
                {
                    **status,
                    "step_index": step_index,
                    "retry": retries,
                    "step_length": step_length,
                }
            )
            if status["success"]:
                accepted = True
                break
            step_length *= float(continuation["shrink_factor"])
            retries += 1
            if step_length < float(continuation["minimum_step_length"]):
                break
        if not accepted:
            break
        points.append(corrected)
        row = _diagnose(
            corrected,
            a=a,
            b=b,
            solver=solver,
            orbit_sample_count=int(manifest["orbit_sample_count"]),
        )
        row["step_index"] = step_index
        row["step_length"] = step_length
        rows.append(row)
        if row["half_period_closure"] < float(
            acceptance["minimum_half_period_closure"]
        ):
            break
        bracket = first_real_minus_one_bracket(
            rows, float(acceptance["maximum_bracket_multiplier_imaginary"])
        )
        if bracket is not None and bracket_index is None:
            bracket_index = len(rows) - 1
        if step_index % int(manifest["independent_check_stride"]) == 0 or (
            bracket_index == len(rows) - 1
        ):
            parameters = RosslerParameters(a=a, b=b, c=float(corrected[4]))
            independent_orbit = correct_periodic_orbit(
                parameters,
                corrected[:3],
                float(corrected[3]),
                config=independent_solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            )
            independent_monodromy = flow_monodromy(
                parameters,
                independent_orbit.initial_state,
                independent_orbit.period_time,
                config=independent_solver,
            )
            independent_dominant = _dominant_nontrivial(independent_monodromy)
            reference_correction = correct_periodic_orbit(
                parameters,
                corrected[:3],
                float(corrected[3]),
                config=solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            )
            reference_dense = dense_orbit(reference_correction, parameters, solver)
            independent_dense = dense_orbit(
                independent_orbit, parameters, independent_solver
            )
            identity = phase_aligned_rms(
                (reference_correction, reference_dense),
                (independent_orbit, independent_dense),
                phase_samples=int(manifest["comparison"]["phase_samples"]),
                coarse_shifts=int(manifest["comparison"]["coarse_shifts"]),
                shift_tolerance=float(manifest["comparison"]["shift_tolerance"]),
            )
            reference_dominant = complex(
                row["dominant_nontrivial_multiplier"]["real"],
                row["dominant_nontrivial_multiplier"]["imag"],
            )
            independent_rows.append(
                {
                    "row_index": len(rows) - 1,
                    "c": float(corrected[4]),
                    "closure_error": independent_monodromy.closure_error,
                    "orbit_identity": identity,
                    "dominant_nontrivial_multiplier": {
                        "real": float(independent_dominant.real),
                        "imag": float(independent_dominant.imag),
                        "modulus": float(abs(independent_dominant)),
                    },
                    "reference_multiplier_difference": float(
                        abs(independent_dominant - reference_dominant)
                    ),
                }
            )
        step_length = min(
            step_length * float(continuation["growth_factor"]),
            float(continuation["maximum_step_length"]),
        )
        if bracket_index is not None and len(rows) - 1 >= bracket_index + int(
            continuation["post_bracket_points"]
        ):
            break
        if not (
            float(continuation["c_guard"][0])
            <= corrected[4]
            <= float(continuation["c_guard"][1])
        ):
            break
    passed = bool(
        len(rows) >= int(acceptance["minimum_points"])
        and bracket is not None
        and min(row["half_period_closure"] for row in rows)
        >= float(acceptance["minimum_half_period_closure"])
        and max(row["closure_error"] for row in rows)
        <= float(acceptance["maximum_closure_error"])
        and max(row["neutral_multiplier_error"] for row in rows)
        <= float(acceptance["maximum_neutral_multiplier_error"])
        and max(abs(row["winding_number"] - 4.0) for row in rows)
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
        "schema": "butterfly.period4-c-arclength-to-flip-receipt.v1",
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
        "statuses": statuses,
        "independent_radau": independent_rows,
        "first_real_minus_one_bracket": bracket,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "scientific_scope": (
            "identity-safe pseudo-arclength period-4 continuation and first -1 "
            "bracket; not an exact event or switched period-8 child"
        ),
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "passed": passed,
                "point_count": len(rows),
                "c_range": [rows[0]["parameters"]["c"], rows[-1]["parameters"]["c"]],
                "minimum_half_period_closure": min(
                    row["half_period_closure"] for row in rows
                ),
                "first_real_minus_one_bracket": bracket,
                "independent_check_count": len(independent_rows),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
