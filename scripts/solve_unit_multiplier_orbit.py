#!/usr/bin/env python3
"""Solve a periodic orbit and nontrivial +1 Floquet condition together."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import SolverConfig, correct_unit_multiplier_orbit
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.unit-multiplier-manifest.v1":
        raise SystemExit("unsupported unit-multiplier manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash does not match manifest")
    source_receipt = json.loads(source_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("unit-multiplier solve requires clean source")

    bracket = list(map(float, manifest["source_b_bracket"]))
    rows = source_receipt["rows"]
    seed_row = min(
        rows,
        key=lambda row: abs(float(row["b"]) - sum(bracket) / 2.0),
    )
    started = time.perf_counter()
    result = correct_unit_multiplier_orbit(
        a=float(manifest["fixed_a"]),
        c=float(manifest["fixed_c"]),
        initial_b=float(seed_row["b"]),
        initial_state=seed_row["initial_state"],
        period_time=float(seed_row["period_time"]),
        config=SolverConfig(**manifest["solver"]),
        max_evaluations=int(manifest["corrector"]["max_evaluations"]),
        tolerance=float(manifest["corrector"]["tolerance"]),
    )
    multiplier_rows = [
        {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
        for value in result.multipliers
    ]
    acceptance = manifest["acceptance"]
    in_bracket = bracket[0] <= result.b <= bracket[1]
    passed = bool(
        result.success
        and in_bracket
        and result.closure_error <= float(acceptance["max_closure_error"])
        and result.eigen_residual <= float(acceptance["max_eigen_residual"])
        and result.flow_orthogonality_residual
        <= float(acceptance["max_flow_orthogonality_residual"])
    )
    receipt = {
        "schema": "butterfly.unit-multiplier-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_a": float(manifest["fixed_a"]),
        "fixed_c": float(manifest["fixed_c"]),
        "source_b_bracket": bracket,
        "seed_b": float(seed_row["b"]),
        "corrected_b": result.b,
        "initial_state": result.initial_state.tolist(),
        "period_time": result.period_time,
        "event_eigenvector": result.eigenvector.tolist(),
        "closure_error": result.closure_error,
        "phase_residual": result.phase_residual,
        "eigen_residual": result.eigen_residual,
        "normalization_residual": result.normalization_residual,
        "flow_orthogonality_residual": result.flow_orthogonality_residual,
        "multipliers": multiplier_rows,
        "evaluations": result.evaluations,
        "solver_success": result.success,
        "in_source_bracket": in_bracket,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "Locates a nontrivial +1 event while excluding the flow-neutral mode; generic classification requires explicit second-branch continuation.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
