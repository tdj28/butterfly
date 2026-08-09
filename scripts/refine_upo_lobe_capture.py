#!/usr/bin/env python3
"""Refine shortlisted UPO-lobe capture shifts across orbit phases."""

from __future__ import annotations

import argparse
import json
import platform
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    next_section_return,
    project_floquet_direction_to_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from trace_upo_unstable_lobe_atlas import _stable_cycle, _trace_task


def _advance(parameters, section, state, count, solver, maximum_flight_time):
    current = np.asarray(state, dtype=float)
    for _ in range(count):
        result = next_section_return(
            parameters,
            current,
            section,
            config=solver,
            maximum_flight_time=maximum_flight_time,
        )
        if not result.success:
            raise RuntimeError(result.message)
        current = result.state
    return current


def _phase_offsets(lag, fractions):
    offsets = [min(lag - 1, int(np.floor(float(value) * lag))) for value in fractions]
    if len(set(offsets)) != len(offsets):
        raise ValueError(f"phase fractions do not produce unique offsets for lag {lag}")
    return offsets


def _transport_direction(seed, sign, phase_offset, parameters, manifest, solver):
    section = barrio_rossler_section(parameters)
    base = np.asarray(seed["base_section_state"], dtype=float)
    direction = sign * np.asarray(seed["section_unstable_direction"], dtype=float)
    epsilon = float(manifest["transport"]["epsilon"])
    maximum_flight_time = float(manifest["maximum_flight_time"])
    phase_base = _advance(
        parameters, section, base, phase_offset, solver, maximum_flight_time
    )
    plus = _advance(
        parameters,
        section,
        base + epsilon * direction,
        phase_offset,
        solver,
        maximum_flight_time,
    )
    minus = _advance(
        parameters,
        section,
        base - epsilon * direction,
        phase_offset,
        solver,
        maximum_flight_time,
    )
    transported = project_floquet_direction_to_section(
        (plus - minus) / (2.0 * epsilon),
        rossler_rhs(0.0, phase_base, parameters),
        section.normal,
        coordinate_scales=manifest["coordinate_scales"],
    )
    lag = int(seed["fundamental_lag"])
    reference_final = _advance(
        parameters, section, phase_base, lag, solver, maximum_flight_time
    )
    validation_epsilon = float(manifest["transport"]["validation_epsilon"])
    perturbed_final = _advance(
        parameters,
        section,
        phase_base + validation_epsilon * transported,
        lag,
        solver,
        maximum_flight_time,
    )
    scales = np.asarray(manifest["coordinate_scales"], dtype=float)
    normal = np.asarray(section.normal, dtype=float)
    axes = np.flatnonzero(np.abs(normal) < 0.5)
    tangent = transported[axes] / scales[axes]
    tangent /= np.linalg.norm(tangent)
    delta = (perturbed_final[axes] - reference_final[axes]) / scales[axes]
    observed = float(np.dot(delta, tangent) / validation_epsilon)
    predicted = float(seed["unstable_multiplier"]["real"])
    relative_error = float(abs(observed - predicted) / abs(predicted))
    transverse = delta - observed * validation_epsilon * tangent
    transverse_ratio = float(
        np.linalg.norm(transverse)
        / max(abs(observed * validation_epsilon), np.finfo(float).tiny)
    )
    passed = bool(
        relative_error
        <= float(manifest["acceptance"]["maximum_transport_multiplier_error"])
        and transverse_ratio
        <= float(manifest["acceptance"]["maximum_transport_transverse_ratio"])
    )
    return {
        "phase_return_offset": phase_offset,
        "base_section_state": phase_base.tolist(),
        "section_direction": transported.tolist(),
        "observed_signed_multiplier": observed,
        "predicted_signed_multiplier": predicted,
        "relative_multiplier_error": relative_error,
        "transverse_residual_ratio": transverse_ratio,
        "passed": passed,
    }


def _restricted_capture_mean(rows, horizon):
    values = [
        min(int(row["capture_start_return"]), horizon)
        if row["captured"] and int(row["computed_returns"]) <= horizon
        else horizon
        for row in rows
    ]
    return float(np.mean(values))


