#!/usr/bin/env python3
"""Construct and independently verify the analytic Rössler Hopf curve."""

from __future__ import annotations

import argparse
import json
import os
import platform
import tempfile
import time
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "butterfly-matplotlib-cache")
)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.optimize import brentq

from butterfly import (
    RosslerParameters,
    equilibrium_eigenvalues,
    rossler_equilibrium_characteristic_coefficients,
    rossler_hopf_points,
    rossler_jacobian,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _pair_and_real(values):
    real_index = int(np.argmin(np.abs(values.imag)))
    pair_indices = [index for index in range(3) if index != real_index]
    return values[pair_indices], values[real_index]


def _pair_real(a, b, c, equilibrium_index):
    values = equilibrium_eigenvalues(RosslerParameters(a=a, b=b, c=c))[
        equilibrium_index
    ]
    pair, _real = _pair_and_real(values)
    return float(np.mean(pair.real))


def _row(point, manifest):
    p = point.parameters
    acceptance = manifest["acceptance"]
    equilibrium = point.equilibrium
    coefficients = rossler_equilibrium_characteristic_coefficients(p, equilibrium)
    A, B, C = map(float, coefficients)
    values = equilibrium_eigenvalues(p)[point.equilibrium_index]
    pair, real_value = _pair_and_real(values)
    pair_real = float(np.max(np.abs(pair.real)))
    pair_frequency = float(np.mean(np.abs(pair.imag)))
    polynomial = np.poly(rossler_jacobian(equilibrium, p)).real
    coefficient_error = float(
        np.max(np.abs(polynomial[1:] - coefficients))
    )
    equilibrium_residual = float(np.max(np.abs(rossler_rhs(0.0, equilibrium, p))))
    root_half_width = float(manifest["cross_checks"]["root_bracket_half_width"])
    root_c = float(
        brentq(
            lambda c: _pair_real(p.a, p.b, c, point.equilibrium_index),
            p.c - root_half_width,
            p.c + root_half_width,
            xtol=float(manifest["cross_checks"]["brent_xtol"]),
            rtol=float(manifest["cross_checks"]["brent_rtol"]),
        )
    )
    delta = float(manifest["cross_checks"]["transversality_delta_c"])
    left_real = _pair_real(p.a, p.b, p.c - delta, point.equilibrium_index)
    right_real = _pair_real(p.a, p.b, p.c + delta, point.equilibrium_index)
    checks = {
        "equilibrium_residual": equilibrium_residual,
        "routh_residual": abs(A * B - C),
        "characteristic_coefficient_error": coefficient_error,
        "complex_pair_real_error": pair_real,
        "frequency_error": abs(pair_frequency - point.angular_frequency),
        "brent_root_c_error": abs(root_c - p.c),
        "left_pair_real": left_real,
        "right_pair_real": right_real,
    }
    passed = bool(
        point.equilibrium_index == acceptance["required_equilibrium_index"]
        and real_value.real < -acceptance["minimum_real_eigenvalue_magnitude"]
        and equilibrium_residual <= acceptance["maximum_equilibrium_residual"]
        and checks["routh_residual"] <= acceptance["maximum_routh_residual"]
        and coefficient_error
        <= acceptance["maximum_characteristic_coefficient_error"]
        and pair_real <= acceptance["maximum_complex_pair_real_error"]
        and checks["frequency_error"] <= acceptance["maximum_frequency_error"]
        and checks["brent_root_c_error"] <= acceptance["maximum_brent_root_c_error"]
        and left_real <= -acceptance["minimum_transversality_margin"]
        and right_real >= acceptance["minimum_transversality_margin"]
    )
    return {
        "parameters": {"a": p.a, "b": p.b, "c": p.c},
        "equilibrium_index": point.equilibrium_index,
        "equilibrium": equilibrium.tolist(),
        "characteristic_coefficients": coefficients.tolist(),
        "eigenvalues": [
            {"real": float(value.real), "imag": float(value.imag)} for value in values
        ],
        "angular_frequency": point.angular_frequency,
        "real_eigenvalue": float(real_value.real),
        "independent_brent_root_c": root_c,
        "checks": checks,
        "passed": passed,
    }


def _plot(rows, manifest, output):
    a = np.asarray([row["parameters"]["a"] for row in rows])
    c = np.asarray([row["parameters"]["c"] for row in rows])
    order = np.argsort(a)
    hub = manifest["reported_hub"]
    hub_a, hub_c = float(hub["a"]), float(hub["c"])
    hub_row = min(rows, key=lambda row: abs(row["parameters"]["a"] - hub_a))
    hopf_c = float(hub_row["parameters"]["c"])
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), constrained_layout=True)
    for axis in axes:
        axis.plot(a[order], c[order], color="#7b2cbf", linewidth=2.2, label="analytic Hopf locus")
        axis.scatter([hub_a], [hub_c], color="#d62828", s=42, zorder=5, label="reported hub")
        axis.plot([hub_a, hub_a], [hopf_c, hub_c], color="#111111", linewidth=1.2, linestyle="--", label="fixed-a path")
        axis.scatter([hub_a], [hopf_c], color="#2a9d8f", s=34, zorder=5, label="Hopf start at hub a")
        axis.set_xlabel("a")
        axis.set_ylabel("c")
        axis.grid(alpha=0.22)
    axes[0].set_title("Jones Figure 2 parameter range")
    axes[0].set_xlim(*manifest["figure"]["a_limits"])
    axes[0].set_ylim(*manifest["figure"]["full_c_limits"])
    axes[1].set_title("Hopf locus detail")
    axes[1].set_xlim(*manifest["figure"]["a_limits"])
    axes[1].set_ylim(*manifest["figure"]["detail_c_limits"])
    handles, labels = axes[1].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside lower center", ncol=4, frameon=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp.png")
    figure.savefig(temporary, dpi=180, metadata={"Software": "butterfly"})
    plt.close(figure)
    temporary.replace(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--figure", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.rossler-hopf-curve-manifest.v1":
        raise SystemExit("unsupported Rössler Hopf-curve manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    grid = manifest["grid"]
    a_values = np.linspace(grid["a_min"], grid["a_max"], grid["a_count"])
    a_values = np.unique(np.append(a_values, manifest["reported_hub"]["a"]))
    started = time.perf_counter()
    rows = []
    for a in a_values:
        points = rossler_hopf_points(float(a), float(grid["b"]))
        if len(points) != 1:
            raise SystemExit(f"expected one regular Hopf point at a={a}, got {len(points)}")
        rows.append(_row(points[0], manifest))
    _plot(rows, manifest, args.figure)
    hub_a = float(manifest["reported_hub"]["a"])
    hub_row = min(rows, key=lambda row: abs(row["parameters"]["a"] - hub_a))
    receipt = {
        "schema": "butterfly.rossler-hopf-curve-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "rows": rows,
        "reported_hub_a_hopf_c": hub_row["parameters"]["c"],
        "reported_hub_a_vertical_separation": (
            manifest["reported_hub"]["c"] - hub_row["parameters"]["c"]
        ),
        "figure": str(args.figure),
        "figure_sha256": sha256_bytes(args.figure.read_bytes()),
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(
            len(rows) == manifest["acceptance"]["required_point_count"]
            and all(row["passed"] for row in rows)
        ),
        "scientific_scope": (
            "regular small-equilibrium Hopf locus at fixed b=0.2; not a "
            "periodic-orbit continuation, homoclinic connection, topology-change "
            "curve, or proof of logistic conjugacy"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {key: value for key, value in receipt.items() if key != "rows"},
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
