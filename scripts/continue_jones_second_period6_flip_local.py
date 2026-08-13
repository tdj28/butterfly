#!/usr/bin/env python3
"""Resolve the EXP-226 second period-6 flip as a local fixed-c curve."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.bridge_jones_returning_period12_child import interpolate_event
from scripts.continue_jones_period6_flip_curve import _solve_event


SCHEMA = "butterfly.jones-second-period6-flip-local-manifest.v1"


def solver_control(reference, manifest, solver):
    """Independently correct one local event row at fixed c."""

    corrected = _solve_event(
        float(reference["c"]),
        {
            "a": reference["a"],
            "initial_state": reference["initial_state"],
            "period_time": reference["period_time"],
            "tangent": reference["tangent"],
        },
        manifest,
        solver,
    )
    return {
        "c": float(reference["c"]),
        "passed": bool(corrected["passed"]),
        "a_difference": abs(float(corrected["a"]) - float(reference["a"])),
        "period_relative_difference": abs(
            float(corrected["period_time"]) - float(reference["period_time"])
        )
        / float(reference["period_time"]),
        "state_difference": float(
            np.linalg.norm(
                np.asarray(corrected["initial_state"], dtype=float)
                - np.asarray(reference["initial_state"], dtype=float)
            )
        ),
        "multiplier_modulus_difference": abs(
            float(corrected["dominant_multiplier"]["modulus"])
            - float(reference["dominant_multiplier"]["modulus"])
        ),
        "corrected": corrected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--endpoint-receipt", type=Path, required=True)
    parser.add_argument("--source-arm-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported second-flip local-curve manifest")
    endpoint_bytes = args.endpoint_receipt.read_bytes()
    source_arm_bytes = args.source_arm_receipt.read_bytes()
    if sha256_bytes(endpoint_bytes) != manifest["endpoint_receipt_sha256"]:
        raise SystemExit("endpoint receipt hash mismatch")
    if sha256_bytes(source_arm_bytes) != manifest["source_arm_receipt_sha256"]:
        raise SystemExit("source-arm receipt hash mismatch")
    endpoint = json.loads(endpoint_bytes)
    source_arm = json.loads(source_arm_bytes)
    if not endpoint.get("passed") or not source_arm.get("passed"):
        raise SystemExit("local curve requires passed endpoint and source arm")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("second-flip local continuation requires clean source")

    center_source = endpoint["root_results"][manifest["center_solver"]]["root"]
    center_c = float(center_source["c"])
    center_seed = {
        "a": float(center_source["a"]),
        "initial_state": center_source["summary"]["initial_state"],
        "period_time": center_source["summary"]["period_time"],
    }
    grid = manifest["grid"]
    c_values = np.linspace(
        center_c + float(grid["minimum_offset"]),
        center_c + float(grid["maximum_offset"]),
        int(grid["count"]),
    )
    center_indices = np.flatnonzero(np.isclose(c_values, center_c, atol=1e-15, rtol=0.0))
    if len(center_indices) != 1:
        raise SystemExit("frozen grid does not contain exactly one center")
    center_index = int(center_indices[0])

    source_interval = manifest["source_interval"]
    source_rows = {float(row["c"]): row for row in source_arm["rows"]}
    source_left = source_rows[float(source_interval["left_c"])]
    source_right = source_rows[float(source_interval["right_c"])]

    def source_event_at(c_value):
        fraction = (float(c_value) - float(source_left["c"])) / (
            float(source_right["c"]) - float(source_left["c"])
        )
        return interpolate_event(source_left, source_right, fraction)

    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    rows_by_index = {}
    direction_status = {}
    started = time.perf_counter()
    try:
        center = _solve_event(center_c, center_seed, manifest, solver)
        center["source_arm_a"] = float(source_event_at(center_c)["a"])
        center["source_arm_a_separation"] = center["a"] - center["source_arm_a"]
        rows_by_index[center_index] = center
    except Exception as error:
        center = None
        direction_status["center"] = {
            "completed": False,
            "message": f"{type(error).__name__}: {error}",
        }

    if center is not None:
        direction_status["center"] = {
            "completed": bool(center["passed"]),
            "message": "completed" if center["passed"] else "center failed gates",
        }
        for name, indices in (
            ("down", range(center_index - 1, -1, -1)),
            ("up", range(center_index + 1, len(c_values))),
        ):
            previous = center
            completed = True
            message = "completed"
            for index in indices:
                try:
                    row = _solve_event(float(c_values[index]), previous, manifest, solver)
                except Exception as error:
                    completed = False
                    message = f"{type(error).__name__}: {error}"
                    break
                row["source_arm_a"] = float(source_event_at(row["c"])["a"])
                row["source_arm_a_separation"] = row["a"] - row["source_arm_a"]
                rows_by_index[index] = row
                previous = row
                if not row["passed"]:
                    completed = False
                    message = "point failed exact event gates"
                    break
            direction_status[name] = {"completed": completed, "message": message}

    rows = [rows_by_index[index] for index in sorted(rows_by_index)]
    controls = []
    for index in manifest["independent_control_indices"]:
        index = int(index)
        if index in rows_by_index:
            controls.append(
                {"index": index, **solver_control(rows_by_index[index], manifest, independent_solver)}
            )
    adjacent_a = [
        abs(float(right["a"]) - float(left["a"]))
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]
    separations = [float(row["source_arm_a_separation"]) for row in rows]
    acceptance = manifest["acceptance"]
    center_a_difference = (
        abs(float(center["a"]) - float(center_source["a"]))
        if center is not None
        else float("inf")
    )
    passed = bool(
        len(rows) == int(grid["count"])
        and all(row["passed"] for row in rows)
        and all(status["completed"] for status in direction_status.values())
        and center_a_difference <= float(acceptance["maximum_center_a_difference"])
        and max(adjacent_a, default=float("inf"))
        <= float(acceptance["maximum_adjacent_a_jump"])
        and all(
            separation <= -float(acceptance["minimum_source_arm_a_separation"])
            for separation in separations
        )
        and len(controls) == len(manifest["independent_control_indices"])
        and all(
            control["passed"]
            and control["a_difference"]
            <= float(acceptance["maximum_solver_a_difference"])
            and control["period_relative_difference"]
            <= float(acceptance["maximum_solver_period_relative_difference"])
            and control["state_difference"]
            <= float(acceptance["maximum_solver_state_difference"])
            and control["multiplier_modulus_difference"]
            <= float(acceptance["maximum_solver_modulus_difference"])
            for control in controls
        )
    )
    output = {
        "schema": "butterfly.jones-second-period6-flip-local-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "endpoint_receipt_sha256": sha256_bytes(endpoint_bytes),
        "source_arm_receipt_sha256": sha256_bytes(source_arm_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "center_source": center_source,
        "center_a_difference": center_a_difference,
        "rows": rows,
        "point_count": len(rows),
        "direction_status": direction_status,
        "c_range": [min(row["c"] for row in rows), max(row["c"] for row in rows)] if rows else [None, None],
        "a_range": [min(row["a"] for row in rows), max(row["a"] for row in rows)] if rows else [None, None],
        "source_arm_a_separation_range": [min(separations), max(separations)] if separations else [None, None],
        "maximum_adjacent_a_jump": max(adjacent_a, default=float("inf")),
        "independent_controls": controls,
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
                "point_count": len(rows),
                "c_range": output["c_range"],
                "a_range": output["a_range"],
                "source_arm_a_separation_range": output[
                    "source_arm_a_separation_range"
                ],
                "direction_status": direction_status,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