def _summaries(traces, manifest):
    coarse = set(int(value) for value in manifest["seed_grid"]["coarse_indices"])
    administrative = [int(value) for value in manifest["administrative_horizons"]]
    grouped = {}
    for trace in traces:
        key = (trace["family_id"], trace["sign"], trace["phase_index"], trace["case_id"])
        grouped.setdefault(key, []).append(trace)
    phase_case_rows = []
    for key, rows in sorted(grouped.items()):
        rows.sort(key=lambda value: value["amplitude_index"])
        coarse_rows = [row for row in rows if row["amplitude_index"] in coarse]
        means = {
            str(horizon): _restricted_capture_mean(rows, horizon)
            for horizon in administrative
        }
        coarse_means = {
            str(horizon): _restricted_capture_mean(coarse_rows, horizon)
            for horizon in administrative
        }
        maximum_grid_difference = max(
            abs(means[str(horizon)] - coarse_means[str(horizon)])
            for horizon in administrative
        )
        family_id, sign, phase_index, case_id = key
        phase_case_rows.append(
            {
                "family_id": family_id,
                "sign": sign,
                "phase_index": phase_index,
                "case_id": case_id,
                "trajectory_count": len(rows),
                "capture_fraction": float(np.mean([row["captured"] for row in rows])),
                "restricted_capture_means": means,
                "coarse_restricted_capture_means": coarse_means,
                "maximum_coarse_fine_mean_difference": maximum_grid_difference,
                "all_integrations_succeeded": all(
                    row["integration_success"] for row in rows
                ),
                "passed": bool(
                    all(row["integration_success"] for row in rows)
                    and maximum_grid_difference
                    <= float(
                        manifest["acceptance"][
                            "maximum_coarse_fine_restricted_mean_difference"
                        ]
                    )
                ),
            }
        )
    return phase_case_rows


