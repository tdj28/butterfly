#!/usr/bin/env python3
"""Reclassify EXP-242 spectra without the near-zero eigenvalue identity swap."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period24-flip-scan-reclassification-manifest.v1"


def nontrivial_eigenvalues(row: dict) -> list[complex]:
    values = row["floquet"]["direct_products"][0]["eigenvalues"]
    eigenvalues = np.asarray(
        [complex(value["real"], value["imag"]) for value in values], dtype=complex
    )
    neutral = int(np.argmin(np.abs(eigenvalues - 1.0)))
    return [complex(value) for index, value in enumerate(eigenvalues) if index != neutral]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-24 scan reclassification manifest")
    scan_bytes = args.scan.read_bytes()
    if sha256_bytes(scan_bytes) != manifest["scan_receipt_sha256"]:
        raise SystemExit("scan receipt hash mismatch")
    scan = json.loads(scan_bytes)
    if scan.get("schema") != manifest["scan_schema"] or scan.get("passed"):
        raise SystemExit("bound scan must be the failed EXP-242 receipt")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    rows = []
    for source_row in scan["rows"]:
        values = sorted(nontrivial_eigenvalues(source_row), key=abs, reverse=True)
        tracked, collapsed = values
        rows.append(
            {
                "index": int(source_row["index"]),
                "a": float(source_row["a"]),
                "tracked_multiplier": {
                    "real": float(tracked.real),
                    "imag": float(tracked.imag),
                    "modulus": float(abs(tracked)),
                },
                "collapsed_multiplier_modulus": float(abs(collapsed)),
                "modulus_separation_ratio": float(abs(tracked) / max(abs(collapsed), 1e-300)),
                "flip_residual": float(tracked.real + 1.0),
            }
        )
    imaginary_limit = float(manifest["acceptance"]["maximum_multiplier_imaginary"])
    brackets = []
    for left, right in zip(rows[:-1], rows[1:]):
        if max(abs(left["tracked_multiplier"]["imag"]), abs(right["tracked_multiplier"]["imag"])) > imaginary_limit:
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
        and len(brackets) == int(acceptance["required_flip_brackets"])
        and min(row["modulus_separation_ratio"] for row in rows)
        >= float(acceptance["minimum_modulus_separation_ratio"])
        and max(abs(row["tracked_multiplier"]["imag"]) for row in rows)
        <= imaginary_limit
        and rows[0]["tracked_multiplier"]["modulus"]
        <= float(acceptance["maximum_initial_multiplier_modulus"])
        and rows[-1]["tracked_multiplier"]["real"]
        <= float(acceptance["maximum_terminal_multiplier_real"])
    )
    output = {
        "schema": "butterfly.jones-period24-flip-scan-reclassification-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "scan_receipt_sha256": sha256_bytes(scan_bytes),
        "source": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__},
        "rows": rows,
        "flip_brackets": brackets,
        "minimum_modulus_separation_ratio": min(row["modulus_separation_ratio"] for row in rows),
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
