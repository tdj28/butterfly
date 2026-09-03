#!/usr/bin/env python3
"""Extend one accepted pseudo-arclength flip-surface slice from a prior receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from pseudo_arclength_unit_event import correct_event_arclength


def variables(row: dict) -> np.ndarray:
    return np.concatenate(
        (
            np.asarray(row["initial_state"], dtype=float),
            (float(row["period_time"]), float(row["a"]), float(row["b"])),
            np.asarray(row["event_eigenvector"], dtype=float),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-slices", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.flip-surface-slice-extension-manifest.v1":
        raise SystemExit("unsupported flip-surface slice extension manifest")
    source_bytes = args.source_slices.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_slices_receipt_sha256"]:
        raise SystemExit("source slices receipt hash does not match manifest")
    prior = json.loads(source_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("slice extension requires clean source")

    c = float(manifest["fixed_c"])
    prior_slice = next(row for row in prior["slices"] if abs(float(row["c"]) - c) < 1e-12)
    points = [variables(row) for row in prior_slice["rows"][-2:]]
    step_length = float(prior_slice["step_length"])
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    continuation = manifest["continuation"]
    acceptance = manifest["acceptance"]
    new_rows = []
    statuses = []
    started = time.perf_counter()
    for step_index in range(int(continuation["steps"])):
        tangent = points[-1] - points[-2]
        tangent /= np.linalg.norm(tangent)
        predictor = points[-1] + step_length * tangent
        corrected, status = correct_event_arclength(
            predictor,
            tangent,
            points[-1],
            c=c,
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )
        status["step_index"] = step_index
        statuses.append(status)
        if not status["success"]:
            break
        if np.dot(corrected[6:9], points[-1][6:9]) < 0.0:
            corrected[6:9] *= -1.0
        points.append(corrected)
        new_rows.append(
            {
                "initial_state": corrected[:3].tolist(),
                "period_time": float(corrected[3]),
                "a": float(corrected[4]),
                "b": float(corrected[5]),
                "c": c,
                "event_eigenvector": corrected[6:9].tolist(),
                **status,
            }
        )
        a_guard = list(map(float, continuation["a_guard"]))
        b_guard = list(map(float, continuation["b_guard"]))
        if not (
            a_guard[0] <= corrected[4] <= a_guard[1]
            and b_guard[0] <= corrected[5] <= b_guard[1]
        ):
            break

    combined = prior_slice["rows"] + new_rows
    b_values = np.asarray([row["b"] for row in combined], dtype=float)
    b_differences = np.diff(b_values)
    b_reversals = int(np.sum(b_differences[:-1] * b_differences[1:] < 0.0))
    max_closure = max((row["closure_error"] for row in new_rows), default=float("inf"))
    max_eigen = max((row["eigen_residual"] for row in new_rows), default=float("inf"))
    max_orthogonality = max(
        (row["flow_orthogonality_residual"] for row in new_rows), default=float("inf")
    )
    max_arclength = max(
        (row["arclength_residual"] for row in new_rows), default=float("inf")
    )
    receipt = {
        "schema": "butterfly.flip-surface-slice-extension-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_slices_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_c": c,
        "step_length": step_length,
        "new_rows": new_rows,
        "statuses": statuses,
        "new_point_count": len(new_rows),
        "combined_point_count": len(combined),
        "combined_b_range": [float(np.min(b_values)), float(np.max(b_values))],
        "combined_b_reversals": b_reversals,
        "combined_minimum_b_row": min(combined, key=lambda row: float(row["b"])),
        "max_closure_error": max_closure,
        "max_eigen_residual": max_eigen,
        "max_flow_orthogonality_residual": max_orthogonality,
        "max_arclength_residual": max_arclength,
        "elapsed_seconds": time.perf_counter() - started,
    }
    receipt["passed"] = bool(
        len(new_rows) >= int(acceptance["minimum_new_points"])
        and b_reversals >= int(acceptance["minimum_combined_b_reversals"])
        and max_closure <= float(acceptance["max_closure_error"])
        and max_eigen <= float(acceptance["max_eigen_residual"])
        and max_orthogonality
        <= float(acceptance["max_flow_orthogonality_residual"])
        and max_arclength <= float(acceptance["max_arclength_residual"])
    )
    receipt["interpretation_limit"] = "Completing one boundary slice resolves local fold persistence across the five sampled c values, not global surface connectivity."
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key not in ("new_rows", "statuses", "combined_minimum_b_row")}, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
