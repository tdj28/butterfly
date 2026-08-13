#!/usr/bin/env python3
"""Test whether EXP-227 is the known EXP-217 arm at exactly matched c."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.bridge_jones_returning_period12_child import interpolate_event
from scripts.continue_jones_period6_flip_curve import _solve_event


SCHEMA = "butterfly.exp227-exact-source-identity-manifest.v1"


def _difference(reference, corrected):
    reference_state = np.asarray(reference["initial_state"], dtype=float)
    corrected_state = np.asarray(corrected["initial_state"], dtype=float)
    reference_tangent = np.asarray(reference["tangent"], dtype=float)
    corrected_tangent = np.asarray(corrected["tangent"], dtype=float)
    tangent_difference = min(
        np.linalg.norm(reference_tangent - corrected_tangent),
        np.linalg.norm(reference_tangent + corrected_tangent),
    )
    return {
        "a_difference": abs(float(reference["a"]) - float(corrected["a"])),
        "period_relative_difference": abs(
            float(reference["period_time"]) - float(corrected["period_time"])
        )
        / float(reference["period_time"]),
        "state_difference": float(np.linalg.norm(reference_state - corrected_state)),
        "tangent_sign_invariant_difference": float(tangent_difference),
        "multiplier_modulus_difference": abs(
            float(reference["dominant_multiplier"]["modulus"])
            - float(corrected["dominant_multiplier"]["modulus"])
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate-receipt", type=Path, required=True)
    parser.add_argument("--source-arm-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported exact-source identity manifest")
    candidate_bytes = args.candidate_receipt.read_bytes()
    source_arm_bytes = args.source_arm_receipt.read_bytes()
    if sha256_bytes(candidate_bytes) != manifest["candidate_receipt_sha256"]:
        raise SystemExit("candidate receipt hash mismatch")
    if sha256_bytes(source_arm_bytes) != manifest["source_arm_receipt_sha256"]:
        raise SystemExit("source-arm receipt hash mismatch")
    candidate = json.loads(candidate_bytes)
    source_arm = json.loads(source_arm_bytes)
    if not candidate.get("passed") or not source_arm.get("passed"):
        raise SystemExit("identity audit requires passed input receipts")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("exact-source identity audit requires clean source")

    source_rows = sorted(source_arm["rows"], key=lambda row: float(row["c"]))
    source_c = np.asarray([row["c"] for row in source_rows], dtype=float)
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    acceptance = manifest["identity_acceptance"]
    control_indices = set(map(int, manifest["independent_control_indices"]))
    rows = []
    controls = []
    started = time.perf_counter()

    for index, reference in enumerate(candidate["rows"]):
        c_value = float(reference["c"])
        nearest_index = int(np.argmin(abs(source_c - c_value)))
        nearest = source_rows[nearest_index]
        exact = _solve_event(c_value, nearest, manifest, solver)
        differences = _difference(reference, exact)

        bracket_index = max(
            0,
            min(
                len(source_rows) - 2,
                int(np.searchsorted(source_c, c_value)) - 1,
            ),
        )
        left = source_rows[bracket_index]
        right = source_rows[bracket_index + 1]
        fraction = (c_value - float(left["c"])) / (
            float(right["c"]) - float(left["c"])
        )
        interpolated = interpolate_event(left, right, fraction)
        interpolation_a_error = float(interpolated["a"]) - float(exact["a"])
        identity_passed = bool(
            exact["passed"]
            and differences["a_difference"]
            <= float(acceptance["maximum_a_difference"])
            and differences["period_relative_difference"]
            <= float(acceptance["maximum_period_relative_difference"])
            and differences["state_difference"]
            <= float(acceptance["maximum_state_difference"])
            and differences["tangent_sign_invariant_difference"]
            <= float(acceptance["maximum_tangent_difference"])
            and differences["multiplier_modulus_difference"]
            <= float(acceptance["maximum_modulus_difference"])
        )
        rows.append(
            {
                "index": index,
                "c": c_value,
                "candidate_a": float(reference["a"]),
                "exact_source_a": float(exact["a"]),
                "linear_interpolated_source_a": float(interpolated["a"]),
                "linear_interpolation_a_error": interpolation_a_error,
                "nearest_source_c_distance": abs(float(nearest["c"]) - c_value),
                **differences,
                "exact_source_passed": bool(exact["passed"]),
                "passed": identity_passed,
            }
        )
        if index in control_indices:
            independent = _solve_event(c_value, nearest, manifest, independent_solver)
            control_differences = _difference(reference, independent)
            controls.append(
                {
                    "index": index,
                    "c": c_value,
                    **control_differences,
                    "independent_passed": bool(independent["passed"]),
                    "passed": bool(
                        independent["passed"]
                        and control_differences["a_difference"]
                        <= float(acceptance["maximum_independent_a_difference"])
                        and control_differences["period_relative_difference"]
                        <= float(
                            acceptance[
                                "maximum_independent_period_relative_difference"
                            ]
                        )
                        and control_differences["state_difference"]
                        <= float(acceptance["maximum_independent_state_difference"])
                        and control_differences["multiplier_modulus_difference"]
                        <= float(acceptance["maximum_independent_modulus_difference"])
                    ),
                }
            )

    def maximum(key, values):
        return max(float(row[key]) for row in values)

    passed = bool(
        len(rows) == int(manifest["required_point_count"])
        and all(row["passed"] for row in rows)
        and len(controls) == len(control_indices)
        and all(control["passed"] for control in controls)
    )
    summary = {
        "maximum_a_difference": maximum("a_difference", rows),
        "maximum_period_relative_difference": maximum(
            "period_relative_difference", rows
        ),
        "maximum_state_difference": maximum("state_difference", rows),
        "maximum_tangent_sign_invariant_difference": maximum(
            "tangent_sign_invariant_difference", rows
        ),
        "maximum_multiplier_modulus_difference": maximum(
            "multiplier_modulus_difference", rows
        ),
        "linear_interpolation_a_error_range": [
            min(float(row["linear_interpolation_a_error"]) for row in rows),
            max(float(row["linear_interpolation_a_error"]) for row in rows),
        ],
        "maximum_independent_a_difference": maximum("a_difference", controls),
        "maximum_independent_state_difference": maximum(
            "state_difference", controls
        ),
        "maximum_independent_modulus_difference": maximum(
            "multiplier_modulus_difference", controls
        ),
    }
    output = {
        "schema": "butterfly.exp227-exact-source-identity-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "candidate_receipt_sha256": sha256_bytes(candidate_bytes),
        "source_arm_receipt_sha256": sha256_bytes(source_arm_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "rows": rows,
        "independent_controls": controls,
        "summary": summary,
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
                **summary,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
