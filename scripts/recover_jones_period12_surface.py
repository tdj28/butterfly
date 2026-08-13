#!/usr/bin/env python3
"""Recover EXP-210 with independent child seeds and identity selection."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.compare_periodic_orbit_identity import phase_aligned_rms
from scripts.continue_jones_period12_surface import _row_passes
from scripts.qualify_jones_period12_normal_form import (
    _correct,
    _radau_check,
    _row_diagnostics,
    fit_power_law,
)


SCHEMA = "butterfly.jones-period12-surface-recovery-manifest.v1"


def interpolate_normal_form_seed(normal_form_receipt, c_value, offset_a):
    anchors = []
    for target in sorted(normal_form_receipt["targets"], key=lambda item: item["c"]):
        rows = sorted(target["rows"], key=lambda item: item["offset_a"])
        offsets = np.asarray([row["offset_a"] for row in rows], dtype=float)
        state = np.asarray(
            [
                np.interp(
                    float(offset_a),
                    offsets,
                    [row["child"]["initial_state"][index] for row in rows],
                )
                for index in range(3)
            ],
            dtype=float,
        )
        period = float(
            np.interp(
                float(offset_a), offsets, [row["child"]["period_time"] for row in rows]
            )
        )
        anchors.append((float(target["c"]), state, period))
    c_anchors = np.asarray([item[0] for item in anchors], dtype=float)
    state = np.asarray(
        [
            np.interp(float(c_value), c_anchors, [item[1][index] for item in anchors])
            for index in range(3)
        ],
        dtype=float,
    )
    period = float(np.interp(float(c_value), c_anchors, [item[2] for item in anchors]))
    return state, period


def interpolate_passing_surface_seed(surface_receipt, c_value, offset_a):
    matching = [
        line
        for line in surface_receipt["lines"]
        if float(line["offset_a"]) == float(offset_a)
    ]
    if len(matching) != 1:
        raise ValueError("offset must select exactly one failed-surface line")
    rows = sorted(
        (row for row in matching[0]["rows"] if row["passed"]), key=lambda row: row["c"]
    )
    if not rows:
        raise ValueError("failed-surface line contains no passing child roots")
    c_values = np.asarray([row["c"] for row in rows], dtype=float)
    state = np.asarray(
        [
            np.interp(
                float(c_value),
                c_values,
                [row["child"]["initial_state"][index] for row in rows],
            )
            for index in range(3)
        ],
        dtype=float,
    )
    period = float(
        np.interp(float(c_value), c_values, [row["child"]["period_time"] for row in rows])
    )
    return state, period


def _half_period_closure(parameters, orbit, solver):
    integration = solve_ivp(
        lambda time_value, state: rossler_rhs(time_value, state, parameters),
        (0.0, 0.5 * orbit.period_time),
        orbit.initial_state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not integration.success:
        raise RuntimeError(f"half-period integration failed: {integration.message}")
    return float(np.linalg.norm(integration.y[:, -1] - orbit.initial_state))


def _attempt(parameters, seed, source_name, solver, manifest):
    try:
        child = _correct(
            parameters,
            seed[0],
            seed[1],
            solver,
            manifest["corrector"],
        )
    except RuntimeError as error:
        return None, {"source": source_name, "success": False, "message": str(error)}
    half_closure = _half_period_closure(parameters, child[0], solver)
    return child, {
        "source": source_name,
        "success": True,
        "half_period_closure": half_closure,
        "closure_error": float(child[1].closure_error),
    }


def _surface_row_lookup(surface_receipt):
    return {
        (float(line["offset_a"]), float(row["c"])): row
        for line in surface_receipt["lines"]
        for row in line["rows"]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--normal-form-receipt", type=Path, required=True)
    parser.add_argument("--failed-surface-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-12 surface-recovery manifest")
    event_bytes = args.event_receipt.read_bytes()
    normal_form_bytes = args.normal_form_receipt.read_bytes()
    failed_surface_bytes = args.failed_surface_receipt.read_bytes()
    for value, key, label in (
        (event_bytes, "event_receipt_sha256", "event"),
        (normal_form_bytes, "normal_form_receipt_sha256", "normal-form"),
        (failed_surface_bytes, "failed_surface_receipt_sha256", "failed-surface"),
    ):
        if sha256_bytes(value) != manifest[key]:
            raise SystemExit(f"{label} receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("period-12 surface recovery requires clean source")
    event_receipt = json.loads(event_bytes)
    normal_form_receipt = json.loads(normal_form_bytes)
    failed_surface = json.loads(failed_surface_bytes)
    if not event_receipt.get("passed") or not normal_form_receipt.get("passed"):
        raise SystemExit("event and normal-form receipts must have passed")
    if failed_surface.get("passed"):
        raise SystemExit("surface-recovery source must be the failed EXP-210 receipt")
    event_lookup = {float(row["c"]): row for row in event_receipt["rows"]}
    source_rows = _surface_row_lookup(failed_surface)
    c_values = [float(value) for value in manifest["c_values"]]
    offsets = [float(value) for value in manifest["offset_a_values"]]
    reference_solver = SolverConfig(**manifest["reference_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    control_c = {float(value) for value in manifest["independent_controls"]["c_values"]}
    control_offsets = {
        float(value) for value in manifest["independent_controls"]["offset_a_values"]
    }
    selection_gate = float(manifest["selection"]["minimum_half_period_closure"])
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    lines = []
    for offset_a in offsets:
        rows = []
        child_objects = []
        child_dense = []
        for c_value in c_values:
            event = event_lookup[c_value]
            parameters = RosslerParameters(
                a=float(event["a"]) + offset_a,
                b=float(manifest["fixed_b"]),
                c=c_value,
            )
            parent = _correct(
                parameters,
                np.asarray(event["initial_state"], dtype=float),
                float(event["period_time"]),
                reference_solver,
                manifest["corrector"],
            )
            attempts = []
            candidates = []
            primary_seed = interpolate_normal_form_seed(
                normal_form_receipt, c_value, offset_a
            )
            child, attempt = _attempt(
                parameters,
                primary_seed,
                "interpolated-exp209",
                reference_solver,
                manifest,
            )
            attempts.append(attempt)
            if child is not None:
                candidates.append((child, attempt))
            if child is None or attempt["half_period_closure"] < selection_gate:
                source_row = source_rows[(offset_a, c_value)]
                fallback_seeds = [
                    (
                        np.asarray(source_row["child"]["initial_state"], dtype=float),
                        float(source_row["child"]["period_time"]),
                        "exp210-cell",
                    ),
                    (
                        *interpolate_passing_surface_seed(
                            failed_surface, c_value, offset_a
                        ),
                        "interpolated-exp210-passing",
                    ),
                ]
                for state, period, source_name in fallback_seeds:
                    fallback, fallback_attempt = _attempt(
                        parameters,
                        (state, period),
                        source_name,
                        reference_solver,
                        manifest,
                    )
                    attempts.append(fallback_attempt)
                    if fallback is not None:
                        candidates.append((fallback, fallback_attempt))
            if not candidates:
                raise RuntimeError("all identity-constrained child corrections failed")
            child, selected_attempt = max(
                candidates,
                key=lambda item: float(item[1].get("half_period_closure", -np.inf)),
            )
            diagnostics = _row_diagnostics(
                parameters, parent, child, reference_solver, manifest
            )
            radau = None
            if c_value in control_c and offset_a in control_offsets:
                radau = _radau_check(
                    parameters,
                    (parent, child),
                    diagnostics,
                    independent_solver,
                    manifest,
                )
            serializable = {
                key: value for key, value in diagnostics.items() if key != "dense"
            }
            serializable.update(
                {
                    "c": c_value,
                    "event_a": float(event["a"]),
                    "a": parameters.a,
                    "offset_a": offset_a,
                    "selected_seed_source": selected_attempt["source"],
                    "selection_attempts": attempts,
                    "independent_radau": radau,
                }
            )
            serializable["passed"] = bool(
                selected_attempt["half_period_closure"] >= selection_gate
                and _row_passes(serializable, acceptance, manifest["identity"])
            )
            rows.append(serializable)
            child_objects.append(child[0])
            child_dense.append(diagnostics["dense"]["child"])
        for index in range(len(rows)):
            rows[index]["adjacent_child_identity"] = None
            if index:
                rows[index]["adjacent_child_identity"] = phase_aligned_rms(
                    (child_objects[index - 1], child_dense[index - 1]),
                    (child_objects[index], child_dense[index]),
                    phase_samples=int(manifest["comparison"]["phase_samples"]),
                    coarse_shifts=int(manifest["comparison"]["coarse_shifts"]),
                    shift_tolerance=float(manifest["comparison"]["shift_tolerance"]),
                )
        lines.append({"offset_a": offset_a, "rows": rows})

    by_c = []
    for c_value in c_values:
        rows = [
            next(row for row in line["rows"] if float(row["c"]) == c_value)
            for line in lines
        ]
        by_c.append(
            {
                "c": c_value,
                "opening_power_law": fit_power_law(
                    [row["offset_a"] for row in rows],
                    [row["opening_identity"]["rms"] for row in rows],
                ),
            }
        )
    all_rows = [row for line in lines for row in line["rows"]]
    adjacent = [
        row["adjacent_child_identity"]["rms"]
        for row in all_rows
        if row["adjacent_child_identity"] is not None
    ]
    radau_rows = [row["independent_radau"] for row in all_rows if row["independent_radau"]]
    passed = bool(
        len(all_rows) == int(acceptance["required_surface_points"])
        and all(row["passed"] for row in all_rows)
        and all(
            float(acceptance["minimum_opening_exponent"])
            <= row["opening_power_law"]["exponent"]
            <= float(acceptance["maximum_opening_exponent"])
            and row["opening_power_law"]["r_squared"]
            >= float(acceptance["minimum_opening_r_squared"])
            for row in by_c
        )
        and max(adjacent) <= float(acceptance["maximum_adjacent_child_identity_rms"])
        and len(radau_rows) == int(acceptance["required_independent_controls"])
        and all(
            max(item["rms"] for item in row["solver_identities"].values())
            <= float(acceptance["maximum_solver_identity_rms"])
            and max(row["multiplier_modulus_differences"].values())
            <= float(acceptance["maximum_solver_modulus_difference"])
            and max(row["period_relative_differences"].values())
            <= float(acceptance["maximum_solver_period_relative_difference"])
            for row in radau_rows
        )
    )
    output = {
        "schema": "butterfly.jones-period12-surface-recovery-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "normal_form_receipt_sha256": sha256_bytes(normal_form_bytes),
        "failed_surface_receipt_sha256": sha256_bytes(failed_surface_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "c_values": c_values,
        "offset_a_values": offsets,
        "lines": lines,
        "opening_fits_by_c": by_c,
        "surface_point_count": len(all_rows),
        "maximum_adjacent_child_identity_rms": max(adjacent),
        "fallback_cell_count": sum(
            row["selected_seed_source"] != "interpolated-exp209" for row in all_rows
        ),
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
                "surface_points": len(all_rows),
                "fallback_cells": output["fallback_cell_count"],
                "opening_exponent_range": [
                    min(row["opening_power_law"]["exponent"] for row in by_c),
                    max(row["opening_power_law"]["exponent"] for row in by_c),
                ],
                "minimum_opening_r_squared": min(
                    row["opening_power_law"]["r_squared"] for row in by_c
                ),
                "maximum_adjacent_child_identity_rms": max(adjacent),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
