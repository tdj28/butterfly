#!/usr/bin/env python3
"""Audit manifold-match cells by residual winding and return continuity."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-homoclinic-residual-cell-audit-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def winding_number(vectors: np.ndarray) -> tuple[int, float, float]:
    vectors = np.asarray(vectors, dtype=np.float64)
    if vectors.shape != (4, 2):
        raise ValueError("four two-dimensional corner vectors required")
    if np.any(np.linalg.norm(vectors, axis=1) == 0.0):
        raise ValueError("zero corner residual requires direct-root handling")
    total = 0.0
    for index in range(4):
        first = vectors[index]
        second = vectors[(index + 1) % 4]
        total += math.atan2(
            float(first[0] * second[1] - first[1] * second[0]),
            float(np.dot(first, second)),
        )
    winding = int(round(total / (2.0 * math.pi)))
    closure_error = abs(total - winding * 2.0 * math.pi)
    return winding, total, closure_error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported residual-cell audit manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    binding = manifest["source_receipt"]
    source_path = Path(binding["path"])
    if sha256_file(source_path) != binding["sha256"]:
        raise SystemExit("source receipt hash mismatch")
    receipt = json.loads(source_path.read_bytes())
    expected = binding["expected"]
    for field in ("schema", "experiment_id", "classification", "candidate_count", "nominated_cell_count"):
        expected_value = binding[field] if field in binding else expected[field]
        if receipt.get(field) != expected_value:
            raise SystemExit(f"source receipt binding mismatch: {field}")
    closest = receipt["closest_match"]
    for field, value in expected["closest_match"].items():
        if closest.get(field) != value:
            raise SystemExit(f"source closest-match binding mismatch: {field}")

    rows = receipt["rows"]
    c_count = len(receipt["c_values"])
    angle_count = len(receipt["angles"])
    lookup = {(row["c_index"], row["angle_index"]): row for row in rows}
    audited_cells = []
    for c_index in range(c_count - 1):
        for angle_index in range(angle_count):
            corner_indices = [
                (c_index, angle_index),
                (c_index, (angle_index + 1) % angle_count),
                (c_index + 1, (angle_index + 1) % angle_count),
                (c_index + 1, angle_index),
            ]
            corners = [lookup[index] for index in corner_indices]
            if not all(row["status"] in {"completed", "candidate"} for row in corners):
                continue
            branch_signs = {row["stable_branch_sign"] for row in corners}
            if len(branch_signs) != 1:
                continue
            residuals = np.asarray([row["tangent_residual"] for row in corners])
            winding, total_angle, closure_error = winding_number(residuals)
            times = np.asarray([row["inward_crossing_time_after_exit"] for row in corners])
            hull_contains_zero = all(
                float(np.min(residuals[:, axis])) <= 0.0 <= float(np.max(residuals[:, axis]))
                for axis in (0, 1)
            )
            audited_cells.append(
                {
                    "lower_c_index": c_index,
                    "lower_angle_index": angle_index,
                    "corner_indices": [list(index) for index in corner_indices],
                    "stable_branch_sign": next(iter(branch_signs)),
                    "hull_contains_zero": hull_contains_zero,
                    "winding_number": winding,
                    "total_residual_angle": total_angle,
                    "winding_closure_error": closure_error,
                    "crossing_time_spread": float(np.ptp(times)),
                    "minimum_corner_chord_mismatch": min(row["chord_mismatch"] for row in corners),
                    "maximum_corner_chord_mismatch": max(row["chord_mismatch"] for row in corners),
                }
            )

    hull_cells = [cell for cell in audited_cells if cell["hull_contains_zero"]]
    degree_cells = [cell for cell in audited_cells if cell["winding_number"] != 0]
    continuous_degree_cells = [
        cell
        for cell in degree_cells
        if cell["crossing_time_spread"]
        <= float(manifest["continuity"]["maximum_corner_crossing_time_spread"])
    ]
    source_hull_indices = sorted(
        (cell["lower_c_index"], cell["lower_angle_index"])
        for cell in receipt["nominated_cells"]
    )
    audited_hull_indices = sorted(
        (cell["lower_c_index"], cell["lower_angle_index"]) for cell in hull_cells
    )
    acceptance = manifest["acceptance"]
    checks = {
        "source_passed": receipt["passed"] is True,
        "row_count": len(rows) == c_count * angle_count,
        "audited_cells_present": len(audited_cells) > 0,
        "reproduces_source_hull_cells": audited_hull_indices == source_hull_indices,
        "finite_cell_observables": all(
            np.isfinite(cell["total_residual_angle"])
            and np.isfinite(cell["crossing_time_spread"])
            for cell in audited_cells
        ),
        "winding_closure": all(
            cell["winding_closure_error"]
            <= float(acceptance["maximum_winding_closure_error"])
            for cell in audited_cells
        ),
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "source_receipt": {
            "experiment_id": receipt["experiment_id"],
            "sha256": binding["sha256"],
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "audited_cell_count": len(audited_cells),
        "hull_cell_count": len(hull_cells),
        "hull_cells": hull_cells,
        "degree_cell_count": len(degree_cells),
        "degree_cells": degree_cells,
        "continuous_degree_cell_count": len(continuous_degree_cells),
        "continuous_degree_cells": continuous_degree_cells,
        "classification": (
            "continuous_degree_cell_nominated"
            if continuous_degree_cells
            else "degree_cell_without_time_continuity"
            if degree_cells
            else "hull_nominations_rejected_by_winding"
        ),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
