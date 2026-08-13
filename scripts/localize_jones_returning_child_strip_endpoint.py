#!/usr/bin/env python3
"""Localize the terminal parent flip on the frozen returning-child offset path."""

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
from scripts.continue_jones_returning_period12_child import _continue_row, _correct
from scripts.qualify_jones_period12_children import _qualify_target, _summary


SCHEMA = "butterfly.jones-returning-child-strip-endpoint-manifest.v1"


def double_cover_metrics(row):
    """Measure whether the nominal child is the corrected parent traversed twice."""

    half_period = next(
        item["closure"]
        for item in row["proper_subperiod_closures"]
        if float(item["fraction"]) == 0.5
    )
    parent_real = float(row["parent"]["dominant_transverse_multiplier"]["real"])
    child_real = float(row["child"]["dominant_transverse_multiplier"]["real"])
    return {
        "parent_child_state_distance": float(
            np.linalg.norm(
                np.asarray(row["parent"]["initial_state"], dtype=float)
                - np.asarray(row["child"]["initial_state"], dtype=float)
            )
        ),
        "child_half_period_closure": float(half_period),
        "period_ratio_error": abs(float(row["period_ratio"]) - 2.0),
        "multiplier_square_error": abs(child_real - parent_real**2),
        "parent_multiplier_modulus": float(
            row["parent"]["dominant_transverse_multiplier"]["modulus"]
        ),
        "child_multiplier_modulus": float(
            row["child"]["dominant_transverse_multiplier"]["modulus"]
        ),
    }


