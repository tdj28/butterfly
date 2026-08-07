#!/usr/bin/env python3
"""Qualify GPU Poincare crossings and period labels against the CPU oracle."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

try:
    import torch
    import triton
    import triton.language as tl
except ImportError as error:  # pragma: no cover - executed on the GPU worker
    raise SystemExit("PyTorch and Triton are required for GPU crossing qualification") from error


@triton.jit
def _hermite_root_step(alpha, previous_y, y, k1y, end_dy, section_y, dt: tl.constexpr):
    """Apply one bounded Newton step to a cubic-Hermite section root."""
    alpha2 = alpha * alpha
    alpha3 = alpha2 * alpha
    h00 = 2.0 * alpha3 - 3.0 * alpha2 + 1.0
    h10 = alpha3 - 2.0 * alpha2 + alpha
    h01 = -2.0 * alpha3 + 3.0 * alpha2
    h11 = alpha3 - alpha2
    value = (
        h00 * previous_y
        + h10 * dt * k1y
        + h01 * y
        + h11 * dt * end_dy
        - section_y
    )
    derivative = (
        (6.0 * alpha2 - 6.0 * alpha) * previous_y
        + (3.0 * alpha2 - 4.0 * alpha + 1.0) * dt * k1y
        + (-6.0 * alpha2 + 6.0 * alpha) * y
        + (3.0 * alpha2 - 2.0 * alpha) * dt * end_dy
    )
    refined = tl.where(
        tl.abs(derivative) > 1.0e-15,
        alpha - value / derivative,
        alpha,
    )
    return tl.maximum(0.0, tl.minimum(1.0, refined))


@triton.jit
def _rk4_crossing_chunk(
    states,
    parameters,
    section_offsets,
    section_gates,
    crossings,
    crossing_counts,
    batch_size,
    step_count,
    dt: tl.constexpr,
    record_crossings: tl.constexpr,
    max_crossings: tl.constexpr,
    block_size: tl.constexpr,
):
    offsets = tl.program_id(0) * block_size + tl.arange(0, block_size)
    valid = offsets < batch_size
    state_base = offsets * 3
    x = tl.load(states + state_base, mask=valid, other=0.0)
    y = tl.load(states + state_base + 1, mask=valid, other=0.0)
    z = tl.load(states + state_base + 2, mask=valid, other=0.0)
    a = tl.load(parameters + state_base, mask=valid, other=0.0)
    b = tl.load(parameters + state_base + 1, mask=valid, other=0.0)
    c = tl.load(parameters + state_base + 2, mask=valid, other=0.0)
    section_y = tl.load(section_offsets + offsets, mask=valid, other=0.0)
    gate_x = tl.load(section_gates + offsets, mask=valid, other=0.0)
    count = tl.load(crossing_counts + offsets, mask=valid, other=0).to(tl.int32)

    for _ in tl.range(0, step_count):
        previous_x = x
        previous_y = y
        previous_z = z

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
        x = x + (dt / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
        y = y + (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
        z = z + (dt / 6.0) * (k1z + 2.0 * k2z + 2.0 * k3z + k4z)

        if record_crossings:
            previous_value = previous_y - section_y
            current_value = y - section_y
            crossed = previous_value * current_value < 0.0
            denominator = previous_value - current_value
            alpha = tl.where(crossed, previous_value / denominator, 0.0)

            # A linearly interpolated section point is only second-order
            # accurate even though the state step is RK4.  That bias is large
            # enough to defeat the deliberately strict recurrence classifier.
            # Refine the root of y(t) - section_y with the cubic Hermite dense
            # interpolant formed from the state and vector field at both ends
            # of the step.  Four bounded Newton iterations retain the crossing
            # bracket and make the recorded x/z section point commensurate
            # with the fourth-order state integration.
            end_dx = -y - z
            end_dy = x + a * y
            end_dz = b + z * (x - c)
            # Keep the four iterations explicitly unrolled. Triton 3.3 cannot
            # lower a nested ``tl.static_range`` inside this runtime step loop.
            alpha = _hermite_root_step(
                alpha, previous_y, y, k1y, end_dy, section_y, dt
            )
            alpha = _hermite_root_step(
                alpha, previous_y, y, k1y, end_dy, section_y, dt
            )
            alpha = _hermite_root_step(
                alpha, previous_y, y, k1y, end_dy, section_y, dt
            )
            alpha = _hermite_root_step(
                alpha, previous_y, y, k1y, end_dy, section_y, dt
            )

            alpha2 = alpha * alpha
            alpha3 = alpha2 * alpha
            h00 = 2.0 * alpha3 - 3.0 * alpha2 + 1.0
            h10 = alpha3 - 2.0 * alpha2 + alpha
            h01 = -2.0 * alpha3 + 3.0 * alpha2
            h11 = alpha3 - alpha2
            cross_x = (
                h00 * previous_x + h10 * dt * k1x + h01 * x + h11 * dt * end_dx
            )
            cross_z = (
                h00 * previous_z + h10 * dt * k1z + h01 * z + h11 * dt * end_dz
            )
            accepted = valid & crossed & (cross_x < gate_x) & (count < max_crossings)
            slot = offsets * max_crossings * 3 + count * 3
            tl.store(crossings + slot, cross_x, mask=accepted)
            tl.store(crossings + slot + 1, section_y, mask=accepted)
            tl.store(crossings + slot + 2, cross_z, mask=accepted)
            count += accepted.to(tl.int32)

    tl.store(states + state_base, x, mask=valid)
    tl.store(states + state_base + 1, y, mask=valid)
    tl.store(states + state_base + 2, z, mask=valid)
    tl.store(crossing_counts + offsets, count, mask=valid)


def section_arrays(parameters: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = parameters[:, 0]
    b = parameters[:, 1]
    c = parameters[:, 2]
    discriminant = c * c - 4.0 * a * b
    if np.any(discriminant < 0.0) or np.any(a == 0.0):
        raise ValueError("GPU legacy section requires positive discriminant and nonzero a")
    root = np.sqrt(discriminant)
    gate = 0.5 * (c - root)
    offset = 0.5 * (-c + root) / a
    return offset, gate


def integrate_gpu_crossings(
    parameters: np.ndarray,
    initial_states: np.ndarray,
    *,
    transient: float,
    observation_horizon: float,
    dt: float,
    chunk_steps: int,
    max_crossings: int,
    dtype: torch.dtype,
) -> tuple[list[np.ndarray], dict[str, float | int | str]]:
    if transient < 0.0 or observation_horizon <= 0.0 or dt <= 0.0:
        raise ValueError("invalid GPU integration horizon")
    transient_steps = round(transient / dt)
    observation_steps = round(observation_horizon / dt)
    if not math.isclose(transient_steps * dt, transient, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("transient must be an integer multiple of dt")
    if not math.isclose(
        observation_steps * dt, observation_horizon, rel_tol=0.0, abs_tol=1e-12
    ):
        raise ValueError("observation horizon must be an integer multiple of dt")
    device = torch.device("cuda")
    state = torch.as_tensor(initial_states, dtype=dtype, device=device).contiguous()
    parameter_tensor = torch.as_tensor(parameters, dtype=dtype, device=device).contiguous()
    offsets, gates = section_arrays(parameters)
    offset_tensor = torch.as_tensor(offsets, dtype=dtype, device=device)
    gate_tensor = torch.as_tensor(gates, dtype=dtype, device=device)
    crossings = torch.full(
        (len(parameters), max_crossings, 3),
        float("nan"),
        dtype=dtype,
        device=device,
    )
    counts = torch.zeros(len(parameters), dtype=torch.int32, device=device)
    block_size = 128
    grid = (triton.cdiv(len(parameters), block_size),)

    def run_steps(total_steps: int, record: bool) -> None:
        completed = 0
        while completed < total_steps:
            steps = min(chunk_steps, total_steps - completed)
            _rk4_crossing_chunk[grid](
                state,
                parameter_tensor,
                offset_tensor,
                gate_tensor,
                crossings,
                counts,
                len(parameters),
                steps,
                dt=dt,
                record_crossings=record,
                max_crossings=max_crossings,
                block_size=block_size,
                num_warps=4,
            )
            completed += steps
            if record and completed % (chunk_steps * 16) == 0:
                if bool(torch.all(counts >= max_crossings).item()):
                    break

    torch.cuda.synchronize()
    started = time.perf_counter()
    run_steps(transient_steps, False)
    run_steps(observation_steps, True)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    host_counts = counts.cpu().numpy()
    host_crossings = crossings.cpu().double().numpy()
    records = [host_crossings[index, : int(count)] for index, count in enumerate(host_counts)]
    integrated_steps = transient_steps + observation_steps
    return records, {
        "dtype": str(dtype).removeprefix("torch."),
        "batch": len(parameters),
        "dt": dt,
        "transient_steps": transient_steps,
        "observation_steps": observation_steps,
        "elapsed_seconds": elapsed,
        "state_steps_per_second": len(parameters) * integrated_steps / elapsed,
        "minimum_crossing_count": int(host_counts.min()),
        "maximum_crossing_count": int(host_counts.max()),
    }


def cyclic_orbit_error(reference: np.ndarray, candidate: np.ndarray, period: int) -> float:
    reference_tail = reference[-period:]
    candidate_tail = candidate[-period:]
    return min(
        float(np.max(np.linalg.norm(reference_tail - np.roll(candidate_tail, shift, axis=0), axis=1)))
        for shift in range(period)
    )


def cpu_controls(manifest: dict) -> tuple[list[np.ndarray], list[dict]]:
    solver = SolverConfig(**manifest["cpu_solver"])
    classifier = manifest["classifier"]
    records = []
    rows = []
    for control in manifest["controls"]:
        parameters = RosslerParameters(
            a=float(control["a"]), b=float(control["b"]), c=float(control["c"])
        )
        crossings = collect_crossings(
            parameters,
            tuple(map(float, control["initial_state"])),
            legacy_rossler_section(parameters),
            transient=float(manifest["integration"]["transient"]),
            observation_horizon=float(manifest["integration"]["observation_horizon"]),
            max_crossings=int(manifest["integration"]["max_crossings"]),
            config=solver,
        )
        classification = classify_fundamental_period(
            crossings.states,
            max_period=int(classifier["max_period"]),
            required_repeats=int(classifier["required_repeats"]),
            atol=float(classifier["atol"]),
            rtol=float(classifier["rtol"]),
        )
        records.append(crossings.states)
        rows.append(
            {
                "id": control["id"],
                "expected_period": int(control["expected_period"]),
                "label": classification.label.value,
                "fundamental_period": classification.fundamental_period,
                "recurrence_error": classification.recurrence_error,
                "crossing_count": len(crossings.times),
                "integration_success": crossings.integration_success,
            }
        )
    return records, rows


def benchmark(manifest: dict, dtype: torch.dtype) -> dict:
    config = manifest["benchmark"]
    batch = int(config["batch"])
    indices = np.arange(batch, dtype=np.float64)
    fractions = indices / max(batch - 1, 1)
    parameters = np.column_stack(
        (
            0.22 + 0.14 * fractions,
            np.full(batch, 0.2),
            5.0 + 10.0 * np.remainder(indices * 0.61803398875, 1.0),
        )
    )
    states = np.tile(np.asarray((0.0, 4.0, 0.0)), (batch, 1))
    _, performance = integrate_gpu_crossings(
        parameters,
        states,
        transient=float(config["horizon"]),
        observation_horizon=float(config["dt"]),
        dt=float(config["dt"]),
        chunk_steps=int(config["chunk_steps"]),
        max_crossings=1,
        dtype=dtype,
    )
    performance["scientific_scope"] = "raw fixed-step ensemble throughput; no classification"
    return performance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.gpu-crossing-qualification-manifest.v1":
        raise SystemExit("unsupported GPU crossing qualification manifest")
    if len(args.source_commit) != 40 or any(
        character not in "0123456789abcdef" for character in args.source_commit.lower()
    ):
        raise SystemExit("--source-commit must be a full hexadecimal Git commit")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("declared source commit differs from the checked-out commit")
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available")

    reference_records, reference_rows = cpu_controls(manifest)
    controls = manifest["controls"]
    parameters = np.asarray([[row["a"], row["b"], row["c"]] for row in controls], dtype=np.float64)
    initial_states = np.asarray([row["initial_state"] for row in controls], dtype=np.float64)
    classifier = manifest["classifier"]
    gpu_runs = []
    acceptance = manifest["acceptance"]
    for dt in manifest["gpu"]["dt_values"]:
        records, performance = integrate_gpu_crossings(
            parameters,
            initial_states,
            transient=float(manifest["integration"]["transient"]),
            observation_horizon=float(manifest["integration"]["observation_horizon"]),
            dt=float(dt),
            chunk_steps=int(manifest["gpu"]["chunk_steps"]),
            max_crossings=int(manifest["integration"]["max_crossings"]),
            dtype=torch.float64,
        )
        rows = []
        for control, reference, crossings in zip(controls, reference_records, records, strict=True):
            classification = classify_fundamental_period(
                crossings,
                max_period=int(classifier["max_period"]),
                required_repeats=int(classifier["required_repeats"]),
                atol=float(classifier["atol"]),
                rtol=float(classifier["rtol"]),
            )
            expected = int(control["expected_period"])
            error = (
                cyclic_orbit_error(reference, crossings, expected)
                if len(reference) >= expected and len(crossings) >= expected
                else None
            )
            rows.append(
                {
                    "id": control["id"],
                    "label": classification.label.value,
                    "fundamental_period": classification.fundamental_period,
                    "recurrence_error": classification.recurrence_error,
                    "crossing_count": len(crossings),
                    "cyclic_orbit_error_vs_cpu": error,
                    "period_parity": classification.fundamental_period == expected,
                    "orbit_error_passed": (
                        error is not None and error <= float(acceptance["max_cyclic_orbit_error"])
                    ),
                }
            )
        gpu_runs.append(
            {
                "dt": float(dt),
                "performance": performance,
                "controls": rows,
                "passed": all(row["period_parity"] and row["orbit_error_passed"] for row in rows),
            }
        )

    properties = torch.cuda.get_device_properties(0)
    receipt = {
        "schema": "butterfly.gpu-crossing-qualification-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source": {
            "commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "cpu_controls": reference_rows,
        "gpu_runs": gpu_runs,
        "benchmark": benchmark(manifest, torch.float64),
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
            "gpu_memory_bytes": properties.total_memory,
            "gpu_compute_capability": [properties.major, properties.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "passed": all(run["passed"] for run in gpu_runs),
        "scientific_scope": (
            "Float64 fixed-step RK4 Poincare crossing, recurrence-period parity, "
            "and raw throughput on frozen stable periodic controls. Chaotic "
            "trajectory identity and Lyapunov parity are not claimed."
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({"output": str(args.output), "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
