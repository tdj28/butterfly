#!/usr/bin/env python3
"""Continue the period-6 flip curve through the EXP-214 section grazing."""

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
from scripts.continue_jones_period6_flip_curve import _solve_event
from scripts.extend_jones_period6_flip_pseudoarclength import (
    _correct,
    _diagnose,
    _variables,
)
from scripts.qualify_jones_period6_flip_extremum_count import (
    extremum_partitioned_legacy_count,
)
from scripts.refine_jones_period6_flip_section_grazing import (
    _scientific_event_passes,
)


SCHEMA = "butterfly.jones-period6-flip-through-grazing-manifest.v1"


def _invariant_row_passes(row):
    return all(
        value
        for name, value in row["checks"].items()
        if name != "historical_section"
    )


def _extremum_count(row, solver):
    parameters = RosslerParameters(a=row["a"], b=row["b"], c=row["c"])
    return extremum_partitioned_legacy_count(
        parameters,
        np.asarray(row["initial_state"], dtype=float),
        float(row["period_time"]),
        solver,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--extension-receipt", type=Path, required=True)
    parser.add_argument("--grazing-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported through-grazing manifest")
    extension_bytes = args.extension_receipt.read_bytes()
    grazing_bytes = args.grazing_receipt.read_bytes()
    if sha256_bytes(extension_bytes) != manifest["extension_receipt_sha256"]:
        raise SystemExit("extension receipt hash mismatch")
    if sha256_bytes(grazing_bytes) != manifest["grazing_receipt_sha256"]:
        raise SystemExit("grazing receipt hash mismatch")
    extension = json.loads(extension_bytes)
    grazing = json.loads(grazing_bytes)
    if not grazing.get("passed"):
        raise SystemExit("extremum-aware grazing receipt must have passed")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("through-grazing continuation requires clean source")

    source_rows = extension["directions"]["down"]["rows"]
    points = [_variables(row) for row in source_rows[-2:]]
    if np.dot(points[0][6:], points[1][6:]) < 0.0:
        points[0][6:] *= -1.0
    continuation = manifest["continuation"]
    step_length = float(continuation["step_scale"]) * np.linalg.norm(
        points[1] - points[0]
    )
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    acceptance = manifest["acceptance"]
    rows = []
    statuses = []
    message = "completed requested steps"
    started = time.perf_counter()
    for step_index in range(int(continuation["steps"])):
        secant = points[-1] - points[-2]
        secant /= np.linalg.norm(secant)
        predictor = points[-1] + step_length * secant
        try:
            corrected, status = _correct(
                predictor, secant, points[-1], manifest, solver
            )
        except Exception as error:
            message = f"{type(error).__name__}: {error}"
            break
        status["step_index"] = step_index
        statuses.append(status)
        row = _diagnose(corrected, status, manifest, solver)
        row["extremum_partitioned"] = _extremum_count(row, solver)
        row["invariant_passed"] = _invariant_row_passes(row)
        row["passed"] = bool(
            row["invariant_passed"]
            and row["barrio_phase_count"] == int(acceptance["barrio_phase_count"])
            and row["extremum_partitioned"]["count"]
            == int(acceptance["historical_extremum_count"])
            and row["extremum_partitioned"]["maximum_section_residual"]
            <= float(acceptance["maximum_section_residual"])
        )
        if not row["passed"]:
            message = "corrected point failed invariant or section-identity checks"
            break
        points.append(corrected)
        rows.append(row)

    independent = None
    if rows:
        terminal = rows[-1]
        corrected = _solve_event(
            terminal["c"],
            {
                "a": terminal["a"],
                "initial_state": terminal["initial_state"],
                "period_time": terminal["period_time"],
                "tangent": terminal["tangent"],
            },
            manifest,
            independent_solver,
        )
        corrected["extremum_partitioned"] = _extremum_count(
            {
                "a": corrected["a"],
                "b": corrected["b"],
                "c": corrected["c"],
                "initial_state": corrected["initial_state"],
                "period_time": corrected["period_time"],
            },
            independent_solver,
        )
        independent = {
            "corrected": corrected,
            "scientific_event_passed": _scientific_event_passes(corrected),
            "a_difference": abs(corrected["a"] - terminal["a"]),
            "period_relative_difference": abs(
                corrected["period_time"] - terminal["period_time"]
            )
            / terminal["period_time"],
            "state_difference": float(
                np.linalg.norm(
                    np.asarray(corrected["initial_state"], dtype=float)
                    - np.asarray(terminal["initial_state"], dtype=float)
                )
            ),
            "multiplier_modulus_difference": abs(
                corrected["dominant_multiplier"]["modulus"]
                - terminal["dominant_multiplier"]["modulus"]
            ),
        }
    adjacent_a = [
        abs(right["a"] - left["a"])
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]
    adjacent_c = [
        abs(right["c"] - left["c"])
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]
    passed = bool(
        len(rows) == int(continuation["steps"])
        and rows[-1]["c"] <= float(acceptance["required_maximum_terminal_c"])
        and max(adjacent_a) <= float(acceptance["maximum_adjacent_a_jump"])
        and max(adjacent_c) <= float(acceptance["maximum_adjacent_c_jump"])
        and independent is not None
        and independent["scientific_event_passed"]
        and independent["corrected"]["barrio_phase_count"]
        == int(acceptance["barrio_phase_count"])
        and independent["corrected"]["extremum_partitioned"]["count"]
        == int(acceptance["historical_extremum_count"])
        and independent["a_difference"]
        <= float(acceptance["maximum_solver_a_difference"])
        and independent["period_relative_difference"]
        <= float(acceptance["maximum_solver_period_relative_difference"])
        and independent["state_difference"]
        <= float(acceptance["maximum_solver_state_difference"])
        and independent["multiplier_modulus_difference"]
        <= float(acceptance["maximum_solver_modulus_difference"])
    )
    output = {
        "schema": "butterfly.jones-period6-flip-through-grazing-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "extension_receipt_sha256": sha256_bytes(extension_bytes),
        "grazing_receipt_sha256": sha256_bytes(grazing_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "step_length": step_length,
        "rows": rows,
        "statuses": statuses,
        "message": message,
        "point_count": len(rows),
        "c_range": [min(row["c"] for row in rows), max(row["c"] for row in rows)]
        if rows
        else [None, None],
        "a_range": [min(row["a"] for row in rows), max(row["a"] for row in rows)]
        if rows
        else [None, None],
        "maximum_adjacent_a_jump": max(adjacent_a, default=float("inf")),
        "maximum_adjacent_c_jump": max(adjacent_c, default=float("inf")),
        "independent_radau": independent,
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
                "message": message,
                "historical_counts": sorted(
                    {row["extremum_partitioned"]["count"] for row in rows}
                ),
                "barrio_counts": sorted({row["barrio_phase_count"] for row in rows}),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
