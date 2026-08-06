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
from .models import RosslerParameters, equilibrium_eigenvalues, rossler_equilibria


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="butterfly")
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify_parser = subparsers.add_parser("verify", help="run the reference-core check")
    verify_parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "verify":
        return verify(args.output)
    parser.error(f"unknown command: {args.command}")
    return 2
