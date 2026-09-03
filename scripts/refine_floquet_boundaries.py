#!/usr/bin/env python3
"""Refine signed real Floquet-multiplier crossings on corrected orbit branches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, correct_periodic_orbit, flow_monodromy
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def significant_multiplier(parameters, corrected, solver) -> tuple[complex, dict]:
    monodromy = flow_monodromy(
        parameters, corrected.initial_state, corrected.period_time, config=solver
    )
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    nontrivial = np.delete(monodromy.multipliers, neutral_index)
    value = complex(nontrivial[int(np.argmax(np.abs(nontrivial)))])
    return value, {
        "initial_state": corrected.initial_state.tolist(),
        "period_time": corrected.period_time,
        "closure_error": corrected.closure_error,
        "phase_residual": corrected.phase_residual,
        "neutral_multiplier_error": float(abs(monodromy.multipliers[neutral_index] - 1.0)),
        "significant_multiplier": {
            "real": float(value.real),
            "imag": float(value.imag),
            "modulus": float(abs(value)),
        },
    }


def row_multiplier(row: dict) -> complex:
    values = [complex(value["real"], value["imag"]) for value in row["nontrivial_multipliers"]]
    return max(values, key=abs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--continuation-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.floquet-boundary-refinement-manifest.v1":
        raise SystemExit("unsupported Floquet-boundary refinement manifest")
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
        raise SystemExit("boundary refinement requires clean source")
    solver = SolverConfig(**manifest["solver"])
    corrector_config = manifest["corrector"]
    started = time.perf_counter()
    results = []
    families = {family["id"]: family for family in continuation["families"]}
    for boundary in manifest["boundaries"]:
        family = families[boundary["family_id"]]
        target = float(boundary["target_multiplier"])
        left_b, right_b = map(float, boundary["b_bracket"])
        left_row = min(family["rows"], key=lambda row: abs(row["parameters"]["b"] - left_b))
        right_row = min(family["rows"], key=lambda row: abs(row["parameters"]["b"] - right_b))
        if abs(left_row["parameters"]["b"] - left_b) > 1e-12 or abs(
            right_row["parameters"]["b"] - right_b
        ) > 1e-12:
            raise RuntimeError(f"{boundary['id']} bracket endpoints are absent")
        left_value = row_multiplier(left_row)
        right_value = row_multiplier(right_row)
        left_residual = left_value.real - target
        right_residual = right_value.real - target
        if abs(left_value.imag) > 1e-8 or abs(right_value.imag) > 1e-8:
            raise RuntimeError(f"{boundary['id']} endpoints do not have real multipliers")
        if left_residual * right_residual > 0.0:
            raise RuntimeError(f"{boundary['id']} does not bracket its signed multiplier")
        evaluations = []
        fixed_a = float(family["fixed_a"])
        fixed_c = float(family["fixed_c"])
        for _ in range(int(manifest["refinement"]["maximum_iterations"])):
            if right_b - left_b <= float(manifest["refinement"]["b_tolerance"]):
                break
            middle_b = 0.5 * (left_b + right_b)
            seed_row = left_row if middle_b - left_b <= right_b - middle_b else right_row
            parameters = RosslerParameters(a=fixed_a, b=middle_b, c=fixed_c)
            corrected = correct_periodic_orbit(
                parameters,
                seed_row["initial_state"],
                float(seed_row["period_time"]),
                config=solver,
                max_evaluations=int(corrector_config["max_evaluations"]),
                tolerance=float(corrector_config["tolerance"]),
            )
            if not corrected.success:
                raise RuntimeError(f"{boundary['id']} midpoint orbit correction failed")
            middle_value, middle_row = significant_multiplier(parameters, corrected, solver)
            if abs(middle_value.imag) > 1e-8:
                raise RuntimeError(f"{boundary['id']} multiplier became complex")
            middle_residual = middle_value.real - target
            middle_row["b"] = middle_b
            middle_row["residual"] = float(middle_residual)
            evaluations.append(middle_row)
            source_row = {
                "initial_state": middle_row["initial_state"],
                "period_time": middle_row["period_time"],
            }
            if left_residual * middle_residual <= 0.0:
                right_b = middle_b
                right_residual = middle_residual
                right_row = source_row
            else:
                left_b = middle_b
                left_residual = middle_residual
                left_row = source_row
        best = min(evaluations, key=lambda row: abs(row["residual"]))
        result = {
            "id": boundary["id"],
            "family_id": boundary["family_id"],
            "target_multiplier": target,
            "boundary_type": "period-doubling" if target == -1.0 else "saddle-node",
            "b_bracket": [left_b, right_b],
            "b_estimate": 0.5 * (left_b + right_b),
            "bracket_width": right_b - left_b,
            "best_evaluation": best,
            "evaluation_count": len(evaluations),
        }
        acceptance = manifest["acceptance"]
        result["passed"] = bool(
            result["bracket_width"] <= float(acceptance["max_b_bracket_width"])
            and abs(best["residual"]) <= float(acceptance["max_multiplier_residual"])
            and best["closure_error"] <= float(acceptance["max_closure_error"])
        )
        results.append(result)
    receipt = {
        "schema": "butterfly.floquet-boundary-refinement-receipt.v1",
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
        "results": results,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(result["passed"] for result in results),
        "interpretation_limit": (
            "Scalar bisection on corrected orbit branches refines signed Floquet "
            "crossings but is not a coupled codimension-one boundary continuation."
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
                "boundaries": [
                    {
                        "id": result["id"],
                        "type": result["boundary_type"],
                        "b_estimate": result["b_estimate"],
                        "width": result["bracket_width"],
                    }
                    for result in results
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