def double_cover_passes(row, metrics, acceptance):
    """Apply frozen doubled-parent and stable-parent gates."""

    return bool(
        row["checks"]["closure"]
        and row["checks"]["child_stable"]
        and row["checks"]["period_ratio"]
        and row["checks"]["section_identity"]
        and not row["checks"]["parent_unstable"]
        and not row["checks"]["proper_subperiod"]
        and metrics["parent_multiplier_modulus"]
        <= float(acceptance["maximum_right_parent_multiplier_modulus"])
        and metrics["parent_child_state_distance"]
        <= float(acceptance["maximum_double_cover_state_distance"])
        and metrics["child_half_period_closure"]
        <= float(acceptance["maximum_double_cover_half_period_closure"])
        and metrics["period_ratio_error"]
        <= float(acceptance["maximum_period_ratio_error"])
        and metrics["multiplier_square_error"]
        <= float(acceptance["maximum_multiplier_square_error"])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--adaptive-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported returning-child endpoint manifest")
    event_bytes = args.event_receipt.read_bytes()
    adaptive_bytes = args.adaptive_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(adaptive_bytes) != manifest["adaptive_receipt_sha256"]:
        raise SystemExit("adaptive receipt hash mismatch")
    event_receipt = json.loads(event_bytes)
    adaptive_receipt = json.loads(adaptive_bytes)
    if not event_receipt.get("passed") or adaptive_receipt.get("passed"):
        raise SystemExit("endpoint localization requires passed event arm and failed adaptive claim")

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("returning-child endpoint localization requires clean source")

    expected_delta = float(manifest["expected_delta_a"])
    delta_a = float(adaptive_receipt["delta_a"])
    if delta_a != expected_delta:
        raise SystemExit("adaptive child offset does not match frozen endpoint path")
    source_interval = manifest["source_interval"]
    source_rows = {
        float(row["c"]): row for row in event_receipt["rows"]
    }
    event_left = source_rows[float(source_interval["left_c"])]
    event_right = source_rows[float(source_interval["right_c"])]

    def event_at(c_value):
        fraction = (float(c_value) - float(event_left["c"])) / (
            float(event_right["c"]) - float(event_left["c"])
        )
        return interpolate_event(event_left, event_right, fraction)

    corrector = manifest["corrector"]
    solvers = {
        "dop853": SolverConfig(**manifest["solver"]),
        "radau": SolverConfig(**manifest["independent_solver"]),
    }

    def parent_evaluator(solver):
        cache = {}

        def evaluate(c_value):
            key = float(c_value)
            if key not in cache:
                event = event_at(key)
                parameters = RosslerParameters(
                    a=float(event["a"]) + delta_a,
                    b=float(manifest["fixed_b"]),
                    c=key,
                )
                orbit, monodromy = _correct(
                    parameters,
                    event["initial_state"],
                    event["period_time"],
                    solver,
                    corrector,
                )
                summary = _summary(orbit, monodromy)
                multiplier = summary["dominant_transverse_multiplier"]
                cache[key] = {
                    "c": key,
                    "a": parameters.a,
                    "summary": summary,
                    "flip_residual": float(multiplier["real"]) + 1.0,
                    "imaginary_part": float(multiplier["imag"]),
                }
            return cache[key]

        return evaluate, cache

    root_config = manifest["root"]
    bracket = manifest["endpoint_bracket"]
    root_results = {}
    started = time.perf_counter()
    for name, solver in solvers.items():
        evaluate, cache = parent_evaluator(solver)
        left = evaluate(float(bracket["left_c"]))
        right = evaluate(float(bracket["right_c"]))
        root_c, root_info = brentq(
            lambda c_value: evaluate(c_value)["flip_residual"],
            float(bracket["left_c"]),
            float(bracket["right_c"]),
            xtol=float(root_config["xtol"]),
            rtol=float(root_config["rtol"]),
            maxiter=int(root_config["maximum_iterations"]),
            full_output=True,
            disp=False,
        )
        root = evaluate(root_c)
        root_results[name] = {
            "left": left,
            "right": right,
            "root": root,
            "converged": bool(root_info.converged),
            "iterations": int(root_info.iterations),
            "function_calls": int(root_info.function_calls),
            "evaluations": [cache[key] for key in sorted(cache)],
        }

    root_c = float(root_results["dop853"]["root"]["c"])
    bilateral_delta_c = float(manifest["bilateral"]["delta_c"])
    left_c = root_c - bilateral_delta_c
    right_c = root_c + bilateral_delta_c
    terminal_rows = [
        row
        for row in adaptive_receipt["accepted_rows"]
        if float(row["c"]) == float(manifest["terminal_seed_c"])
    ]
    if len(terminal_rows) != 1:
        raise SystemExit("terminal seed c does not select one accepted child")
    seed_child = terminal_rows[0]["child"]

    left_event = event_at(left_c)
    left_row = _continue_row(
        left_event, seed_child, delta_a, manifest, solvers["dop853"]
    )
    try:
        left_control = _qualify_target(
            {
                "c": left_row["c"],
                "candidate_a": left_row["a"],
                "source_direction": 1,
            },
            {
                "c": left_row["c"],
                "event_a": left_event["a"],
                "event_variables": [
                    *left_event["initial_state"],
                    2.0 * float(left_event["period_time"]),
                    float(left_event["a"]),
                ],
            },
            {
                "initial_state": left_row["child"]["initial_state"],
                "period_time": left_row["child"]["period_time"],
            },
            manifest,
            (solvers["dop853"], solvers["radau"]),
        )
    except Exception as error:
        left_control = {
            "c": float(left_row["c"]),
            "a": float(left_row["a"]),
            "passed": False,
            "error": f"{type(error).__name__}: {error}",
        }

    right_event = event_at(right_c)
    right_double_cover = {}
    try:
        right_dop853 = _continue_row(
            right_event,
            left_row["child"],
            delta_a,
            manifest,
            solvers["dop853"],
        )
        metrics = double_cover_metrics(right_dop853)
        right_double_cover["dop853"] = {
            "row": right_dop853,
            "metrics": metrics,
            "passed": double_cover_passes(
                right_dop853, metrics, manifest["acceptance"]
            ),
        }
    except Exception as error:
        right_double_cover["dop853"] = {
            "passed": False,
            "error": f"{type(error).__name__}: {error}",
        }
    if "row" in right_double_cover["dop853"]:
        try:
            right_radau = _continue_row(
                right_event,
                right_double_cover["dop853"]["row"]["child"],
                delta_a,
                manifest,
                solvers["radau"],
            )
            metrics = double_cover_metrics(right_radau)
            right_double_cover["radau"] = {
                "row": right_radau,
                "metrics": metrics,
                "passed": double_cover_passes(
                    right_radau, metrics, manifest["acceptance"]
                ),
            }
        except Exception as error:
            right_double_cover["radau"] = {
                "passed": False,
                "error": f"{type(error).__name__}: {error}",
            }
    else:
        right_double_cover["radau"] = {
            "passed": False,
            "error": "DOP853 right control unavailable",
        }

    acceptance = manifest["acceptance"]
    root_difference = abs(
        float(root_results["dop853"]["root"]["c"])
        - float(root_results["radau"]["root"]["c"])
    )
    root_checks = {
        "both_converged": all(row["converged"] for row in root_results.values()),
        "dop853_bracket": (
            root_results["dop853"]["left"]["flip_residual"]
            <= -float(acceptance["minimum_bracket_residual_magnitude"])
            and root_results["dop853"]["right"]["flip_residual"]
            >= float(acceptance["minimum_bracket_residual_magnitude"])
        ),
        "radau_bracket": (
            root_results["radau"]["left"]["flip_residual"]
            <= -float(acceptance["minimum_bracket_residual_magnitude"])
            and root_results["radau"]["right"]["flip_residual"]
            >= float(acceptance["minimum_bracket_residual_magnitude"])
        ),
        "root_residuals": all(
            abs(row["root"]["flip_residual"])
            <= float(acceptance["maximum_root_residual"])
            for row in root_results.values()
        ),
        "real_multipliers": all(
            max(
                abs(row["left"]["imaginary_part"]),
                abs(row["right"]["imaginary_part"]),
                abs(row["root"]["imaginary_part"]),
            )
            <= float(acceptance["maximum_multiplier_imaginary_part"])
            for row in root_results.values()
        ),
        "solver_root_agreement": root_difference
        <= float(acceptance["maximum_solver_root_difference"]),
    }
    passed = bool(
        all(root_checks.values())
        and left_row["passed"]
        and left_control["passed"]
        and all(row["passed"] for row in right_double_cover.values())
    )
    output = {
        "schema": "butterfly.jones-returning-child-strip-endpoint-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "adaptive_receipt_sha256": sha256_bytes(adaptive_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "delta_a": delta_a,
        "root_results": root_results,
        "root_solver_c_difference": root_difference,
        "root_checks": root_checks,
        "bilateral_delta_c": bilateral_delta_c,
        "primitive_left": {"row": left_row, "independent_control": left_control},
        "double_cover_right": right_double_cover,
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
                "dop853_root_c": root_results["dop853"]["root"]["c"],
                "radau_root_c": root_results["radau"]["root"]["c"],
                "root_solver_c_difference": root_difference,
                "primitive_left_passed": bool(left_control["passed"]),
                "double_cover_right_passed": {
                    name: row["passed"] for name, row in right_double_cover.items()
                },
                "root_checks": root_checks,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
