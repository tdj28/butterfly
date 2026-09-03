#!/usr/bin/env python3
"""Extend the verified period-10 child without section-count identity gates."""
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
from pseudo_arclength_periodic_b import correct_arclength, diagnose


def variables(row):
    return np.r_[row["initial_state"], row["period_time"], row["b"]]


def half_period_closure(row, solver):
    parameters = RosslerParameters(a=row["a"], b=row["b"], c=row["c"])
    state = np.asarray(row["initial_state"], dtype=float)
    result = solve_ivp(
        lambda t, x: rossler_rhs(t, x, parameters),
        (0.0, 0.5 * row["period_time"]),
        state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    return float(np.linalg.norm(result.y[:, -1] - state))


def unit_crossings(rows, maximum_imaginary_part):
    events = []
    for target in (-1.0, 1.0):
        for left, right in zip(rows[:-1], rows[1:]):
            lm = left["significant_multiplier"]
            rm = right["significant_multiplier"]
            if max(abs(lm["imag"]), abs(rm["imag"])) > maximum_imaginary_part:
                continue
            if (lm["real"] - target) * (rm["real"] - target) <= 0.0:
                events.append(
                    {
                        "target": target,
                        "b_bracket": sorted([left["b"], right["b"]]),
                        "left_multiplier": lm,
                        "right_multiplier": rm,
                    }
                )
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--branch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    branch_bytes = args.branch.read_bytes()
    if sha256_bytes(branch_bytes) != manifest["branch_receipt_sha256"]:
        raise SystemExit("branch receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    prior = json.loads(branch_bytes)
    branch = next(
        item
        for item in prior["branches"]
        if item["direction"] == manifest["source_direction"]
    )
    seed_rows = branch["rows"][-2:]
    points = [variables(row) for row in seed_rows]
    a = float(seed_rows[-1]["a"])
    c = float(seed_rows[-1]["c"])
    solver = SolverConfig(**manifest["solver"])
    rows = []
    for row in seed_rows:
        diagnosed = diagnose(variables(row), a=a, c=c, solver=solver)
        diagnosed["seed"] = True
        diagnosed["half_period_closure"] = half_period_closure(diagnosed, solver)
        rows.append(diagnosed)
    statuses = []
    nominal_step = float(manifest["continuation"]["nominal_step"])
    minimum_step = float(manifest["continuation"]["minimum_step"])
    growth = float(manifest["continuation"]["growth_factor"])
    step_length = nominal_step
    started = time.perf_counter()
    for step_index in range(int(manifest["continuation"]["maximum_steps"])):
        tangent = points[-1] - points[-2]
        tangent /= np.linalg.norm(tangent)
        accepted = False
        trial_step = step_length
        while trial_step >= minimum_step:
            predictor = points[-1] + trial_step * tangent
            corrected, status = correct_arclength(
                predictor,
                tangent,
                points[-1][:3],
                float(points[-1][4]),
                a=a,
                c=c,
                solver=solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["max_evaluations"]),
            )
            status.update({"step_index": step_index, "trial_step": trial_step})
            statuses.append(status)
            if status["success"]:
                accepted = True
                break
            trial_step *= 0.5
        if not accepted:
            break
        points.append(corrected)
        row = diagnose(corrected, a=a, c=c, solver=solver)
        row["seed"] = False
        row["corrector"] = status
        row["half_period_closure"] = half_period_closure(row, solver)
        rows.append(row)
        step_length = min(nominal_step, trial_step * growth)
        if not (
            manifest["continuation"]["b_guard"][0]
            <= corrected[4]
            <= manifest["continuation"]["b_guard"][1]
        ):
            break
    b_values = [row["b"] for row in rows]
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.period10-child-extension.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "branch_receipt_sha256": sha256_bytes(branch_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_a": a,
        "fixed_c": c,
        "rows": rows,
        "statuses": statuses,
        "point_count": len(rows),
        "b_range": [min(b_values), max(b_values)],
        "unit_multiplier_candidates": unit_crossings(
            rows, manifest["diagnostics"]["maximum_imaginary_part"]
        ),
        "max_closure_error": max(row["closure_error"] for row in rows),
        "minimum_half_period_closure": min(
            row["half_period_closure"] for row in rows
        ),
        "elapsed_seconds": time.perf_counter() - started,
    }
    output["passed"] = (
        len(rows) >= acceptance["minimum_points"]
        and max(b_values) - min(b_values) >= acceptance["minimum_b_span"]
        and output["max_closure_error"] <= acceptance["max_closure_error"]
        and output["minimum_half_period_closure"]
        >= acceptance["minimum_half_period_closure"]
    )
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {key: value for key, value in output.items() if key not in ("rows", "statuses")},
            sort_keys=True,
        )
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
