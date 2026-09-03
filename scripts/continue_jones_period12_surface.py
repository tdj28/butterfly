#!/usr/bin/env python3
"""Continue a dense fixed-offset period-12 surface patch from EXP-209."""

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
from scripts.compare_periodic_orbit_identity import phase_aligned_rms
from scripts.qualify_jones_period12_normal_form import (
    _correct,
    _radau_check,
    _row_diagnostics,
    fit_power_law,
)


SCHEMA = "butterfly.jones-period12-surface-manifest.v1"


def select_child_seed(normal_form_receipt, c_value, offset_a):
    targets = [
        target
        for target in normal_form_receipt["targets"]
        if float(target["c"]) == float(c_value)
    ]
    if len(targets) != 1:
        raise ValueError("seed c must select exactly one normal-form target")
    row = min(
        targets[0]["rows"],
        key=lambda item: abs(float(item["offset_a"]) - float(offset_a)),
    )
    return np.asarray(row["child"]["initial_state"], dtype=float), float(
        row["child"]["period_time"]
    )


def _section_counts_pass(row, identity):
    expected = {
        "parent_historical": int(identity["historical_parent_phase_count"]),
        "parent_barrio": int(identity["barrio_parent_phase_count"]),
        "child_historical": int(identity["historical_child_phase_count"]),
        "child_barrio": int(identity["barrio_child_phase_count"]),
    }
    return all(
        row["section_counts"][name]["count"] == count
        and row["section_counts"][name]["integration_success"]
        for name, count in expected.items()
    )


def _row_passes(row, acceptance, identity):
    return bool(
        row["parent"]["closure_error"] <= float(acceptance["maximum_closure_error"])
        and row["child"]["closure_error"] <= float(acceptance["maximum_closure_error"])
        and row["parent"]["dominant_transverse_multiplier"]["real"]
        <= -float(acceptance["minimum_parent_multiplier_modulus"])
        and row["child"]["dominant_transverse_multiplier"]["modulus"]
        <= float(acceptance["maximum_child_multiplier_modulus"])
        and abs(row["parent"]["dominant_transverse_multiplier"]["imag"])
        <= float(acceptance["maximum_multiplier_imaginary_part"])
        and abs(row["child"]["dominant_transverse_multiplier"]["imag"])
        <= float(acceptance["maximum_multiplier_imaginary_part"])
        and abs(row["period_ratio"] - 2.0)
        <= float(acceptance["maximum_period_ratio_error"])
        and row["minimum_proper_subperiod_closure"]
        >= float(acceptance["minimum_proper_subperiod_closure"])
        and float(acceptance["minimum_multiplier_ratio"])
        <= row["flip_multiplier_ratio"]
        <= float(acceptance["maximum_multiplier_ratio"])
        and _section_counts_pass(row, identity)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--normal-form-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-12 surface manifest")
    event_bytes = args.event_receipt.read_bytes()
    normal_form_bytes = args.normal_form_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(normal_form_bytes) != manifest["normal_form_receipt_sha256"]:
        raise SystemExit("normal-form receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("period-12 surface continuation requires clean source")
    event_receipt = json.loads(event_bytes)
    normal_form_receipt = json.loads(normal_form_bytes)
    if not event_receipt.get("passed") or not normal_form_receipt.get("passed"):
        raise SystemExit("source experiment receipts must have passed")
    event_lookup = {float(row["c"]): row for row in event_receipt["rows"]}
    c_values = [float(value) for value in manifest["c_values"]]
    if any(value not in event_lookup for value in c_values):
        raise SystemExit("surface c grid must be an exact subset of EXP-206")
    offsets = [float(value) for value in manifest["offset_a_values"]]
    reference_solver = SolverConfig(**manifest["reference_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    control_c = {float(value) for value in manifest["independent_controls"]["c_values"]}
    control_offsets = {
        float(value) for value in manifest["independent_controls"]["offset_a_values"]
    }
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    lines = []
    for offset_a in offsets:
        child_seed = select_child_seed(normal_form_receipt, c_values[0], offset_a)
        previous_child = None
        previous_dense = None
        rows = []
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
            child = _correct(
                parameters,
                child_seed[0],
                child_seed[1],
                reference_solver,
                manifest["corrector"],
            )
            diagnostics = _row_diagnostics(
                parameters, parent, child, reference_solver, manifest
            )
            adjacent_identity = None
            if previous_child is not None:
                adjacent_identity = phase_aligned_rms(
                    (previous_child, previous_dense),
                    (child[0], diagnostics["dense"]["child"]),
                    phase_samples=int(manifest["comparison"]["phase_samples"]),
                    coarse_shifts=int(manifest["comparison"]["coarse_shifts"]),
                    shift_tolerance=float(manifest["comparison"]["shift_tolerance"]),
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
                    "adjacent_child_identity": adjacent_identity,
                    "independent_radau": radau,
                }
            )
            serializable["passed"] = _row_passes(
                serializable, acceptance, manifest["identity"]
            )
            rows.append(serializable)
            previous_child = child[0]
            previous_dense = diagnostics["dense"]["child"]
            child_seed = (child[0].initial_state, child[0].period_time)
        lines.append({"offset_a": offset_a, "rows": rows})

    by_c = []
    for c_value in c_values:
        rows = [
            next(row for row in line["rows"] if float(row["c"]) == c_value)
            for line in lines
        ]
        fit = fit_power_law(
            [row["offset_a"] for row in rows],
            [row["opening_identity"]["rms"] for row in rows],
        )
        by_c.append({"c": c_value, "opening_power_law": fit})
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
        "schema": "butterfly.jones-period12-surface-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "normal_form_receipt_sha256": sha256_bytes(normal_form_bytes),
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
