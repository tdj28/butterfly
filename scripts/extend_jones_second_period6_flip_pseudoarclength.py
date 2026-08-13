#!/usr/bin/env python3
"""Broadly continue the distinct second period-6 flip in both directions."""

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
from scripts.extend_jones_period6_flip_pseudoarclength import (
    _correct,
    _diagnose,
    _independent_control,
    _variables,
)


SCHEMA = "butterfly.jones-second-period6-flip-pseudoarclength-manifest.v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--local-receipt", type=Path, required=True)
    parser.add_argument("--source-arm-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported second-flip pseudo-arclength manifest")
    local_bytes = args.local_receipt.read_bytes()
    source_arm_bytes = args.source_arm_receipt.read_bytes()
    if sha256_bytes(local_bytes) != manifest["local_receipt_sha256"]:
        raise SystemExit("local receipt hash mismatch")
    if sha256_bytes(source_arm_bytes) != manifest["source_arm_receipt_sha256"]:
        raise SystemExit("source-arm receipt hash mismatch")
    local = json.loads(local_bytes)
    source_arm = json.loads(source_arm_bytes)
    if not local.get("passed") or not source_arm.get("passed"):
        raise SystemExit("broad continuation requires passed local and source curves")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("second-flip pseudo-arclength requires clean source")

    local_rows = sorted(local["rows"], key=lambda row: float(row["c"]))
    arm_rows = sorted(source_arm["rows"], key=lambda row: float(row["c"]))
    arm_c = np.asarray([row["c"] for row in arm_rows], dtype=float)
    arm_a = np.asarray([row["a"] for row in arm_rows], dtype=float)
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    continuation = manifest["continuation"]
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    directions = {}

    for name, seeds in (
        ("down", (local_rows[1], local_rows[0])),
        ("up", (local_rows[-2], local_rows[-1])),
    ):
        points = [_variables(seed) for seed in seeds]
        if np.dot(points[0][6:], points[1][6:]) < 0.0:
            points[0][6:] *= -1.0
        step_length = float(continuation["step_scale"]) * float(
            np.linalg.norm(points[1] - points[0])
        )
        rows = []
        statuses = []
        message = "completed requested steps"
        previous_row = seeds[-1]
        for step_index in range(int(continuation["steps_per_direction"])):
            secant = points[-1] - points[-2]
            secant /= np.linalg.norm(secant)
            predictor = points[-1] + step_length * secant
            try:
                corrected, status = _correct(
                    predictor, secant, points[-1], manifest, solver
                )
                row = _diagnose(corrected, status, manifest, solver)
            except Exception as error:
                message = f"{type(error).__name__}: {error}"
                break
            status["step_index"] = step_index
            statuses.append(status)
            row["source_arm_a"] = float(np.interp(row["c"], arm_c, arm_a))
            row["source_arm_a_separation"] = row["a"] - row["source_arm_a"]
            row["source_arm_separation_passed"] = bool(
                arm_c[0] <= row["c"] <= arm_c[-1]
                and row["source_arm_a_separation"]
                <= -float(acceptance["minimum_source_arm_a_separation"])
            )
            row["jump_passed"] = bool(
                abs(float(row["a"]) - float(previous_row["a"]))
                <= float(acceptance["maximum_adjacent_a_jump"])
                and abs(float(row["c"]) - float(previous_row["c"]))
                <= float(acceptance["maximum_adjacent_c_jump"])
            )
            row["passed"] = bool(
                all(row["checks"].values())
                and row["source_arm_separation_passed"]
                and row["jump_passed"]
            )
            if not row["passed"]:
                message = "corrected event failed invariant, separation, or jump gates"
                break
            points.append(corrected)
            rows.append(row)
            previous_row = row
        directions[name] = {
            "step_length": step_length,
            "rows": rows,
            "statuses": statuses,
            "message": message,
        }

    controls = []
    for name in ("down", "up"):
        if directions[name]["rows"]:
            controls.append(
                {
                    "direction": name,
                    **_independent_control(
                        directions[name]["rows"][-1], manifest, independent_solver
                    ),
                }
            )
    all_rows = directions["down"]["rows"] + directions["up"]["rows"]
    c_values = [float(row["c"]) for row in all_rows]
    separations = [float(row["source_arm_a_separation"]) for row in all_rows]
    passed = bool(
        all(
            len(directions[name]["rows"])
            == int(continuation["steps_per_direction"])
            for name in ("down", "up")
        )
        and min(c_values, default=float("inf"))
        <= float(acceptance["required_minimum_c"])
        and max(c_values, default=float("-inf"))
        >= float(acceptance["required_maximum_c"])
        and all(row["passed"] for row in all_rows)
        and len(controls) == 2
        and all(
            control["row_passed"]
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
        "schema": "butterfly.jones-second-period6-flip-pseudoarclength-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "local_receipt_sha256": sha256_bytes(local_bytes),
        "source_arm_receipt_sha256": sha256_bytes(source_arm_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "directions": directions,
        "new_point_count": len(all_rows),
        "c_range": [min(c_values), max(c_values)] if c_values else [None, None],
        "a_range": [min(row["a"] for row in all_rows), max(row["a"] for row in all_rows)] if all_rows else [None, None],
        "source_arm_a_separation_range": [min(separations), max(separations)] if separations else [None, None],
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
                "new_point_count": len(all_rows),
                "c_range": output["c_range"],
                "a_range": output["a_range"],
                "source_arm_a_separation_range": output[
                    "source_arm_a_separation_range"
                ],
                "direction_messages": {
                    name: directions[name]["message"] for name in directions
                },
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
