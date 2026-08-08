#!/usr/bin/env python3
"""Qualify published chaotic saddles with independent PIM straddles."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import io
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    advance_pim_straddle,
    barrio_rossler_section,
    capture_lifetimes_on_section,
    classify_fundamental_period,
    collect_crossings,
    infer_return_map_branches_robust,
    refine_pim_segment,
    section_return_map,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _measure_lifetime(argument):
    parameters, section, cycle, capture, pim, solver, point = argument
    measured = capture_lifetimes_on_section(
        parameters,
        np.asarray(point, dtype=np.float64)[None, :],
        section,
        cycle,
        capture_coordinate_axes=tuple(capture["coordinate_axes"]),
        capture_coordinate_scales=tuple(capture["coordinate_scales"]),
        capture_radius=float(capture["radius"]),
        required_capture_crossings=int(capture["required_crossings"]),
        maximum_returns=int(pim["maximum_escape_returns"]),
        config=solver,
        maximum_flight_time=float(pim["maximum_flight_time"]),
    )
    return (
        float(measured.lifetimes[0]),
        bool(measured.captured[0]),
        bool(measured.failed[0]),
        int(measured.return_counts[0]),
    )


class LifetimeEvaluator:
    """Memoized adaptive capture-time oracle with explicit censor tracking."""

    def __init__(self, parameters, section, cycle, manifest, solver):
        self.parameters = parameters
        self.section = section
        self.cycle = cycle
        self.capture = manifest["capture"]
        self.pim = manifest["pim"]
        self.solver = solver
        self.cache: dict[bytes, tuple[float, bool, bool, int]] = {}
        self.request_count = 0
        self.integration_count = 0
        self.executor = ProcessPoolExecutor(
            max_workers=int(self.pim["lifetime_workers"])
        )

    def close(self):
        self.executor.shutdown(wait=True)

    def __call__(self, points):
        points = np.asarray(points, dtype=np.float64)
        self.request_count += len(points)
        keys = [point.tobytes() for point in points]
        missing_indices = [
            index for index, key in enumerate(keys) if key not in self.cache
        ]
        if missing_indices:
            missing = points[missing_indices]
            measured = [None] * len(missing)
            futures = {}
            for local, point in enumerate(missing):
                argument = (
                    self.parameters,
                    self.section,
                    self.cycle,
                    self.capture,
                    self.pim,
                    self.solver,
                    point,
                )
                futures[self.executor.submit(_measure_lifetime, argument)] = local
            self.integration_count += len(missing)
            terminal_error = None
            for future in as_completed(futures):
                local = futures[future]
                value = future.result()
                measured[local] = value
                source_index = missing_indices[local]
                self.cache[keys[source_index]] = value
                if value[2]:
                    terminal_error = "PIM lifetime integration failed"
                    break
                if not value[1]:
                    terminal_error = (
                        "PIM lifetime evaluation reached the frozen 256-return "
                        "censor limit"
                    )
                    break
            if terminal_error is not None:
                for future in futures:
                    future.cancel()
                raise RuntimeError(terminal_error)
            assert all(value is not None for value in measured)
        return np.asarray([self.cache[key][0] for key in keys], dtype=np.float64)

    def diagnostics_since(self, keys_before):
        new = [value for key, value in self.cache.items() if key not in keys_before]
        return {
            "unique_lifetime_evaluations": len(new),
            "censored_evaluations": sum(not value[1] and not value[2] for value in new),
            "failed_evaluations": sum(value[2] for value in new),
            "maximum_return_count": max((value[3] for value in new), default=0),
            "maximum_lifetime": max((value[0] for value in new), default=0.0),
        }


def _cycle_reference(parameters, section, manifest, solver):
    declared = manifest["cycle_reference"]
    crossings = collect_crossings(
        parameters,
        manifest["cycle_initial_state"],
        section,
        transient=float(declared["transient"]),
        observation_horizon=float(declared["observation_horizon"]),
        max_crossings=int(declared["max_crossings"]),
        config=solver,
    )
    classification = classify_fundamental_period(
        crossings.states, **declared["recurrence"]
    )
    return crossings, classification


def _combined_critical_spans(coordinate_row, cpu_reference):
    pim_intervals = coordinate_row["robust_oracle"]["critical_point_intervals"]
    cpu_intervals = cpu_reference["critical_point_intervals"]
    if len(pim_intervals) != len(cpu_intervals):
        return {
            "resolved": False,
            "critical_point_intervals": [],
            "normalized_spans": [],
            "maximum_normalized_span": 1e300,
        }
    domain_minimum = min(
        coordinate_row["source_minimum"], cpu_reference["source_minimum"]
    )
    domain_maximum = max(
        coordinate_row["source_maximum"], cpu_reference["source_maximum"]
    )
    domain_range = max(domain_maximum - domain_minimum, np.finfo(float).eps)
    intervals = []
    spans = []
    for pim, cpu in zip(pim_intervals, cpu_intervals, strict=True):
        lower = min(pim[0], cpu[0])
        upper = max(pim[1], cpu[1])
        intervals.append((lower, upper))
        spans.append((upper - lower) / domain_range)
    return {
        "resolved": True,
        "critical_point_intervals": intervals,
        "normalized_spans": spans,
        "maximum_normalized_span": max(spans, default=0.0),
    }


def _run_case(case, manifest, solver):
    fixed = manifest["fixed_parameters"]
    parameters = RosslerParameters(
        a=float(case["a"]), b=float(fixed["b"]), c=float(fixed["c"])
    )
    section = barrio_rossler_section(parameters)
    cycle_crossings, cycle_classification = _cycle_reference(
        parameters, section, manifest, solver
    )
    stable_period = int(case["stable_period"])
    cycle = cycle_crossings.states[-stable_period:]
    evaluator = LifetimeEvaluator(parameters, section, cycle, manifest, solver)
    pim = manifest["pim"]
    scales = np.asarray(pim["state_coordinate_scales"], dtype=np.float64)
    successful_states = []
    line_rows = []
    state_artifacts = {}

    def mapped(points):
        states, _times, success = section_return_map(
            parameters,
            points,
            section,
            config=solver,
            maximum_flight_time=float(pim["maximum_flight_time"]),
        )
        if not np.all(success):
            raise RuntimeError("one or more PIM triple points failed to return")
        return states

    for line in pim["initial_segments"]:
        left = np.asarray(
            (section.offset, float(line["y_range"][0]), float(line["z"])),
            dtype=np.float64,
        )
        right = np.asarray(
            (section.offset, float(line["y_range"][1]), float(line["z"])),
            dtype=np.float64,
        )
        keys_before = set(evaluator.cache)
        started = time.perf_counter()
        try:
            initial = refine_pim_segment(
                left,
                right,
                evaluator,
                coordinate_scales=scales,
                sample_count=int(pim["refinement_sample_count"]),
                width_tolerance=float(pim["width_tolerance"]),
                max_refinements=int(pim["maximum_initial_refinements"]),
            )
            straddle = advance_pim_straddle(
                initial.triple,
                mapped,
                evaluator,
                coordinate_scales=scales,
                return_count=int(pim["straddle_returns"]),
                sample_count=int(pim["refinement_sample_count"]),
                width_tolerance=float(pim["width_tolerance"]),
                max_refinements_per_event=int(
                    pim["maximum_refinements_per_event"]
                ),
            )
            retained = straddle.states[int(pim["burn_in_returns"]) :]
            successful_states.append(retained)
            state_artifacts[line["id"]] = straddle.states
            row = {
                "id": line["id"],
                "resolved": True,
                "initial_refinement_count": initial.refinement_count,
                "initial_widths": initial.normalized_widths.tolist(),
                "straddle_return_count": len(straddle.states),
                "retained_return_count": len(retained),
                "refinement_event_count": len(straddle.refinement_events),
                "maximum_recorded_width": float(
                    np.max(straddle.normalized_widths)
                ),
                "elapsed_seconds": time.perf_counter() - started,
            }
        except (RuntimeError, ValueError) as error:
            row = {
                "id": line["id"],
                "resolved": False,
                "reason": str(error),
                "elapsed_seconds": time.perf_counter() - started,
            }
        row["lifetime_diagnostics"] = evaluator.diagnostics_since(keys_before)
        line_rows.append(row)
        print(
            json.dumps(
                {
                    "case": case["id"],
                    "line": line["id"],
                    "resolved": row["resolved"],
                    "reason": row.get("reason"),
                    "elapsed_seconds": row["elapsed_seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    evaluator.close()

    coordinate_rows = {}
    acceptance = manifest["acceptance"]
    expected = int(case["expected_saddle_branch_count"])
    for coordinate in manifest["coordinates"]:
        axis = int(coordinate["axis"])
        sources = [states[:-1, axis] for states in successful_states]
        targets = [states[1:, axis] for states in successful_states]
        source = np.concatenate(sources) if sources else np.empty(0)
        target = np.concatenate(targets) if targets else np.empty(0)
        if len(source) >= int(acceptance["minimum_return_pairs"]):
            robust = asdict(
                infer_return_map_branches_robust(
                    source,
                    target,
                    variants=manifest["oracle_variants"],
                    common_options=manifest["oracle_common"],
                    minimum_variant_consensus=float(
                        acceptance["minimum_oracle_variant_consensus"]
                    ),
                    maximum_normalized_critical_point_span=float(
                        acceptance["maximum_within_pim_critical_span"]
                    ),
                )
            )
        else:
            robust = {
                "resolved": False,
                "branch_count": None,
                "critical_point_intervals": (),
                "maximum_normalized_critical_point_span": 1e300,
                "variant_consensus": 0.0,
                "reason": "insufficient PIM return pairs",
            }
        row = {
            "pair_count": len(source),
            "source_minimum": float(np.min(source)) if len(source) else None,
            "source_maximum": float(np.max(source)) if len(source) else None,
            "robust_oracle": robust,
        }
        if len(source):
            row["cpu_comparison"] = _combined_critical_spans(
                row, case["cpu_reference"][coordinate["name"]]
            )
        else:
            row["cpu_comparison"] = {
                "resolved": False,
                "maximum_normalized_span": 1e300,
            }
        coordinate_rows[coordinate["name"]] = row

    successful_lines = sum(row["resolved"] for row in line_rows)
    censor_count = sum(
        row["lifetime_diagnostics"]["censored_evaluations"] for row in line_rows
    )
    failure_count = sum(
        row["lifetime_diagnostics"]["failed_evaluations"] for row in line_rows
    )
    case_passed = (
        cycle_classification.fundamental_period == stable_period
        and successful_lines >= int(acceptance["minimum_successful_straddles"])
        and censor_count <= int(acceptance["maximum_censored_lifetime_evaluations"])
        and failure_count == 0
        and all(
            row["pair_count"] >= int(acceptance["minimum_return_pairs"])
            and row["robust_oracle"]["resolved"]
            and row["robust_oracle"]["branch_count"] == expected
            and row["cpu_comparison"]["resolved"]
            and row["cpu_comparison"]["maximum_normalized_span"]
            <= float(acceptance["maximum_cpu_pim_critical_span"])
            for row in coordinate_rows.values()
        )
    )
    return (
        {
            "id": case["id"],
            "parameters": asdict(parameters),
            "expected_saddle_branch_count": expected,
            "stable_cycle_classification": asdict(cycle_classification),
            "lines": line_rows,
            "successful_straddles": successful_lines,
            "censored_lifetime_evaluations": censor_count,
            "failed_lifetime_evaluations": failure_count,
            "coordinates": coordinate_rows,
            "passed": case_passed,
        },
        state_artifacts,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states-output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.pim-saddle-controls-manifest.v1":
        raise SystemExit("unsupported PIM-saddle manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["reference_solver"])
    cases = []
    arrays = {}
    started = time.perf_counter()
    for case in manifest["cases"]:
        row, state_artifacts = _run_case(case, manifest, solver)
        cases.append(row)
        for line_id, states in state_artifacts.items():
            arrays[f"{case['id']}__{line_id}"] = states
    state_buffer = io.BytesIO()
    np.savez_compressed(state_buffer, **arrays)
    state_bytes = state_buffer.getvalue()
    atomic_write(args.states_output, state_bytes)
    receipt = {
        "schema": "butterfly.pim-saddle-controls-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "lifetime_workers": int(manifest["pim"]["lifetime_workers"]),
        },
        "states_artifact": str(args.states_output),
        "states_artifact_bytes": len(state_bytes),
        "states_artifact_sha256": sha256_bytes(state_bytes),
        "cases": cases,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(case["passed"] for case in cases),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True), flush=True)
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
