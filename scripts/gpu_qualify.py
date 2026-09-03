#!/usr/bin/env python3
"""Qualify a CUDA batched Rössler kernel against the adaptive CPU reference.

This is a throughput/correctness gate, not a paper-scale scan. It compares a
fixed-step batched RK4 CUDA path with SciPy DOP853 on a frozen parameter grid,
then measures Float64 and Float32 state-step throughput on the same GPU.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

try:
    import torch
except ImportError as error:  # pragma: no cover - exercised on the GPU worker
    raise SystemExit("PyTorch is required for GPU qualification") from error


def rossler_rhs_torch(
    state: torch.Tensor, parameters: torch.Tensor
) -> torch.Tensor:
    x, y, z = state.unbind(dim=1)
    a, b, c = parameters.unbind(dim=1)
    return torch.stack((-y - z, x + a * y, b + z * (x - c)), dim=1)


def rk4_ensemble(
    state: torch.Tensor, parameters: torch.Tensor, dt: float, steps: int
) -> torch.Tensor:
    for _ in range(steps):
        k1 = rossler_rhs_torch(state, parameters)
        k2 = rossler_rhs_torch(state + 0.5 * dt * k1, parameters)
        k3 = rossler_rhs_torch(state + 0.5 * dt * k2, parameters)
        k4 = rossler_rhs_torch(state + dt * k3, parameters)
        state = state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return state


def reference_endpoints(parameters: np.ndarray, horizon: float) -> np.ndarray:
    initial = np.asarray((0.0, 4.0, 0.0), dtype=np.float64)
    endpoints = []
    for a, b, c in parameters:
        def rhs(_time: float, state: np.ndarray) -> tuple[float, float, float]:
            x, y, z = state
            return -y - z, x + a * y, b + z * (x - c)

        result = solve_ivp(
            rhs,
            (0.0, horizon),
            initial,
            method="DOP853",
            rtol=1e-12,
            atol=1e-14,
            max_step=0.01,
        )
        if not result.success:
            raise RuntimeError(result.message)
        endpoints.append(result.y[:, -1])
    return np.asarray(endpoints)


def parameter_grid(side: int) -> np.ndarray:
    a_values = np.linspace(0.175, 0.185, side)
    c_values = np.linspace(10.1, 10.5, side)
    aa, cc = np.meshgrid(a_values, c_values, indexing="ij")
    return np.column_stack(
        (aa.ravel(), np.full(aa.size, 0.2, dtype=np.float64), cc.ravel())
    )


def cuda_endpoint(
    parameters: np.ndarray, *, dtype: torch.dtype, dt: float, steps: int
) -> np.ndarray:
    device = torch.device("cuda")
    parameter_tensor = torch.as_tensor(parameters, dtype=dtype, device=device)
    state = torch.tensor((0.0, 4.0, 0.0), dtype=dtype, device=device).repeat(
        len(parameters), 1
    )
    with torch.no_grad():
        result = rk4_ensemble(state, parameter_tensor, dt, steps)
    torch.cuda.synchronize()
    return result.cpu().double().numpy()


def benchmark(
    *, batch: int, steps: int, dt: float, dtype: torch.dtype
) -> dict[str, float | int | str]:
    device = torch.device("cuda")
    index = torch.arange(batch, device=device, dtype=torch.float64)
    fraction = index / max(batch - 1, 1)
    parameters = torch.stack(
        (
            0.175 + 0.010 * fraction,
            torch.full_like(fraction, 0.2),
            10.1 + 0.4 * torch.remainder(index * 0.61803398875, 1.0),
        ),
        dim=1,
    ).to(dtype=dtype)
    state = torch.tensor((0.0, 4.0, 0.0), dtype=dtype, device=device).repeat(batch, 1)
    with torch.no_grad():
        rk4_ensemble(state[: min(batch, 1024)], parameters[: min(batch, 1024)], dt, 10)
        torch.cuda.synchronize()
        started = time.perf_counter()
        final = rk4_ensemble(state, parameters, dt, steps)
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
    if not torch.isfinite(final).all():
        raise RuntimeError(f"non-finite {dtype} benchmark result")
    return {
        "dtype": str(dtype).removeprefix("torch."),
        "batch": batch,
        "steps": steps,
        "elapsed_seconds": elapsed,
        "trajectories_per_second": batch / elapsed,
        "state_steps_per_second": batch * steps / elapsed,
    }


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ("git", *args), text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=int, default=32768)
    parser.add_argument("--benchmark-steps", type=int, default=1000)
    parser.add_argument("--parity-steps", type=int, default=2000)
    parser.add_argument("--dt", type=float, default=0.001)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available")

    frozen_parameters = parameter_grid(4)
    horizon = args.dt * args.parity_steps
    reference = reference_endpoints(frozen_parameters, horizon)
    float64 = cuda_endpoint(
        frozen_parameters,
        dtype=torch.float64,
        dt=args.dt,
        steps=args.parity_steps,
    )
    float32 = cuda_endpoint(
        frozen_parameters,
        dtype=torch.float32,
        dt=args.dt,
        steps=args.parity_steps,
    )
    error64 = np.max(np.abs(float64 - reference), axis=0)
    error32 = np.max(np.abs(float32 - reference), axis=0)
    pass64 = bool(np.max(error64) < 1e-8)
    pass32 = bool(np.max(error32) < 2e-4)

    properties = torch.cuda.get_device_properties(0)
    receipt = {
        "schema": "butterfly.gpu-qualification.v1",
        "passed": pass64 and pass32,
        "scientific_scope": (
            "short-horizon endpoint parity and raw batched RK4 throughput only; "
            "not period-classification parity"
        ),
        "source": {
            "commit": git_value("rev-parse", "HEAD"),
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "parity": {
            "grid": {"a": [0.175, 0.185, 4], "b": 0.2, "c": [10.1, 10.5, 4]},
            "initial_state": [0.0, 4.0, 0.0],
            "dt": args.dt,
            "steps": args.parity_steps,
            "horizon": horizon,
            "reference": {
                "solver": "DOP853",
                "rtol": 1e-12,
                "atol": 1e-14,
                "max_step": 0.01,
            },
            "float64_max_abs_error_by_state": error64.tolist(),
            "float32_max_abs_error_by_state": error32.tolist(),
            "float64_threshold": 1e-8,
            "float32_threshold": 2e-4,
            "float64_passed": pass64,
            "float32_passed": pass32,
        },
        "benchmarks": [
            benchmark(
                batch=args.batch,
                steps=args.benchmark_steps,
                dt=args.dt,
                dtype=torch.float64,
            ),
            benchmark(
                batch=args.batch,
                steps=args.benchmark_steps,
                dt=args.dt,
                dtype=torch.float32,
            ),
        ],
        "environment": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_bytes": properties.total_memory,
            "gpu_compute_capability": [properties.major, properties.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    args.output.write_text(rendered, encoding="utf-8")
    digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    print(json.dumps({"output": str(args.output), "sha256": digest, "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
