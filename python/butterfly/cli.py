"""Command-line entry points for reproducible reference checks."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

from .integrate import SolverConfig, integrate_trajectory
from .lyapunov import LyapunovConfig, lyapunov_spectrum
from .models import RosslerParameters, equilibrium_eigenvalues, rossler_equilibria
from .scan import atomic_write, canonical_json, execute_scan, git_value


def _complex_rows(values: np.ndarray) -> list[list[dict[str, float]]]:
    return [
        [{"real": float(value.real), "imag": float(value.imag)} for value in row]
        for row in values
    ]


def verify(output: Path | None) -> int:
    parameters = RosslerParameters(a=0.1798, b=0.2, c=10.3084)
    equilibria = rossler_equilibria(parameters)
    eigenvalues = equilibrium_eigenvalues(parameters)
    trajectory = integrate_trajectory(
        parameters,
        initial_state=(0.0, 4.0, 0.0),
        t_span=(0.0, 10.0),
        config=SolverConfig(),
    )
    receipt = {
        "schema": "butterfly.reference-verification.v1",
        "parameters": {
            "system": "rossler",
            "a": parameters.a,
            "b": parameters.b,
            "c": parameters.c,
        },
        "equilibria": equilibria.tolist(),
        "equilibrium_eigenvalues": _complex_rows(eigenvalues),
        "integration": {
            "initial_state": [0.0, 4.0, 0.0],
            "t_span": [0.0, 10.0],
            "final_state": trajectory.y[:, -1].tolist(),
            "nfev": trajectory.nfev,
            "success": trajectory.success,
            "message": trajectory.message,
            "solver": {
                "method": "DOP853",
                "rtol": 1e-10,
                "atol": 1e-12,
                "max_step": 0.05,
            },
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if output is None:
        print(rendered, end="")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(output)
    return 0 if trajectory.success else 1


def lyapunov_receipt(args: argparse.Namespace) -> tuple[dict, bool]:
    parameters = RosslerParameters(a=args.a, b=args.b, c=args.c)
    solver = SolverConfig(
        method=args.method,
        rtol=args.rtol,
        atol=args.atol,
        max_step=args.max_step,
    )
    config = LyapunovConfig(
        transient=args.transient,
        duration=args.duration,
        qr_interval=args.qr_interval,
        solver=solver,
    )
    result = lyapunov_spectrum(parameters, args.initial_state, config=config)
    checkpoint_count = min(10, len(result.running_exponents))
    if checkpoint_count:
        indices = np.unique(
            np.linspace(0, len(result.running_exponents) - 1, checkpoint_count).astype(int)
        )
        checkpoints = [
            {
                "elapsed": float((index + 1) * args.qr_interval),
                "exponents": result.running_exponents[index].tolist(),
            }
            for index in indices
        ]
    else:
        checkpoints = []
    receipt = {
        "schema": "butterfly.lyapunov-receipt.v1",
        "parameters": {
            "system": "rossler",
            "a": parameters.a,
            "b": parameters.b,
            "c": parameters.c,
        },
        "initial_state": list(map(float, args.initial_state)),
        "config": {
            "transient": config.transient,
            "duration": config.duration,
            "qr_interval": config.qr_interval,
            "solver": {
                "method": solver.method,
                "rtol": solver.rtol,
                "atol": solver.atol,
                "max_step": solver.max_step,
            },
        },
        "result": {
            "success": result.success,
            "message": result.message,
            "exponents": result.exponents.tolist(),
            "mean_divergence": result.mean_divergence,
            "trace_identity_error": result.trace_identity_error,
            "elapsed": result.elapsed,
            "qr_steps": result.qr_steps,
            "final_state": result.final_state.tolist(),
            "convergence_checkpoints": checkpoints,
        },
        "source": {
            "commit": git_value("rev-parse", "HEAD"),
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    return receipt, result.success


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="butterfly")
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify_parser = subparsers.add_parser("verify", help="run the reference-core check")
    verify_parser.add_argument("--output", type=Path)
    scan_parser = subparsers.add_parser("scan", help="execute a frozen CPU scan manifest")
    scan_parser.add_argument("--manifest", type=Path, required=True)
    scan_parser.add_argument("--output-dir", type=Path, required=True)
    lyapunov_parser = subparsers.add_parser(
        "lyapunov", help="compute a variational-equation/QR Lyapunov receipt"
    )
    lyapunov_parser.add_argument("--a", type=float, required=True)
    lyapunov_parser.add_argument("--b", type=float, required=True)
    lyapunov_parser.add_argument("--c", type=float, required=True)
    lyapunov_parser.add_argument(
        "--initial-state", type=float, nargs=3, default=(0.0, 4.0, 0.0)
    )
    lyapunov_parser.add_argument("--transient", type=float, default=100.0)
    lyapunov_parser.add_argument("--duration", type=float, default=1000.0)
    lyapunov_parser.add_argument("--qr-interval", type=float, default=0.5)
    lyapunov_parser.add_argument("--method", default="DOP853")
    lyapunov_parser.add_argument("--rtol", type=float, default=1e-10)
    lyapunov_parser.add_argument("--atol", type=float, default=1e-12)
    lyapunov_parser.add_argument("--max-step", type=float, default=0.05)
    lyapunov_parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "verify":
        return verify(args.output)
    if args.command == "scan":
        receipt = execute_scan(args.manifest, args.output_dir)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    if args.command == "lyapunov":
        receipt, success = lyapunov_receipt(args)
        rendered = canonical_json(receipt)
        if args.output:
            atomic_write(args.output, rendered)
            print(args.output)
        else:
            print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if success else 1
    parser.error(f"unknown command: {args.command}")
    return 2
