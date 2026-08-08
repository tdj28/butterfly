#!/usr/bin/env python3
"""Qualify a Triton Float64 sprinkler sampler against EXP-112."""
from __future__ import annotations

import argparse
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
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    collect_crossings,
    infer_return_map_branches_robust,
    scrambled_sobol_section_states,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

try:
    import torch
    import triton
    import triton.language as tl
except ImportError as error:  # pragma: no cover - GPU worker only
    raise SystemExit("PyTorch and Triton are required") from error


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
def _rk4_sprinkler_chunk(
    states,
    active_values,
    failed_values,
    capture_streaks,
    parameters,
    section_offset,
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
    capture_scale_y: tl.constexpr,
    capture_scale_z: tl.constexpr,
    capture_radius_squared: tl.constexpr,
    required_capture_crossings: tl.constexpr,
    escape_radius_squared: tl.constexpr,
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
    a = tl.load(parameters)
    b = tl.load(parameters + 1)
    c = tl.load(parameters + 2)
    section_x = tl.load(section_offset)
    cy0 = tl.load(cycle_states + 1)
    cz0 = tl.load(cycle_states + 2)
    cy1 = tl.load(cycle_states + 4)
    cz1 = tl.load(cycle_states + 5)
    cy2 = tl.load(cycle_states + 7)
    cz2 = tl.load(cycle_states + 8)
    cy3 = tl.load(cycle_states + 10)
    cz3 = tl.load(cycle_states + 11)

    for step in tl.range(0, step_count):
        px = x
        py = y
        pz = z
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
        left_value = px - section_x
        right_value = x - section_x
        crossed = was_active & state_valid & (left_value < 0.0) & (right_value >= 0.0)
        alpha = tl.where(crossed, -left_value / (right_value - left_value), 0.0)
        end_dx = -y - z
        end_dy = x + a * y
        end_dz = b + z * (x - c)
        alpha = _hermite_root_step(alpha, px, x, k1x, end_dx, section_x, dt)
        alpha = _hermite_root_step(alpha, px, x, k1x, end_dx, section_x, dt)
        alpha = _hermite_root_step(alpha, px, x, k1x, end_dx, section_x, dt)
        alpha = _hermite_root_step(alpha, px, x, k1x, end_dx, section_x, dt)
        alpha2 = alpha * alpha
        alpha3 = alpha * alpha * alpha
        h00 = 2.0 * alpha3 - 3.0 * alpha2 + 1.0
        h10 = alpha3 - 2.0 * alpha2 + alpha
        h01 = -2.0 * alpha3 + 3.0 * alpha2
        h11 = alpha3 - alpha2
        cross_y = h00 * py + h10 * dt * k1y + h01 * y + h11 * dt * end_dy
        cross_z = h00 * pz + h10 * dt * k1z + h01 * z + h11 * dt * end_dz

        if record_crossings:
            recorded = crossed & (record_count < max_recorded_crossings)
            slot = offsets * max_recorded_crossings * 3 + record_count * 3
            tl.store(recorded_states + slot, section_x, mask=recorded)
            tl.store(recorded_states + slot + 1, cross_y, mask=recorded)
            tl.store(recorded_states + slot + 2, cross_z, mask=recorded)
            time_slot = offsets * max_recorded_crossings + record_count
            tl.store(recorded_times + time_slot, (step_offset + step + alpha) * dt, mask=recorded)
            record_count += recorded.to(tl.int32)

        dy0 = (cross_y - cy0) / capture_scale_y
        dz0 = (cross_z - cz0) / capture_scale_z
        dy1 = (cross_y - cy1) / capture_scale_y
        dz1 = (cross_z - cz1) / capture_scale_z
        dy2 = (cross_y - cy2) / capture_scale_y
        dz2 = (cross_z - cz2) / capture_scale_z
        dy3 = (cross_y - cy3) / capture_scale_y
        dz3 = (cross_z - cz3) / capture_scale_z
        d0 = dy0 * dy0 + dz0 * dz0
        d1 = dy1 * dy1 + dz1 * dz1
        d2 = dy2 * dy2 + dz2 * dz2
        d3 = dy3 * dy3 + dz3 * dz3
        close = tl.minimum(tl.minimum(d0, d1), tl.minimum(d2, d3)) <= capture_radius_squared
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


def integrate_gpu(parameters, initial, section, cycle, *, dt, horizon, checkpoints, midpoint, capture, escape_radius, chunk_steps, max_crossings):
    total_steps = round(horizon / dt)
    checkpoint_steps = [round(value / dt) for value in checkpoints]
    midpoint_steps = [round(value / dt) for value in midpoint]
    if not math.isclose(total_steps * dt, horizon, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("horizon is not step aligned")
    if len(cycle) != 4:
        raise ValueError("the frozen GPU kernel requires a period-4 cycle")
    device = torch.device("cuda")
    state = torch.as_tensor(initial, dtype=torch.float64, device=device).contiguous()
    params = torch.as_tensor(
        (parameters.a, parameters.b, parameters.c),
        dtype=torch.float64,
        device=device,
    )
    section_value = torch.tensor((section.offset,), dtype=torch.float64, device=device)
    cycle_values = torch.as_tensor(cycle, dtype=torch.float64, device=device).contiguous()
    active = torch.ones(len(initial), dtype=torch.int32, device=device)
    failed = torch.zeros(len(initial), dtype=torch.int32, device=device)
    streaks = torch.zeros(len(initial), dtype=torch.int32, device=device)
    states = torch.full((len(initial), max_crossings, 3), float("nan"), dtype=torch.float64, device=device)
    times = torch.full((len(initial), max_crossings), float("nan"), dtype=torch.float64, device=device)
    counts = torch.zeros(len(initial), dtype=torch.int32, device=device)
    block_size = 128
    grid = (triton.cdiv(len(initial), block_size),)
    boundaries = sorted(set((0, total_steps, *checkpoint_steps, *midpoint_steps)))
    checkpoint_set = set(checkpoint_steps)
    survivor_counts = []
    completed = 0
    torch.cuda.synchronize()
    started = time.perf_counter()
    for boundary in boundaries[1:]:
        while completed < boundary:
            steps = min(chunk_steps, boundary - completed)
            record = midpoint_steps[0] <= completed and completed + steps <= midpoint_steps[1]
            _rk4_sprinkler_chunk[grid](
                state, active, failed, streaks, params, section_value, cycle_values,
                states, times, counts, len(initial), completed, steps,
                dt=dt, record_crossings=record, max_recorded_crossings=max_crossings,
                capture_scale_y=float(capture["coordinate_scales"][0]),
                capture_scale_z=float(capture["coordinate_scales"][1]),
                capture_radius_squared=float(capture["radius"]) ** 2,
                required_capture_crossings=int(capture["required_crossings"]),
                escape_radius_squared=float(escape_radius) ** 2,
                block_size=block_size, num_warps=4,
            )
            completed += steps
        if boundary in checkpoint_set:
            survivor_counts.append(int(torch.count_nonzero(active).item()))
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    host_active = active.cpu().numpy().astype(bool)
    host_failed = failed.cpu().numpy().astype(bool)
    host_counts = counts.cpu().numpy()
    host_states = states.cpu().numpy()
    host_times = times.cpu().numpy()
    return {
        "survivor_ids": np.flatnonzero(host_active),
        "failed": host_failed,
        "survivor_counts": np.asarray(survivor_counts),
        "states": [host_states[i, : int(host_counts[i])] for i in range(len(initial))],
        "times": [host_times[i, : int(host_counts[i])] for i in range(len(initial))],
        "elapsed_seconds": elapsed,
        "state_steps_per_second": len(initial) * total_steps / elapsed,
    }


def pairs(records, survivor_ids, axis):
    source, target = [], []
    for trajectory_id in survivor_ids:
        values = records[int(trajectory_id)][:, axis]
        if len(values) >= 2:
            source.append(values[:-1])
            target.append(values[1:])
    return (np.concatenate(source), np.concatenate(target)) if source else (np.empty(0), np.empty(0))


def prepare_case(case, cpu_manifest, solver):
    fixed = cpu_manifest["fixed_parameters"]
    parameters = RosslerParameters(a=float(case["a"]), b=float(fixed["b"]), c=float(fixed["c"]))
    section = barrio_rossler_section(parameters)
    crossings = collect_crossings(
        parameters, cpu_manifest["cycle_initial_state"], section,
        transient=float(cpu_manifest["cycle_reference"]["transient"]),
        observation_horizon=float(cpu_manifest["cycle_reference"]["observation_horizon"]),
        max_crossings=int(cpu_manifest["cycle_reference"]["max_crossings"]), config=solver,
    )
    classification = classify_fundamental_period(crossings.states, **cpu_manifest["cycle_reference"]["recurrence"])
    cycle = crossings.states[-int(case["stable_period"]):]
    run = next(row for row in cpu_manifest["runs"] if row["id"] == "sobol-112-baseline")
    ensemble = cpu_manifest["ensemble"]
    initial = scrambled_sobol_section_states(
        section, first_coordinate_range=tuple(ensemble["y_range"]),
        second_coordinate_range=tuple(ensemble["z_range"]),
        sample_power=int(run["sample_power"]), scramble_seed=int(run["scramble_seed"]),
    )
    return parameters, section, cycle, classification, initial


def gpu_coordinate_summary(gpu, cpu_manifest, manifest):
    output = {}
    for coordinate in cpu_manifest["coordinates"]:
        source, target = pairs(gpu["states"], gpu["survivor_ids"], int(coordinate["axis"]))
        if len(source) < manifest["acceptance"]["minimum_return_pairs"]:
            robust = {"resolved": False, "branch_count": None}
        else:
            robust = asdict(infer_return_map_branches_robust(
                source, target, variants=cpu_manifest["oracle_variants"],
                common_options=cpu_manifest["oracle_common"],
                minimum_variant_consensus=float(manifest["acceptance"]["minimum_oracle_variant_consensus"]),
                maximum_normalized_critical_point_span=float(manifest["acceptance"]["maximum_within_gpu_critical_span"]),
            ))
        output[coordinate["name"]] = {
            "pair_count": len(source),
            "source_minimum": float(np.min(source)) if len(source) else None,
            "source_maximum": float(np.max(source)) if len(source) else None,
            "robust_oracle": robust,
        }
    return output


def compare_critical(reference, gpu, expected):
    output = {}
    for name, fixed in reference.items():
        observed = gpu[name]
        oracle = observed["robust_oracle"]
        if not oracle["resolved"] or oracle["branch_count"] != expected:
            output[name] = {"resolved": False, "maximum_normalized_span": 1e300}
            continue
        domain = max(fixed["source_maximum"], observed["source_maximum"]) - min(fixed["source_minimum"], observed["source_minimum"])
        intervals, spans = [], []
        for index in range(expected - 1):
            lower = min(fixed["critical_point_intervals"][index][0], oracle["critical_point_intervals"][index][0])
            upper = max(fixed["critical_point_intervals"][index][1], oracle["critical_point_intervals"][index][1])
            intervals.append((lower, upper))
            spans.append((upper - lower) / domain)
        output[name] = {"resolved": True, "critical_point_intervals": intervals, "normalized_spans": spans, "maximum_normalized_span": max(spans, default=0.0)}
    return output


def short_audit(parameters, section, cycle, initial, cpu_manifest, manifest, solver):
    audit = manifest["short_horizon_audit"]
    ids = np.asarray(audit["trajectory_ids"], dtype=int)
    capture = {**cpu_manifest["capture"], "radius": audit["disabled_capture_radius"], "required_crossings": audit["disabled_capture_crossings"]}
    gpu = integrate_gpu(
        parameters, initial[ids], section, cycle, dt=float(audit["dt"]),
        horizon=float(audit["horizon"]), checkpoints=(float(audit["horizon"]),),
        midpoint=(0.0, float(audit["horizon"])), capture=capture,
        escape_radius=float(cpu_manifest["ensemble"]["escape_radius"]),
        chunk_steps=int(manifest["gpu"]["chunk_steps"]), max_crossings=int(audit["max_crossings"]),
    )
    axes = np.asarray(cpu_manifest["capture"]["coordinate_axes"], dtype=int)
    scales = np.asarray(cpu_manifest["capture"]["coordinate_scales"], dtype=float)
    rows = []
    for local_id, trajectory_id in enumerate(ids):
        adaptive = collect_crossings(
            parameters, initial[trajectory_id], section, transient=0.0,
            observation_horizon=float(audit["horizon"]), max_crossings=int(audit["max_crossings"]), config=solver,
        )
        retained = adaptive.times > 0.5 * float(audit["dt"])
        adaptive_times, adaptive_states = adaptive.times[retained], adaptive.states[retained]
        count = min(len(gpu["times"][local_id]), len(adaptive_times), int(audit["comparison_crossings"]))
        if count:
            delta = (adaptive_states[:count, axes] - gpu["states"][local_id][:count, axes]) / scales
            state_error = float(np.max(np.linalg.norm(delta, axis=1)))
            time_error = float(np.max(np.abs(adaptive_times[:count] - gpu["times"][local_id][:count])))
        else:
            state_error = time_error = 1e300
        rows.append({"trajectory_id": int(trajectory_id), "comparison_crossings": count, "maximum_scaled_state_error": state_error, "maximum_time_error": time_error, "dop853_success": adaptive.integration_success})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cpu-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    manifest_bytes, cpu_bytes = args.manifest.read_bytes(), args.cpu_manifest.read_bytes()
    manifest, cpu_manifest = json.loads(manifest_bytes), json.loads(cpu_bytes)
    if manifest.get("schema") != "butterfly.gpu-sprinkler-parity-manifest.v1":
        raise SystemExit("unsupported manifest")
    if sha256_bytes(cpu_bytes) != manifest["cpu_manifest_sha256"]:
        raise SystemExit("CPU manifest hash mismatch")
    if len(args.source_commit) != 40 or any(
        value not in "0123456789abcdef" for value in args.source_commit.lower()
    ):
        raise SystemExit("a full source commit is required")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("source commit mismatch")
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable")

    solver = SolverConfig(**cpu_manifest["reference_solver"])
    acceptance = manifest["acceptance"]
    rows = []
    for case in cpu_manifest["cases"]:
        parameters, section, cycle, classification, initial = prepare_case(case, cpu_manifest, solver)
        ensemble = cpu_manifest["ensemble"]
        gpu = integrate_gpu(
            parameters, initial, section, cycle, dt=float(ensemble["dt"]),
            horizon=float(ensemble["horizon"]), checkpoints=ensemble["checkpoint_times"],
            midpoint=tuple(ensemble["midpoint_window"]), capture=cpu_manifest["capture"],
            escape_radius=float(ensemble["escape_radius"]), chunk_steps=int(manifest["gpu"]["chunk_steps"]),
            max_crossings=int(manifest["gpu"]["max_recorded_crossings"]),
        )
        coordinates = gpu_coordinate_summary(gpu, cpu_manifest, manifest)
        expected = int(case["expected_saddle_branch_count"])
        reference = manifest["cpu_reference"][case["id"]]
        survivor_difference = float(np.max(np.abs(np.asarray(reference["survivor_counts"]) - gpu["survivor_counts"]) / len(initial)))
        critical = compare_critical(reference["coordinates"], coordinates, expected)
        audit = short_audit(parameters, section, cycle, initial, cpu_manifest, manifest, solver)
        required_audit_crossings = manifest["short_horizon_audit"][
            "comparison_crossings"
        ]
        passed = bool(
            classification.label == OrbitLabel.PERIODIC
            and classification.fundamental_period == int(case["stable_period"])
            and not np.any(gpu["failed"])
            and survivor_difference <= acceptance["maximum_survivor_fraction_difference"]
            and all(
                value["pair_count"] >= acceptance["minimum_return_pairs"]
                and value["robust_oracle"]["resolved"]
                and value["robust_oracle"]["branch_count"] == expected
                and value["robust_oracle"]["variant_consensus"] >= acceptance["minimum_oracle_variant_consensus"]
                and critical[name]["maximum_normalized_span"] <= acceptance["maximum_across_backend_critical_span"]
                for name, value in coordinates.items()
            )
            and all(
                value["dop853_success"]
                and value["comparison_crossings"] >= required_audit_crossings
                and value["maximum_scaled_state_error"] <= acceptance["maximum_short_horizon_scaled_state_error"]
                and value["maximum_time_error"] <= acceptance["maximum_short_horizon_time_error"]
                for value in audit
            )
        )
        row = {
            "id": case["id"], "parameters": asdict(parameters), "expected_branch_count": expected,
            "cycle_classification": asdict(classification), "gpu_survivor_counts": gpu["survivor_counts"].tolist(),
            "cpu_reference_survivor_counts": reference["survivor_counts"],
            "maximum_survivor_fraction_difference": survivor_difference,
            "gpu_final_survivor_count": len(gpu["survivor_ids"]), "gpu_failed_count": int(np.count_nonzero(gpu["failed"])),
            "gpu_elapsed_seconds": gpu["elapsed_seconds"], "gpu_state_steps_per_second": gpu["state_steps_per_second"],
            "gpu_coordinates": coordinates, "critical_point_backend_comparison": critical,
            "short_horizon_audit": audit, "passed": passed,
        }
        rows.append(row)
        print(json.dumps({"id": row["id"], "gpu_survivors": row["gpu_survivor_counts"], "gpu_branches": {name: value["robust_oracle"]["branch_count"] for name, value in coordinates.items()}, "passed": passed}, sort_keys=True), flush=True)

    props = torch.cuda.get_device_properties(0)
    output = {
        "schema": "butterfly.gpu-sprinkler-parity.v1", "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes), "cpu_manifest_sha256": sha256_bytes(cpu_bytes),
        "source": {"declared_commit": args.source_commit, "observed_git_commit": observed_commit, "branch": git_value("branch", "--show-current"), "dirty": bool(git_value("status", "--porcelain"))},
        "environment": {"hostname": platform.node(), "platform": platform.platform(), "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "torch": torch.__version__, "torch_cuda": torch.version.cuda, "triton": triton.__version__, "gpu_name": torch.cuda.get_device_name(0), "gpu_memory_bytes": props.total_memory, "gpu_compute_capability": [props.major, props.minor], "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")},
        "cases": rows, "passed": all(row["passed"] for row in rows),
        "scientific_scope": "Float64 CPU/GPU statistical parity on the two qualified sprinkler controls; no chaotic trajectory identity or TBA-curve claim",
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps({"output": str(args.output), "passed": output["passed"]}))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
