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
}


def transverse_values(floquet: dict) -> list[complex]:
    values = floquet["direct_products"][0]["eigenvalues"]
    eigenvalues = np.asarray(
        [complex(row["real"], row["imag"]) for row in values], dtype=complex
    )
    neutral = int(np.argmin(np.abs(eigenvalues - 1.0)))
    return [complex(value) for index, value in enumerate(eigenvalues) if index != neutral]


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
    if not continuation.get("passed"):
        raise SystemExit("a passed period-24 continuation is required")
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
    for index, source_row in enumerate(continuation["rows"]):
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
            "modulus_separation_ratio": modulus_separation_ratio,
            "cyclic_dominant_real_spread": float(
                max(value.real for value in cyclic)
                - min(value.real for value in cyclic)
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
    imaginary_limit = float(manifest["acceptance"]["maximum_multiplier_imaginary"])
    for left, right in zip(rows[:-1], rows[1:]):
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
    acceptance = manifest["acceptance"]
    passed = bool(
        len(rows) == int(acceptance["required_points"])
        and len(brackets) >= int(acceptance["minimum_flip_brackets"])
        and max(row["matching_residual"] for row in rows)
        <= float(acceptance["maximum_matching_residual"])
        and max(abs(row["tracked_multiplier"]["imag"]) for row in rows)
        <= imaginary_limit
        and rows[0]["tracked_multiplier"]["modulus"]
        <= float(acceptance["maximum_initial_multiplier_modulus"])
        and rows[-1]["tracked_multiplier"]["real"]
        <= float(acceptance["maximum_terminal_multiplier_real"])
        and (
            manifest.get("tracking_method") != "magnitude_separated"
            or min(row["modulus_separation_ratio"] for row in rows)
            >= float(acceptance["minimum_modulus_separation_ratio"])
        )
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
