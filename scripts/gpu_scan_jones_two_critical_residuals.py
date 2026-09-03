#!/usr/bin/env python3
"""GPU-batch Jones-section survivor maps and rank two-critical orbit residuals."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    PoincareSection,
    RosslerParameters,
    barrio_rossler_section,
    infer_return_map_branches_robust,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.qualify_jones_landmark_word import _spline_residuals

try:  # pragma: no cover - CUDA worker only
    import torch
    import triton
    import triton.language as tl
except ImportError:  # pragma: no cover - pure helpers remain testable on CPU
    torch = None
    triton = None
    tl = None


SCHEMA = "butterfly.jones-two-critical-gpu-scan-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def critical_orbit_assignment(orbit_values, critical_intervals, domain) -> dict:
    """Assign two ordered criticals to distinct orbit phases without symbols."""

    values = np.asarray(orbit_values, dtype=float)
    intervals = np.asarray(critical_intervals, dtype=float)
    lower, upper = map(float, domain)
    width = upper - lower
    if values.ndim != 1 or intervals.shape != (2, 2) or width <= 0.0:
        return {"resolved": False, "reason": "invalid orbit, interval, or domain"}
    rows = []
    for first in range(len(values)):
        for second in range(len(values)):
            if first == second:
                continue
            indices = (first, second)
            midpoint_distances = []
            signed_midpoint_residuals = []
            interval_distances = []
            for critical_index, orbit_index in enumerate(indices):
                lo, hi = intervals[critical_index]
                value = values[orbit_index]
                signed_midpoint = (value - 0.5 * (lo + hi)) / width
                signed_midpoint_residuals.append(signed_midpoint)
                midpoint_distances.append(abs(signed_midpoint))
                interval_distances.append(max(lo - value, 0.0, value - hi) / width)
            rows.append(
                (
                    max(midpoint_distances),
                    sum(midpoint_distances),
                    max(interval_distances),
                    indices,
                    midpoint_distances,
                    signed_midpoint_residuals,
                    interval_distances,
                )
            )
    best = min(rows, key=lambda row: (row[0], row[1], row[2], row[3]))
    return {
        "resolved": True,
        "orbit_indices": list(best[3]),
        "orbit_values": [float(values[index]) for index in best[3]],
        "normalized_midpoint_distances": [float(value) for value in best[4]],
        "normalized_signed_midpoint_residuals": [
            float(value) for value in best[5]
        ],
        "normalized_interval_distances": [float(value) for value in best[6]],
        "maximum_normalized_midpoint_distance": float(best[0]),
        "sum_normalized_midpoint_distance": float(best[1]),
        "maximum_normalized_interval_distance": float(best[2]),
    }


def rank_candidate_rows(rows) -> list[dict]:
    eligible = [row for row in rows if row.get("eligible")]
    return sorted(
        eligible,
        key=lambda row: (
            row["ranking"]["maximum_normalized_midpoint_distance"],
            row["ranking"]["sum_normalized_midpoint_distance"],
            row["ranking"]["maximum_zero_slope_residual"],
            row["id"],
        ),
    )


def signed_residual_bracket_cells(rows: list[dict], profile_count: int) -> list[dict]:
    """Find complete grid cells bracketing both signed residuals at every step."""

    if profile_count < 1:
        raise ValueError("profile_count must be positive")
    lookup = {
        tuple(row["grid_index"]): row
        for row in rows
        if row.get("eligible")
        and row.get("grid_index") is not None
        and row.get("signed_midpoint_residuals_by_profile") is not None
        and row.get("assignment_indices_by_profile") is not None
    }
    cells = []
    for i, j in sorted(lookup):
        indices = ((i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1))
        if any(index not in lookup for index in indices):
            continue
        corners = [lookup[index] for index in indices]
        profiles = []
        passed = True
        for profile_index in range(profile_count):
            assignments = [
                tuple(row["assignment_indices_by_profile"][profile_index])
                for row in corners
            ]
            if len(set(assignments)) != 1:
                passed = False
                break
            residual_ranges = []
            for residual_index in range(2):
                values = [
                    float(
                        row["signed_midpoint_residuals_by_profile"][profile_index][
                            residual_index
                        ]
                    )
                    for row in corners
                ]
                residual_range = [min(values), max(values)]
                residual_ranges.append(residual_range)
                if residual_range[0] > 0.0 or residual_range[1] < 0.0:
                    passed = False
            profiles.append(
                {
                    "profile_index": profile_index,
                    "assignment_indices": list(assignments[0]),
                    "signed_residual_ranges": residual_ranges,
                }
            )
        if passed:
            a_values = [float(row["parameters"]["a"]) for row in corners]
            c_values = [float(row["parameters"]["c"]) for row in corners]
            cells.append(
                {
                    "lower_grid_index": [i, j],
                    "corner_ids": [row["id"] for row in corners],
                    "a_bounds": [min(a_values), max(a_values)],
                    "c_bounds": [min(c_values), max(c_values)],
                    "profiles": profiles,
                }
            )
    return cells


def return_coordinate_axis(manifest: dict) -> tuple[str, int]:
    """Return an explicitly validated scalar return-map coordinate."""

    coordinate = manifest.get("return_coordinate", {"name": "x", "axis": 0})
    name = str(coordinate["name"])
    axis = int(coordinate["axis"])
    if (name, axis) not in (("x", 0), ("z", 2)):
        raise ValueError("return coordinate must be x/0 or z/2")
    return name, axis


def section_kind(manifest: dict) -> tuple[str, int]:
    """Return the declared section name and its GPU compile-time code."""

    name = str(manifest.get("section", {}).get("kind", "legacy_negative"))
    codes = {"legacy_negative": 0, "barrio_positive_x": 1}
    if name not in codes:
        raise ValueError("section kind must be legacy_negative or barrio_positive_x")
    return name, codes[name]


def cycle_state_count(manifest: dict) -> int:
    """Return the fixed number of target-section phases per candidate."""

    count = int(manifest.get("cycle_state_count", 6))
    if not 2 <= count <= 64:
        raise ValueError("cycle state count must be between 2 and 64")
    return count


if triton is not None:  # pragma: no cover - compiled only on CUDA workers

    @triton.jit
    def _hermite_root_step(alpha, left, right, left_d, right_d, offset, dt: tl.constexpr):
        alpha2 = alpha * alpha
        alpha3 = alpha2 * alpha
        h00 = 2.0 * alpha3 - 3.0 * alpha2 + 1.0
        h10 = alpha3 - 2.0 * alpha2 + alpha
        h01 = -2.0 * alpha3 + 3.0 * alpha2
        h11 = alpha3 - alpha2
        value = h00 * left + h10 * dt * left_d + h01 * right + h11 * dt * right_d - offset
        derivative = (
            (6.0 * alpha2 - 6.0 * alpha) * left
            + (3.0 * alpha2 - 4.0 * alpha + 1.0) * dt * left_d
            + (-6.0 * alpha2 + 6.0 * alpha) * right
            + (3.0 * alpha2 - 2.0 * alpha) * dt * right_d
        )
        refined = tl.where(tl.abs(derivative) > 1.0e-15, alpha - value / derivative, alpha)
        return tl.maximum(0.0, tl.minimum(1.0, refined))


    @triton.jit
    def _rk4_jones_chunk(
        states,
        active_values,
        failed_values,
        capture_streaks,
        case_ids,
        parameters,
        section_offsets,
        gate_uppers,
        cycle_states,
        recorded_states,
        recorded_times,
        recorded_counts,
        batch_size,
        step_offset,
        step_count,
        dt: tl.constexpr,
        record_crossings: tl.constexpr,
        max_recorded_crossings: tl.constexpr,
        cycle_state_count: tl.constexpr,
        capture_scale_first: tl.constexpr,
        capture_scale_z: tl.constexpr,
        capture_radius_squared: tl.constexpr,
        required_capture_crossings: tl.constexpr,
        escape_radius_squared: tl.constexpr,
        section_kind_code: tl.constexpr,
        block_size: tl.constexpr,
    ):
        offsets = tl.program_id(0) * block_size + tl.arange(0, block_size)
        lane = offsets < batch_size
        base = offsets * 3
        x = tl.load(states + base, mask=lane, other=0.0)
        y = tl.load(states + base + 1, mask=lane, other=0.0)
        z = tl.load(states + base + 2, mask=lane, other=0.0)
        active = tl.load(active_values + offsets, mask=lane, other=0) != 0
        failed = tl.load(failed_values + offsets, mask=lane, other=0) != 0
        streak = tl.load(capture_streaks + offsets, mask=lane, other=0).to(tl.int32)
        record_count = tl.load(recorded_counts + offsets, mask=lane, other=0).to(tl.int32)
        case = tl.load(case_ids + offsets, mask=lane, other=0).to(tl.int32)
        a = tl.load(parameters + case * 3)
        b = tl.load(parameters + case * 3 + 1)
        c = tl.load(parameters + case * 3 + 2)
        section_offset = tl.load(section_offsets + case)
        gate_x = tl.load(gate_uppers + case)

        for step in tl.range(0, step_count):
            px, py, pz = x, y, z
            was_active = active
            k1x = -y - z
            k1y = x + a * y
            k1z = b + z * (x - c)
            x2 = x + 0.5 * dt * k1x
            y2 = y + 0.5 * dt * k1y
            z2 = z + 0.5 * dt * k1z
            k2x = -y2 - z2
            k2y = x2 + a * y2
            k2z = b + z2 * (x2 - c)
            x3 = x + 0.5 * dt * k2x
            y3 = y + 0.5 * dt * k2y
            z3 = z + 0.5 * dt * k2z
            k3x = -y3 - z3
            k3y = x3 + a * y3
            k3z = b + z3 * (x3 - c)
            x4 = x + dt * k3x
            y4 = y + dt * k3y
            z4 = z + dt * k3z
            k4x = -y4 - z4
            k4y = x4 + a * y4
            k4z = b + z4 * (x4 - c)
            nx = x + (dt / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
            ny = y + (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
            nz = z + (dt / 6.0) * (k1z + 2.0 * k2z + 2.0 * k3z + k4z)
            x = tl.where(was_active, nx, x)
            y = tl.where(was_active, ny, y)
            z = tl.where(was_active, nz, z)

            finite = (x == x) & (y == y) & (z == z)
            bounded = x * x + y * y + z * z <= escape_radius_squared
            state_valid = finite & bounded
            failed = failed | (was_active & ~state_valid)
            if section_kind_code == 0:
                left_value = py - section_offset
                right_value = y - section_offset
                crossed_plane = (
                    was_active
                    & state_valid
                    & (left_value > 0.0)
                    & (right_value <= 0.0)
                )
                root_left = py
                root_right = y
                root_left_d = k1y
                root_right_d = x + a * y
            else:
                left_value = px - section_offset
                right_value = x - section_offset
                crossed_plane = (
                    was_active
                    & state_valid
                    & (left_value < 0.0)
                    & (right_value >= 0.0)
                )
                root_left = px
                root_right = x
                root_left_d = k1x
                root_right_d = -y - z
            alpha = tl.where(crossed_plane, -left_value / (right_value - left_value), 0.0)
            end_dx = -y - z
            end_dy = x + a * y
            end_dz = b + z * (x - c)
            for _ in tl.static_range(0, 4):
                alpha = _hermite_root_step(
                    alpha,
                    root_left,
                    root_right,
                    root_left_d,
                    root_right_d,
                    section_offset,
                    dt,
                )
            alpha2 = alpha * alpha
            alpha3 = alpha2 * alpha
            h00 = 2.0 * alpha3 - 3.0 * alpha2 + 1.0
            h10 = alpha3 - 2.0 * alpha2 + alpha
            h01 = -2.0 * alpha3 + 3.0 * alpha2
            h11 = alpha3 - alpha2
            cross_x = h00 * px + h10 * dt * k1x + h01 * x + h11 * dt * end_dx
            cross_y = h00 * py + h10 * dt * k1y + h01 * y + h11 * dt * end_dy
            cross_z = h00 * pz + h10 * dt * k1z + h01 * z + h11 * dt * end_dz
            if section_kind_code == 0:
                crossed = crossed_plane & (cross_x < gate_x)
            else:
                crossed = crossed_plane

            if record_crossings:
                recorded = crossed & (record_count < max_recorded_crossings)
                slot = offsets * max_recorded_crossings * 3 + record_count * 3
                tl.store(recorded_states + slot, cross_x, mask=recorded)
                tl.store(recorded_states + slot + 1, cross_y, mask=recorded)
                tl.store(recorded_states + slot + 2, cross_z, mask=recorded)
                time_slot = offsets * max_recorded_crossings + record_count
                tl.store(recorded_times + time_slot, (step_offset + step + alpha) * dt, mask=recorded)
                record_count += recorded.to(tl.int32)

            minimum_distance = tl.full((block_size,), float("inf"), tl.float64)
            for orbit_index in tl.static_range(0, cycle_state_count):
                cycle_base = case * cycle_state_count * 3 + orbit_index * 3
                cycle_x = tl.load(cycle_states + cycle_base)
                cycle_y = tl.load(cycle_states + cycle_base + 1)
                cycle_z = tl.load(cycle_states + cycle_base + 2)
                if section_kind_code == 0:
                    first_difference = (cross_x - cycle_x) / capture_scale_first
                else:
                    first_difference = (cross_y - cycle_y) / capture_scale_first
                dz = (cross_z - cycle_z) / capture_scale_z
                minimum_distance = tl.minimum(
                    minimum_distance,
                    first_difference * first_difference + dz * dz,
                )
            close = minimum_distance <= capture_radius_squared
            streak = tl.where(crossed, tl.where(close, streak + 1, 0), streak)
            captured = crossed & (streak >= required_capture_crossings)
            active = was_active & state_valid & ~captured

        tl.store(states + base, x, mask=lane)
        tl.store(states + base + 1, y, mask=lane)
        tl.store(states + base + 2, z, mask=lane)
        tl.store(active_values + offsets, active.to(tl.int32), mask=lane)
        tl.store(failed_values + offsets, failed.to(tl.int32), mask=lane)
        tl.store(capture_streaks + offsets, streak, mask=lane)
        tl.store(recorded_counts + offsets, record_count, mask=lane)


def _sections(candidates, kind: str):
    sections = []
    for candidate in candidates:
        parameters = RosslerParameters(**candidate["parameters"])
        if kind == "legacy_negative":
            base = legacy_rossler_section(parameters)
            sections.append(
                PoincareSection(
                    normal=base.normal,
                    offset=base.offset,
                    direction=-1,
                    gate_axis=base.gate_axis,
                    gate_upper=base.gate_upper,
                    name="legacy-small-equilibrium-half-plane:negative",
                )
            )
        else:
            sections.append(barrio_rossler_section(parameters))
    return sections


def _initial_ensemble(candidates, ensemble):
    x_values = np.linspace(*ensemble["x_range"], int(ensemble["x_count"]))
    z_values = np.linspace(*ensemble["z_range"], int(ensemble["z_count"]))
    x_grid, z_grid = np.meshgrid(x_values, z_values, indexing="ij")
    per_case = []
    for candidate in candidates:
        parameters = RosslerParameters(**candidate["parameters"])
        historical = legacy_rossler_section(parameters)
        per_case.append(
            np.column_stack(
                (
                    x_grid.ravel(),
                    np.full(x_grid.size, historical.offset),
                    z_grid.ravel(),
                )
            )
        )
    return np.asarray(per_case, dtype=float)


def integrate_gpu(
    candidates,
    *,
    dt,
    horizon,
    checkpoints,
    midpoint,
    ensemble,
    capture,
    gpu_options,
    section_name,
    section_code,
    target_cycle_state_count,
):
    if torch is None or triton is None or not torch.cuda.is_available():
        raise RuntimeError("CUDA, PyTorch, and Triton are required")
    case_count = len(candidates)
    sections = _sections(candidates, section_name)
    initial = _initial_ensemble(candidates, ensemble)
    seed_count = initial.shape[1]
    flat_initial = initial.reshape(-1, 3)
    total = len(flat_initial)
    device = torch.device("cuda")
    state = torch.as_tensor(flat_initial, dtype=torch.float64, device=device).contiguous()
    case_ids = torch.arange(case_count, device=device, dtype=torch.int32).repeat_interleave(seed_count)
    parameters = torch.as_tensor(
        [[row["parameters"][name] for name in ("a", "b", "c")] for row in candidates],
        dtype=torch.float64,
        device=device,
    ).contiguous()
    section_offsets = torch.as_tensor([row.offset for row in sections], dtype=torch.float64, device=device)
    gate_uppers = torch.as_tensor(
        [float("inf") if row.gate_upper is None else row.gate_upper for row in sections],
        dtype=torch.float64,
        device=device,
    )
    cycles = torch.as_tensor([row["section_states"] for row in candidates], dtype=torch.float64, device=device).contiguous()
    active = torch.ones(total, dtype=torch.int32, device=device)
    failed = torch.zeros(total, dtype=torch.int32, device=device)
    streaks = torch.zeros(total, dtype=torch.int32, device=device)
    max_crossings = int(gpu_options["max_recorded_crossings"])
    states = torch.full((total, max_crossings, 3), float("nan"), dtype=torch.float64, device=device)
    times = torch.full((total, max_crossings), float("nan"), dtype=torch.float64, device=device)
    counts = torch.zeros(total, dtype=torch.int32, device=device)
    total_steps = round(float(horizon) / float(dt))
    checkpoint_steps = [round(float(value) / float(dt)) for value in checkpoints]
    midpoint_steps = [round(float(value) / float(dt)) for value in midpoint]
    if not math.isclose(total_steps * dt, horizon, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("horizon must be step aligned")
    boundaries = sorted(set((0, total_steps, *checkpoint_steps, *midpoint_steps)))
    checkpoint_set = set(checkpoint_steps)
    survivor_counts = []
    completed = 0
    block_size = 128
    grid = (triton.cdiv(total, block_size),)
    torch.cuda.synchronize()
    started = time.perf_counter()
    for boundary in boundaries[1:]:
        while completed < boundary:
            steps = min(int(gpu_options["chunk_steps"]), boundary - completed)
            record = midpoint_steps[0] <= completed and completed + steps <= midpoint_steps[1]
            _rk4_jones_chunk[grid](
                state,
                active,
                failed,
                streaks,
                case_ids,
                parameters,
                section_offsets,
                gate_uppers,
                cycles,
                states,
                times,
                counts,
                total,
                completed,
                steps,
                dt=float(dt),
                record_crossings=record,
                max_recorded_crossings=max_crossings,
                cycle_state_count=target_cycle_state_count,
                capture_scale_first=float(capture["coordinate_scales"][0]),
                capture_scale_z=float(capture["coordinate_scales"][1]),
                capture_radius_squared=float(capture["radius"]) ** 2,
                required_capture_crossings=int(capture["required_crossings"]),
                escape_radius_squared=float(ensemble["escape_radius"]) ** 2,
                section_kind_code=section_code,
                block_size=block_size,
                num_warps=4,
            )
            completed += steps
        if boundary in checkpoint_set:
            survivor_counts.append(active.reshape(case_count, seed_count).sum(dim=1).cpu().numpy())
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    active_mask = active != 0
    survivor_global_ids = torch.nonzero(active_mask, as_tuple=False).flatten()
    host_case_ids = case_ids[survivor_global_ids].cpu().numpy()
    host_seed_ids = (survivor_global_ids % seed_count).cpu().numpy()
    host_counts = counts[survivor_global_ids].cpu().numpy()
    host_states = states[survivor_global_ids].cpu().numpy()
    host_times = times[survivor_global_ids].cpu().numpy()
    failed_counts = failed.reshape(case_count, seed_count).sum(dim=1).cpu().numpy()
    records = []
    for case_index in range(case_count):
        selected = np.flatnonzero(host_case_ids == case_index)
        records.append(
            {
                "seed_ids": host_seed_ids[selected],
                "states": [host_states[index, : int(host_counts[index])] for index in selected],
                "times": [host_times[index, : int(host_counts[index])] for index in selected],
            }
        )
    return {
        "initial": initial,
        "sections": sections,
        "survivor_counts": np.asarray(survivor_counts, dtype=int).T,
        "failed_counts": failed_counts,
        "records": records,
        "elapsed_seconds": elapsed,
        "state_steps_per_second": total * total_steps / elapsed,
    }


def _pairs(record, axis=0):
    source, target = [], []
    for states in record["states"]:
        values = np.asarray(states, dtype=float)[:, axis]
        if len(values) >= 2:
            source.append(values[:-1])
            target.append(values[1:])
    if not source:
        return np.empty(0), np.empty(0)
    return np.concatenate(source), np.concatenate(target)


def _profile_rows(candidates, run, manifest, profile):
    acceptance = manifest["acceptance"]
    variants = tuple(
        {**manifest["oracle_common"], **variant["options"]}
        for variant in manifest["oracle_variants"]
    )
    _, coordinate_axis = return_coordinate_axis(manifest)
    rows = []
    for index, candidate in enumerate(candidates):
        source, target = _pairs(run["records"][index], axis=coordinate_axis)
        if len(source) >= int(acceptance["minimum_return_pairs"]):
            robust = infer_return_map_branches_robust(
                source,
                target,
                variants=variants,
                minimum_variant_consensus=1.0,
                maximum_normalized_critical_point_span=float(acceptance["maximum_normalized_critical_span"]),
            )
            robust_row = asdict(robust)
        else:
            robust_row = {"resolved": False, "branch_count": None, "reason": "insufficient return pairs"}
        assignment = {"resolved": False, "reason": "requires a resolved three-branch map"}
        slope_residuals = None
        assigned_slope = None
        if robust_row.get("resolved") and robust_row.get("branch_count") == 3:
            domain = (float(np.min(source)), float(np.max(source)))
            orbit_values = np.asarray(candidate["section_states"], dtype=float)[
                :, coordinate_axis
            ]
            assignment = critical_orbit_assignment(
                orbit_values, robust_row["critical_point_intervals"], domain
            )
            slope_residuals = _spline_residuals(source, target, orbit_values, variants)
            assigned_slope = max(slope_residuals[index] for index in assignment["orbit_indices"])
        eligible = bool(
            run["failed_counts"][index] == 0
            and run["survivor_counts"][index, -1] >= int(acceptance["minimum_final_survivors"])
            and len(source) >= int(acceptance["minimum_return_pairs"])
            and robust_row.get("resolved")
            and robust_row.get("branch_count") == 3
            and assignment.get("resolved")
        )
        rows.append(
            {
                "id": candidate["id"],
                "profile": profile["name"],
                "dt": profile["dt"],
                "survivor_counts": run["survivor_counts"][index].tolist(),
                "failed_count": int(run["failed_counts"][index]),
                "pair_count": len(source),
                "source_domain": [float(np.min(source)), float(np.max(source))] if len(source) else None,
                "robust_partition": robust_row,
                "assignment": assignment,
                "zero_slope_residuals": list(slope_residuals) if slope_residuals is not None else None,
                "assigned_maximum_zero_slope_residual": float(assigned_slope) if assigned_slope is not None else None,
                "eligible": eligible,
            }
        )
    return rows


def _combine_candidates(candidates, profile_rows, manifest):
    acceptance = manifest["acceptance"]
    initial_count = int(manifest["ensemble"]["x_count"]) * int(manifest["ensemble"]["z_count"])
    rows = []
    for candidate in candidates:
        matching = [row for rows_for_profile in profile_rows for row in rows_for_profile if row["id"] == candidate["id"]]
        eligible = len(matching) == 2 and all(row["eligible"] for row in matching)
        if eligible:
            critical_midpoints = []
            for row in matching:
                domain = row["source_domain"]
                width = domain[1] - domain[0]
                critical_midpoints.append(
                    [(0.5 * (lo + hi) - domain[0]) / width for lo, hi in row["robust_partition"]["critical_point_intervals"]]
                )
            critical_step_difference = float(np.max(np.abs(np.asarray(critical_midpoints[0]) - critical_midpoints[1])))
            survivor_difference = float(
                np.max(
                    np.abs(
                        np.asarray(matching[0]["survivor_counts"], dtype=float)
                        - np.asarray(matching[1]["survivor_counts"], dtype=float)
                    )
                    / initial_count
                )
            )
            assignment_agreement = matching[0]["assignment"]["orbit_indices"] == matching[1]["assignment"]["orbit_indices"]
            ranking = {
                "maximum_normalized_midpoint_distance": max(row["assignment"]["maximum_normalized_midpoint_distance"] for row in matching),
                "sum_normalized_midpoint_distance": sum(row["assignment"]["sum_normalized_midpoint_distance"] for row in matching),
                "maximum_normalized_interval_distance": max(row["assignment"]["maximum_normalized_interval_distance"] for row in matching),
                "maximum_zero_slope_residual": max(row["assigned_maximum_zero_slope_residual"] for row in matching),
            }
            signed_midpoint_residuals_by_profile = [
                row["assignment"]["normalized_signed_midpoint_residuals"]
                for row in matching
            ]
            assignment_indices_by_profile = [
                row["assignment"]["orbit_indices"] for row in matching
            ]
            parity_passed = bool(
                critical_step_difference <= float(acceptance["maximum_step_critical_midpoint_difference"])
                and survivor_difference <= float(acceptance["maximum_survivor_fraction_difference"])
                and assignment_agreement
            )
            eligible = parity_passed
        else:
            critical_step_difference = None
            survivor_difference = None
            assignment_agreement = False
            ranking = None
            signed_midpoint_residuals_by_profile = None
            assignment_indices_by_profile = None
            parity_passed = False
        rows.append(
            {
                "id": candidate["id"],
                "grid_index": candidate.get("grid_index"),
                "parameters": candidate["parameters"],
                "critical_step_difference": critical_step_difference,
                "survivor_fraction_difference": survivor_difference,
                "assignment_agreement": assignment_agreement,
                "ranking": ranking,
                "signed_midpoint_residuals_by_profile": signed_midpoint_residuals_by_profile,
                "assignment_indices_by_profile": assignment_indices_by_profile,
                "parity_passed": parity_passed,
                "eligible": eligible,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    candidate_bytes = args.candidates.read_bytes()
    manifest = json.loads(manifest_bytes)
    candidate_document = json.loads(candidate_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported two-critical GPU scan manifest")
    for evidence in manifest["evidence"]:
        if sha256_file(Path(evidence["path"])) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    if sha256_bytes(candidate_bytes) != manifest["candidate_input_sha256"]:
        raise SystemExit("candidate input hash mismatch")
    if len(args.source_commit) != 40 or any(value not in "0123456789abcdef" for value in args.source_commit.lower()):
        raise SystemExit("a full source commit is required")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("source commit mismatch")
    if torch is None or triton is None or not torch.cuda.is_available():
        raise SystemExit("CUDA, PyTorch, and Triton are required")
    candidates = [row for row in candidate_document["candidates"] if row["passed"]]
    if len(candidates) != int(manifest["expected_candidate_count"]):
        raise SystemExit("unexpected passed candidate count")
    coordinate_name, coordinate_axis = return_coordinate_axis(manifest)
    section_name, section_code = section_kind(manifest)
    target_cycle_state_count = cycle_state_count(manifest)
    if any(
        np.asarray(row["section_states"]).shape != (target_cycle_state_count, 3)
        for row in candidates
    ):
        raise SystemExit("candidate section-state count or shape mismatch")

    profile_results = []
    profile_rows = []
    for profile in manifest["profiles"]:
        run = integrate_gpu(
            candidates,
            dt=float(profile["dt"]),
            horizon=float(manifest["ensemble"]["horizon"]),
            checkpoints=manifest["ensemble"]["checkpoint_times"],
            midpoint=manifest["ensemble"]["midpoint_window"],
            ensemble=manifest["ensemble"],
            capture=manifest["capture"],
            gpu_options=manifest["gpu"],
            section_name=section_name,
            section_code=section_code,
            target_cycle_state_count=target_cycle_state_count,
        )
        rows = _profile_rows(candidates, run, manifest, profile)
        profile_rows.append(rows)
        profile_results.append(
            {
                "name": profile["name"],
                "dt": profile["dt"],
                "elapsed_seconds": run["elapsed_seconds"],
                "state_steps_per_second": run["state_steps_per_second"],
                "eligible_candidate_count": sum(row["eligible"] for row in rows),
                "rows": rows,
            }
        )
        print(json.dumps({"profile": profile["name"], "eligible": profile_results[-1]["eligible_candidate_count"]}, sort_keys=True), flush=True)

    combined = _combine_candidates(candidates, profile_rows, manifest)
    ranked = rank_candidate_rows(combined)
    selected = ranked[0] if ranked else None
    bracket_cells = signed_residual_bracket_cells(combined, len(profile_rows))
    acceptance = manifest["acceptance"]
    eligible_count_passed = len(ranked) >= int(
        acceptance["minimum_eligible_candidates"]
    )
    direct_candidate_passed = bool(
        eligible_count_passed
        and selected is not None
        and selected["ranking"]["maximum_normalized_midpoint_distance"]
        <= float(acceptance["maximum_selected_midpoint_distance"])
        and selected["ranking"]["maximum_normalized_interval_distance"]
        <= float(acceptance["maximum_selected_interval_distance"])
        and selected["ranking"]["maximum_zero_slope_residual"]
        <= float(acceptance["maximum_selected_zero_slope_residual"])
    )
    minimum_bracket_cells = int(acceptance.get("minimum_signed_bracket_cells", 0))
    bracket_passed = bool(
        minimum_bracket_cells > 0
        and eligible_count_passed
        and len(bracket_cells) >= minimum_bracket_cells
    )
    passed = direct_candidate_passed or bracket_passed
    props = torch.cuda.get_device_properties(0)
    output = {
        "schema": "butterfly.jones-two-critical-gpu-scan.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "candidate_input_sha256": sha256_bytes(candidate_bytes),
        "return_coordinate": {"name": coordinate_name, "axis": coordinate_axis},
        "section": {"kind": section_name, "gpu_code": section_code},
        "cycle_state_count": target_cycle_state_count,
        "source": {
            "declared_commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "environment": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "triton": triton.__version__,
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_bytes": props.total_memory,
            "gpu_compute_capability": [props.major, props.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "profiles": profile_results,
        "combined_candidates": combined,
        "ranked_candidate_ids": [row["id"] for row in ranked],
        "selected_candidate": selected,
        "direct_candidate_passed": direct_candidate_passed,
        "signed_residual_bracket_cells": bracket_cells,
        "signed_residual_bracket_passed": bracket_passed,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps({"output": str(args.output), "passed": passed, "eligible": len(ranked), "selected": selected}, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
