#!/usr/bin/env python3
"""Track the period-24 Floquet branch along EXP-239 and bracket its next flip."""

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
from audit_segmented_floquet_precision import block_and_product_floquet


SCHEMAS = {
    "butterfly.jones-period24-segmented-flip-scan-manifest.v1",
    "butterfly.jones-period48-segmented-flip-scan-manifest.v1",
    "butterfly.jones-period96-segmented-flip-scan-manifest.v1",
    "butterfly.jones-period192-segmented-flip-scan-manifest.v1",
    "butterfly.jones-period384-segmented-flip-scan-manifest.v1",
    "butterfly.jones-period768-segmented-flip-scan-manifest.v1",
    "butterfly.jones-period1536-segmented-flip-scan-manifest.v1",
}


def transverse_values(floquet: dict) -> list[complex]:
    values = floquet["direct_products"][0]["eigenvalues"]
    eigenvalues = np.asarray(
        [complex(row["real"], row["imag"]) for row in values], dtype=complex
    )
    neutral = int(np.argmin(np.abs(eigenvalues - 1.0)))
    return [complex(value) for index, value in enumerate(eigenvalues) if index != neutral]


def selected_source_rows(continuation: dict, manifest: dict) -> list[dict]:
    """Return either a passed continuation or an explicitly allowed exact prefix."""

    if continuation.get("passed"):
        return continuation["rows"]
    if not manifest.get("allow_failed_continuation_prefix", False):
        raise ValueError("a passed period-24 continuation is required")
    maximum_step = int(manifest["maximum_source_step_index"])
    rows = [
        row
        for row in continuation.get("rows", [])
        if int(row["step_index"]) <= maximum_step
    ]
    if not rows or int(rows[-1]["step_index"]) != maximum_step:
        raise ValueError("failed continuation does not contain the frozen prefix")
    if not all(row["status"]["success"] for row in rows):
        raise ValueError("failed continuation prefix contains an unsuccessful row")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in SCHEMAS:
        raise SystemExit("unsupported period-24 flip-scan manifest")
    continuation_bytes = args.continuation.read_bytes()
    if sha256_bytes(continuation_bytes) != manifest["continuation_receipt_sha256"]:
        raise SystemExit("continuation receipt hash mismatch")
    continuation = json.loads(continuation_bytes)
    try:
        source_rows = selected_source_rows(continuation, manifest)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    solver = SolverConfig(**manifest["solver"])
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    cyclic_shifts = manifest["cyclic_shifts"]
    rows = []
    previous = None
    started = time.perf_counter()
    for index, source_row in enumerate(source_rows):
        nodes = np.asarray(source_row["nodes"], dtype=float)
        parameters = RosslerParameters(
            a=float(source_row["a"]), b=fixed_b, c=fixed_c
        )
        floquet = block_and_product_floquet(
            nodes,
            float(source_row["period_time"]),
            parameters,
            solver,
            cyclic_shifts,
        )
        values = transverse_values(floquet)
        if manifest.get("tracking_method") == "magnitude_separated":
            ordered = sorted(values, key=abs, reverse=True)
            tracked = ordered[0]
            collapsed = ordered[1]
            modulus_separation_ratio = float(
                abs(tracked) / max(abs(collapsed), 1e-300)
            )
        elif previous is None:
            tracked = max(values, key=abs)
            modulus_separation_ratio = None
        elif manifest.get("tracking_method") == "dominant_modulus":
            tracked = max(values, key=abs)
            modulus_separation_ratio = None
        else:
            tracked = min(values, key=lambda value: abs(value - previous))
            modulus_separation_ratio = None
        previous = tracked
        cyclic = [
            complex(
                item["dominant_nontrivial_multiplier"]["real"],
                item["dominant_nontrivial_multiplier"]["imag"],
            )
            for item in floquet["direct_products"]
        ]
        row = {
            "index": index,
            "a": float(source_row["a"]),
            "period_time": float(source_row["period_time"]),
            "half_node_rms": float(source_row["half_node_rms"]),
            "matching_residual": float(source_row["status"]["matching_residual"]),
            "tracked_multiplier": {
                "real": float(tracked.real),
                "imag": float(tracked.imag),
                "modulus": float(abs(tracked)),
            },
            "flip_residual": float(tracked.real + 1.0),
            "fold_residual": float(tracked.real - 1.0),
            "stability_residual": float(abs(tracked) - 1.0),
            "modulus_separation_ratio": modulus_separation_ratio,
            "cyclic_dominant_real_spread": float(
                max(value.real for value in cyclic)
                - min(value.real for value in cyclic)
            ),
            "cyclic_dominant_modulus_relative_spread": float(
                (max(abs(value) for value in cyclic) - min(abs(value) for value in cyclic))
                / max(abs(value) for value in cyclic)
            ),
            "floquet": floquet,
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "index": index,
                    "a": row["a"],
                    "tracked_multiplier": row["tracked_multiplier"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    brackets = []
    fold_brackets = []
    stability_brackets = []
    imaginary_limit = float(manifest["acceptance"]["maximum_multiplier_imaginary"])
    for left, right in zip(rows[:-1], rows[1:]):
        if left["stability_residual"] * right["stability_residual"] <= 0.0:
            stability_brackets.append(
                {
                    "left_index": left["index"],
                    "right_index": right["index"],
                    "a_bracket": sorted([left["a"], right["a"]]),
                    "left_multiplier": left["tracked_multiplier"],
                    "right_multiplier": right["tracked_multiplier"],
                }
            )
        if max(
            abs(left["tracked_multiplier"]["imag"]),
            abs(right["tracked_multiplier"]["imag"]),
        ) > imaginary_limit:
            continue
        if left["flip_residual"] * right["flip_residual"] <= 0.0:
            brackets.append(
                {
                    "left_index": left["index"],
                    "right_index": right["index"],
                    "a_bracket": sorted([left["a"], right["a"]]),
                    "left_multiplier": left["tracked_multiplier"],
                    "right_multiplier": right["tracked_multiplier"],
                }
            )
        if left["fold_residual"] * right["fold_residual"] <= 0.0:
            fold_brackets.append(
                {
                    "left_index": left["index"],
                    "right_index": right["index"],
                    "a_bracket": sorted([left["a"], right["a"]]),
                    "left_multiplier": left["tracked_multiplier"],
                    "right_multiplier": right["tracked_multiplier"],
                }
            )
    acceptance = manifest["acceptance"]
    passed = bool(
        len(rows) == int(acceptance["required_points"])
        and len(stability_brackets)
        >= int(acceptance.get("minimum_stability_brackets", 0))
        and len(brackets) >= int(acceptance.get("minimum_flip_brackets", 0))
        and max(row["matching_residual"] for row in rows)
        <= float(acceptance["maximum_matching_residual"])
        and (
            manifest.get("tracking_method") == "dominant_modulus"
            or max(abs(row["tracked_multiplier"]["imag"]) for row in rows)
            <= imaginary_limit
        )
        and rows[0]["tracked_multiplier"]["modulus"]
        <= float(acceptance["maximum_initial_multiplier_modulus"])
        and (
            "maximum_terminal_multiplier_real" not in acceptance
            or rows[-1]["tracked_multiplier"]["real"]
            <= float(acceptance["maximum_terminal_multiplier_real"])
        )
        and (
            "minimum_terminal_multiplier_modulus" not in acceptance
            or rows[-1]["tracked_multiplier"]["modulus"]
            >= float(acceptance["minimum_terminal_multiplier_modulus"])
        )
        and (
            manifest.get("tracking_method") != "magnitude_separated"
            or min(row["modulus_separation_ratio"] for row in rows)
            >= float(acceptance["minimum_modulus_separation_ratio"])
        )
        and max(row["cyclic_dominant_modulus_relative_spread"] for row in rows)
        <= float(acceptance.get("maximum_cyclic_modulus_relative_spread", 1.0))
    )
    output = {
        "schema": manifest.get(
            "output_schema",
            "butterfly.jones-period24-segmented-flip-scan-receipt.v1",
        ),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "continuation_receipt_sha256": sha256_bytes(continuation_bytes),
        "source": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__},
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "rows": rows,
        "flip_brackets": brackets,
        "fold_brackets": fold_brackets,
        "stability_brackets": stability_brackets,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    printed = {**output, "rows": [{key: value for key, value in row.items() if key != "floquet"} for row in rows]}
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
