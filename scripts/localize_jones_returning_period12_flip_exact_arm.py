#!/usr/bin/env python3
"""Localize the period-12 flip exposed by exact-arm child continuation."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import brentq

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.bridge_jones_returning_period12_child import interpolate_event
from scripts.continue_jones_period6_flip_curve import _solve_event
from scripts.continue_jones_returning_period12_child import (
    _continue_row,
    _correct,
)
from scripts.continue_jones_returning_period12_child_exact_arm import event_manifest
from scripts.qualify_jones_period12_children import _summary


SCHEMA = "butterfly.jones-returning-period12-flip-exact-arm-manifest.v1"


def root_row_passes(row, root_residual, acceptance):
    """Apply primitive period-12 flip gates without demanding child stability."""

    multiplier = row["child"]["dominant_transverse_multiplier"]
    return bool(
        row["checks"]["closure"]
        and row["checks"]["parent_unstable"]
        and row["checks"]["period_ratio"]
        and row["checks"]["proper_subperiod"]
        and row["checks"]["section_identity"]
        and abs(float(root_residual))
        <= float(acceptance["maximum_root_multiplier_residual"])
        and abs(float(multiplier["imag"]))
        <= float(acceptance["maximum_multiplier_imaginary_part"])
        and float(row["child"]["neutral_multiplier_error"])
        <= float(acceptance["maximum_neutral_multiplier_error"])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--exact-arm-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported exact-arm period-12 flip manifest")
    event_bytes = args.event_receipt.read_bytes()
    exact_arm_bytes = args.exact_arm_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(exact_arm_bytes) != manifest["exact_arm_receipt_sha256"]:
        raise SystemExit("exact-arm receipt hash mismatch")
    arm = json.loads(event_bytes)
    exact_arm = json.loads(exact_arm_bytes)
    if not arm.get("passed") or exact_arm.get("passed"):
        raise SystemExit("flip localization requires passed arm and failed exact-arm claim")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("exact-arm period-12 flip localization requires clean source")

    delta_a = float(exact_arm["delta_a"])
    if abs(delta_a - float(manifest["expected_delta_a"])) > 1e-15:
        raise SystemExit("exact-arm offset mismatch")
    source_interval = manifest["source_interval"]
    source_rows = {float(row["c"]): row for row in arm["rows"]}
    event_left = source_rows[float(source_interval["left_c"])]
    event_right = source_rows[float(source_interval["right_c"])]
    seed_c = float(manifest["child_seed_c"])
    seed_rows = [
        row for row in exact_arm["accepted_rows"] if float(row["c"]) == seed_c
    ]
    if len(seed_rows) != 1:
        raise SystemExit("child seed c does not select one accepted exact-arm row")
    child_seed = seed_rows[0]["child"]
    solvers = {
        "dop853": SolverConfig(**manifest["solver"]),
        "radau": SolverConfig(**manifest["independent_solver"]),
    }
    event_configuration = event_manifest(manifest)

    def interpolated_seed(c_value):
        fraction = (float(c_value) - float(event_left["c"])) / (
            float(event_right["c"]) - float(event_left["c"])
        )
        return interpolate_event(event_left, event_right, fraction)

    def child_evaluator(solver):
        cache = {}

        def evaluate(c_value):
            key = float(c_value)
            if key not in cache:
                event = _solve_event(
                    key,
                    interpolated_seed(key),
                    event_configuration,
                    solver,
                )
                if not event["passed"]:
                    raise RuntimeError("fresh source event failed exact gates")
                parameters = RosslerParameters(
                    a=float(event["a"]) + delta_a,
                    b=float(manifest["fixed_b"]),
                    c=key,
                )
                orbit, monodromy = _correct(
                    parameters,
                    child_seed["initial_state"],
                    child_seed["period_time"],
                    solver,
                    manifest["corrector"],
                )
                summary = _summary(orbit, monodromy)
                multiplier = summary["dominant_transverse_multiplier"]
                cache[key] = {
                    "c": key,
                    "a": parameters.a,
                    "event": event,
                    "child": summary,
                    "flip_residual": float(multiplier["real"]) + 1.0,
                }
            return cache[key]

        return evaluate, cache

    bracket = list(map(float, manifest["root"]["c_bracket"]))
    root_results = {}
    started = time.perf_counter()
    for name, solver in solvers.items():
        evaluate, cache = child_evaluator(solver)
        left = evaluate(bracket[0])
        right = evaluate(bracket[1])
        if left["flip_residual"] * right["flip_residual"] >= 0.0:
            raise RuntimeError(f"{name} does not bracket the child flip")
        root_c, info = brentq(
            lambda value: evaluate(value)["flip_residual"],
            bracket[0],
            bracket[1],
            xtol=float(manifest["root"]["xtol"]),
            rtol=float(manifest["root"]["rtol"]),
            maxiter=int(manifest["root"]["maximum_iterations"]),
            full_output=True,
            disp=False,
        )
        root = evaluate(root_c)
        root_full = _continue_row(
            root["event"], child_seed, delta_a, manifest, solver
        )
        bilateral = {}
        for side, sign in (("left", -1.0), ("right", 1.0)):
            c_value = root_c + sign * float(manifest["bilateral_delta_c"])
            point = evaluate(c_value)
            full = _continue_row(
                point["event"], child_seed, delta_a, manifest, solver
            )
            bilateral[side] = {
                "c": c_value,
                "a": float(full["a"]),
                "child_multiplier": full["child"][
                    "dominant_transverse_multiplier"
                ],
                "minimum_proper_subperiod_closure": float(
                    full["minimum_proper_subperiod_closure"]
                ),
                "checks": full["checks"],
            }
        root_results[name] = {
            "left_bracket": left,
            "right_bracket": right,
            "root": root,
            "root_full": root_full,
            "bilateral": bilateral,
            "converged": bool(info.converged),
            "iterations": int(info.iterations),
            "function_calls": int(info.function_calls),
            "evaluation_count": len(cache),
        }

    acceptance = manifest["root_acceptance"]
    c_difference = abs(
        float(root_results["dop853"]["root"]["c"])
        - float(root_results["radau"]["root"]["c"])
    )
    for result in root_results.values():
        result["root_passed"] = root_row_passes(
            result["root_full"], result["root"]["flip_residual"], acceptance
        )
        left = result["bilateral"]["left"]
        right = result["bilateral"]["right"]
        result["bilateral_passed"] = bool(
            left["checks"]["proper_subperiod"]
            and left["checks"]["section_identity"]
            and right["checks"]["proper_subperiod"]
            and right["checks"]["section_identity"]
            and float(left["child_multiplier"]["real"])
            >= -float(acceptance["maximum_left_child_multiplier_modulus"])
            and float(left["child_multiplier"]["real"]) < 0.0
            and float(right["child_multiplier"]["real"])
            <= -float(acceptance["minimum_right_child_multiplier_modulus"])
        )
    passed = bool(
        c_difference <= float(acceptance["maximum_solver_c_difference"])
        and all(
            result["converged"]
            and result["root_passed"]
            and result["bilateral_passed"]
            for result in root_results.values()
        )
    )
    output = {
        "schema": "butterfly.jones-returning-period12-flip-exact-arm-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "exact_arm_receipt_sha256": sha256_bytes(exact_arm_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "delta_a": delta_a,
        "root_results": root_results,
        "root_solver_c_difference": c_difference,
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
                "roots": {
                    name: {
                        "a": result["root"]["a"],
                        "c": result["root"]["c"],
                        "residual": result["root"]["flip_residual"],
                        "root_passed": result["root_passed"],
                        "bilateral_passed": result["bilateral_passed"],
                    }
                    for name, result in root_results.items()
                },
                "root_solver_c_difference": c_difference,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