def _candidate_summaries(phase_case_rows, manifest):
    cases = [case["id"] for case in manifest["cases"]]
    lookup = {
        (row["family_id"], row["sign"], row["phase_index"], row["case_id"]): row
        for row in phase_case_rows
    }
    horizons = [int(value) for value in manifest["administrative_horizons"]]
    primary = max(horizons)
    minimum_effect = float(
        manifest["acceptance"]["minimum_absolute_endpoint_mean_difference"]
    )
    output = []
    for candidate in manifest["candidates"]:
        phase_differences = {}
        phase_rows = []
        for phase_index in range(len(manifest["phase_fractions"])):
            left = lookup[(candidate["family_id"], candidate["sign"], phase_index, cases[0])]
            right = lookup[(candidate["family_id"], candidate["sign"], phase_index, cases[1])]
            differences = {
                str(horizon): right["restricted_capture_means"][str(horizon)]
                - left["restricted_capture_means"][str(horizon)]
                for horizon in horizons
            }
            phase_differences[str(phase_index)] = differences
            primary_difference = differences[str(primary)]
            horizon_signs = [np.sign(differences[str(horizon)]) for horizon in horizons]
            phase_rows.append(
                {
                    "phase_index": phase_index,
                    "endpoint_differences": differences,
                    "primary_difference": primary_difference,
                    "grid_passed": left["passed"] and right["passed"],
                    "horizon_direction_consistent": len(set(horizon_signs)) == 1,
                }
            )
        primary_values = [row["primary_difference"] for row in phase_rows]
        if all(value <= -minimum_effect for value in primary_values):
            classification = "earlier_capture_at_three_branch_endpoint"
        elif all(value >= minimum_effect for value in primary_values):
            classification = "later_capture_at_three_branch_endpoint"
        else:
            classification = "phase_inconsistent_or_below_effect_floor"
        passed = bool(
            classification != "phase_inconsistent_or_below_effect_floor"
            and all(row["grid_passed"] for row in phase_rows)
            and all(row["horizon_direction_consistent"] for row in phase_rows)
        )
        output.append(
            {
                "family_id": candidate["family_id"],
                "sign": candidate["sign"],
                "phase_rows": phase_rows,
                "classification": classification,
                "passed": passed,
            }
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.upo-lobe-capture-refinement-manifest.v1":
        raise SystemExit("unsupported UPO lobe-capture refinement manifest")
    seed_bytes = Path(manifest["source_seed_receipt"]["path"]).read_bytes()
    atlas_bytes = Path(manifest["source_atlas_receipt"]["path"]).read_bytes()
    if sha256_bytes(seed_bytes) != manifest["source_seed_receipt"]["sha256"]:
        raise SystemExit("source seed receipt hash mismatch")
    if sha256_bytes(atlas_bytes) != manifest["source_atlas_receipt"]["sha256"]:
        raise SystemExit("source atlas receipt hash mismatch")
    seed_receipt = json.loads(seed_bytes)
    atlas_receipt = json.loads(atlas_bytes)
    selected = [
        {"family_id": row["family_id"], "sign": row["sign"]}
        for row in atlas_receipt["selected_refinement_candidates"]
    ]
    if selected != manifest["candidates"]:
        raise SystemExit("manifest candidates do not match frozen atlas selection")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    solver = SolverConfig(**manifest["reference_solver"])
    transport_solver = SolverConfig(**manifest["transport_solver"])
    cycles = {}
    cycle_audits = []
    for case in manifest["cases"]:
        parameters = RosslerParameters(**case["parameters"])
        cycle, audit = _stable_cycle(parameters, manifest, solver)
        audit["case_id"] = case["id"]
        cycle_audits.append(audit)
        if cycle is not None:
            cycles[case["id"]] = cycle
    if not all(row["passed"] for row in cycle_audits):
        raise SystemExit("stable-cycle qualification failed")
    seed_lookup = {
        (row["case_id"], row["family_id"]): row
        for row in seed_receipt["instances"]
        if row["passed"]
    }
    transported_seeds = []
    tasks = []
    for case in manifest["cases"]:
        parameters = RosslerParameters(**case["parameters"])
        for candidate in manifest["candidates"]:
            seed = seed_lookup[(case["id"], candidate["family_id"])]
            offsets = _phase_offsets(
                int(seed["fundamental_lag"]), manifest["phase_fractions"]
            )
            for phase_index, phase_offset in enumerate(offsets):
                transported = _transport_direction(
                    seed,
                    int(candidate["sign"]),
                    phase_offset,
                    parameters,
                    manifest,
                    transport_solver,
                )
                transported.update(
                    {
                        "case_id": case["id"],
                        "family_id": candidate["family_id"],
                        "sign": int(candidate["sign"]),
                        "phase_index": phase_index,
                    }
                )
                transported_seeds.append(transported)
                for amplitude_index, epsilon in enumerate(
                    manifest["seed_grid"]["amplitudes"]
                ):
                    tasks.append(
                        {
                            "case_id": case["id"],
                            "family_id": candidate["family_id"],
                            "sign": int(candidate["sign"]),
                            "phase_index": phase_index,
                            "phase_return_offset": phase_offset,
                            "amplitude_index": amplitude_index,
                            "amplitude": float(epsilon),
                            "parameters": case["parameters"],
                            "base_state": transported["base_section_state"],
                            "direction": transported["section_direction"],
                            "stable_cycle": cycles[case["id"]].tolist(),
                            "coordinate_scales": manifest["coordinate_scales"],
                            "solver": manifest["reference_solver"],
                            "return_horizon": max(manifest["administrative_horizons"]),
                            "maximum_flight_time": manifest["maximum_flight_time"],
                            "capture_radius": manifest["capture"]["scaled_radius"],
                            "required_capture_crossings": manifest["capture"][
                                "required_consecutive_crossings"
                            ],
                        }
                    )
    if not all(row["passed"] for row in transported_seeds):
        raise SystemExit("one or more transported phase directions failed")
    started = time.perf_counter()
    traces = []
    with ProcessPoolExecutor(max_workers=int(manifest["workers"])) as executor:
        futures = [executor.submit(_trace_task, task) for task in tasks]
        for index, future in enumerate(as_completed(futures), start=1):
            traces.append(future.result())
            if index % 24 == 0 or index == len(futures):
                print(
                    json.dumps(
                        {
                            "completed_traces": index,
                            "total_traces": len(futures),
                            "failures": sum(
                                not row["integration_success"] for row in traces
                            ),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    traces.sort(
        key=lambda row: (
            row["family_id"],
            row["sign"],
            row["phase_index"],
            row["case_id"],
            row["amplitude_index"],
        )
    )
    phase_case_rows = _summaries(traces, manifest)
    candidate_rows = _candidate_summaries(phase_case_rows, manifest)
    receipt = {
        "schema": "butterfly.upo-lobe-capture-refinement-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_seed_receipt_sha256": sha256_bytes(seed_bytes),
        "source_atlas_receipt_sha256": sha256_bytes(atlas_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "stable_cycles": cycle_audits,
        "transported_seeds": transported_seeds,
        "traces": traces,
        "phase_case_summaries": phase_case_rows,
        "candidate_summaries": candidate_rows,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(
            traces
            and all(row["integration_success"] for row in traces)
            and all(row["passed"] for row in candidate_rows)
        ),
        "scientific_scope": (
            "phase-resolved capture refinement, not a manifold connection proof"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {
                "experiment_id": receipt["experiment_id"],
                "manifest_sha256": receipt["manifest_sha256"],
                "trace_count": len(traces),
                "candidate_summaries": candidate_rows,
                "elapsed_seconds": receipt["elapsed_seconds"],
                "passed": receipt["passed"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
