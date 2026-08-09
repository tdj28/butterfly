#!/usr/bin/env python3
"""Qualify the period-1 family from the Rössler Hopf locus to the Jones hub."""

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

from butterfly import (
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    correct_periodic_orbit,
    equilibrium_eigenvalues,
    flow_monodromy,
    integrate_trajectory,
    legacy_rossler_section,
    rossler_equilibria,
    rossler_hopf_points,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _continuation_c_values(manifest, hopf_c):
    continuation = manifest["continuation"]
    downward = list(map(float, continuation["downward_bridge_c_values"]))
    downward += [
        hopf_c + float(offset)
        for offset in continuation["near_hopf_c_offsets"]
    ]
    downward = sorted(set(downward), reverse=True)
    upward = np.linspace(
        float(continuation["seed_c"]),
        float(continuation["hub_c"]),
        int(continuation["upward_count"]),
    )
    upward = np.unique(
        np.append(upward, np.asarray(continuation["crosscheck_c_values"], dtype=float))
    )
    return downward, upward.tolist()


def _fit_power_law(offsets, amplitudes):
    x = np.log(np.asarray(offsets, dtype=float))
    y = np.log(np.asarray(amplitudes, dtype=float))
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "exponent": float(slope),
        "intercept": float(intercept),
        "r_squared": float(1.0 - residual / total),
    }


def _minus_one_crossings(rows):
    ordered = sorted(rows, key=lambda row: row["parameters"]["c"])
    crossings = []
    for left, right in zip(ordered, ordered[1:]):
        left_mu = left["primary_nontrivial_multiplier"]["real"]
        right_mu = right["primary_nontrivial_multiplier"]["real"]
        if left_mu <= -1.0 < right_mu or right_mu <= -1.0 < left_mu:
            crossings.append(
                {
                    "c_bracket": [left["parameters"]["c"], right["parameters"]["c"]],
                    "multiplier_bracket": [left_mu, right_mu],
                }
            )
    return crossings


def _orbit_row(parameters, correction, solver, sample_count):
    monodromy = flow_monodromy(
        parameters, correction.initial_state, correction.period_time, config=solver
    )
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    nontrivial = np.delete(monodromy.multipliers, neutral_index)
    primary = nontrivial[int(np.argmax(np.abs(nontrivial)))]
    times = np.linspace(0.0, correction.period_time, sample_count)
    trajectory = integrate_trajectory(
        parameters,
        correction.initial_state,
        (0.0, correction.period_time),
        config=solver,
        t_eval=times,
    )
    states = trajectory.y.T
    equilibrium = rossler_equilibria(parameters)[0]
    centered = states - equilibrium
    distances = np.linalg.norm(centered, axis=1)
    angles = np.unwrap(np.arctan2(centered[:, 1], centered[:, 0]))
    winding = float((angles[-1] - angles[0]) / (2.0 * np.pi))
    return {
        "parameters": {
            "a": parameters.a,
            "b": parameters.b,
            "c": parameters.c,
        },
        "initial_state": correction.initial_state.tolist(),
        "period_time": correction.period_time,
        "closure_error": correction.closure_error,
        "phase_residual": correction.phase_residual,
        "correction_norm": correction.correction_norm,
        "corrector_evaluations": correction.evaluations,
        "neutral_multiplier_error": float(
            abs(monodromy.multipliers[neutral_index] - 1.0)
        ),
        "nontrivial_multipliers": [
            {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
            for value in nontrivial
        ],
        "primary_nontrivial_multiplier": {
            "real": float(primary.real),
            "imag": float(primary.imag),
            "modulus": float(abs(primary)),
        },
        "stable": bool(np.max(np.abs(nontrivial)) < 1.0),
        "trajectory_success": trajectory.success,
        "winding_number": winding,
        "rms_equilibrium_distance": float(np.sqrt(np.mean(distances**2))),
        "minimum_equilibrium_distance": float(np.min(distances)),
        "maximum_equilibrium_distance": float(np.max(distances)),
    }


def _correct_sequence(c_values, seed, manifest, solver):
    a = float(manifest["parameters"]["a"])
    b = float(manifest["parameters"]["b"])
    state = seed.initial_state
    period = seed.period_time
    rows = []
    for c in c_values:
        parameters = RosslerParameters(a=a, b=b, c=float(c))
        correction = correct_periodic_orbit(
            parameters,
            state,
            period,
            config=solver,
            max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            tolerance=float(manifest["corrector"]["tolerance"]),
        )
        if not correction.success:
            raise RuntimeError(f"period-1 correction failed at c={c}: {correction.message}")
        row = _orbit_row(
            parameters,
            correction,
            solver,
            int(manifest["diagnostics"]["orbit_sample_count"]),
        )
        rows.append(row)
        state = correction.initial_state
        period = correction.period_time
    return rows


def _crosscheck(rows, manifest):
    solver = SolverConfig(**manifest["independent_solver"])
    output = []
    for target in manifest["continuation"]["crosscheck_c_values"]:
        source = min(rows, key=lambda row: abs(row["parameters"]["c"] - target))
        if abs(source["parameters"]["c"] - target) > 1e-13:
            raise ValueError(f"independent checkpoint absent: c={target}")
        parameters = RosslerParameters(**source["parameters"])
        correction = correct_periodic_orbit(
            parameters,
            source["initial_state"],
            source["period_time"],
            config=solver,
            max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            tolerance=float(manifest["corrector"]["tolerance"]),
        )
        row = _orbit_row(
            parameters,
            correction,
            solver,
            int(manifest["diagnostics"]["orbit_sample_count"]),
        )
        output.append(
            {
                "c": float(target),
                "success": correction.success,
                "state_difference": float(
                    np.linalg.norm(correction.initial_state - source["initial_state"])
                ),
                "period_difference": abs(correction.period_time - source["period_time"]),
                "closure_error": correction.closure_error,
                "neutral_multiplier_error": row["neutral_multiplier_error"],
                "winding_number": row["winding_number"],
            }
        )
    return output


def _plot(rows, hopf_c, manifest, output):
    ordered = sorted(rows, key=lambda row: row["parameters"]["c"])
    c = np.asarray([row["parameters"]["c"] for row in ordered])
    amplitude = np.asarray([row["rms_equilibrium_distance"] for row in ordered])
    period = np.asarray([row["period_time"] for row in ordered])
    multiplier = np.asarray(
        [row["primary_nontrivial_multiplier"]["real"] for row in ordered]
    )
    figure, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
    axes[0].plot(c - hopf_c, amplitude, color="#7b2cbf")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel(r"$c-c_H$")
    axes[0].set_ylabel("RMS distance from equilibrium")
    axes[0].set_title("Hopf branch amplitude")
    axes[1].plot(c, period, color="#277da1")
    axes[1].set_xlabel("c")
    axes[1].set_ylabel("flow period")
    axes[1].set_title("Period-1 family")
    axes[2].plot(c, multiplier, color="#d62828")
    axes[2].axhline(-1.0, color="#111111", linestyle="--", linewidth=1)
    axes[2].set_xlabel("c")
    axes[2].set_ylabel("primary nontrivial multiplier")
    axes[2].set_title("Stability loss")
    for axis in axes:
        axis.grid(alpha=0.22)
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
    if manifest.get("schema") != "butterfly.hopf-period1-to-hub-manifest.v1":
        raise SystemExit("unsupported Hopf-to-hub period-1 manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    started = time.perf_counter()
    a = float(manifest["parameters"]["a"])
    b = float(manifest["parameters"]["b"])
    hopf = rossler_hopf_points(a, b)[0]
    hopf_c = hopf.parameters.c
    solver = SolverConfig(**manifest["reference_solver"])
    seed_c = float(manifest["continuation"]["seed_c"])
    seed_parameters = RosslerParameters(a=a, b=b, c=seed_c)
    equilibrium = rossler_equilibria(seed_parameters)[0]
    initial = equilibrium + np.asarray(manifest["seed"]["equilibrium_perturbation"])
    crossings = collect_crossings(
        seed_parameters,
        initial,
        legacy_rossler_section(seed_parameters),
        transient=float(manifest["seed"]["transient"]),
        observation_horizon=float(manifest["seed"]["observation_horizon"]),
        max_crossings=int(manifest["seed"]["maximum_crossings"]),
        config=solver,
    )
    recurrence = classify_fundamental_period(
        crossings.states,
        max_period=int(manifest["seed"]["maximum_period"]),
        required_repeats=int(manifest["seed"]["required_repeats"]),
        atol=float(manifest["seed"]["recurrence_atol"]),
        rtol=float(manifest["seed"]["recurrence_rtol"]),
    )
    if recurrence.fundamental_period != 1:
        raise SystemExit("seed attractor did not resolve as period 1")
    seed = correct_periodic_orbit(
        seed_parameters,
        crossings.states[-2],
        float(crossings.times[-1] - crossings.times[-2]),
        config=solver,
        max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
        tolerance=float(manifest["corrector"]["tolerance"]),
    )
    downward_c, upward_c = _continuation_c_values(manifest, hopf_c)
    downward = _correct_sequence(downward_c, seed, manifest, solver)
    upward = _correct_sequence(upward_c[1:], seed, manifest, solver)
    seed_row = _orbit_row(
        seed_parameters,
        seed,
        solver,
        int(manifest["diagnostics"]["orbit_sample_count"]),
    )
    rows = list(reversed(downward)) + [seed_row] + upward
    near_limit = float(manifest["diagnostics"]["near_hopf_fit_maximum_offset"])
    near_rows = [
        row for row in rows if 0.0 < row["parameters"]["c"] - hopf_c <= near_limit
    ]
    power_law = _fit_power_law(
        [row["parameters"]["c"] - hopf_c for row in near_rows],
        [row["rms_equilibrium_distance"] for row in near_rows],
    )
    hopf_period = float(2.0 * np.pi / hopf.angular_frequency)
    closest_hopf_row = min(rows, key=lambda row: row["parameters"]["c"] - hopf_c)
    hub_row = min(
        rows,
        key=lambda row: abs(row["parameters"]["c"] - manifest["continuation"]["hub_c"]),
    )
    crossings_minus_one = _minus_one_crossings(rows)
    independent = _crosscheck(rows, manifest)
    _plot(rows, hopf_c, manifest, args.figure)
    acceptance = manifest["acceptance"]
    rows_pass = all(
        row["trajectory_success"]
        and row["closure_error"] <= acceptance["maximum_closure_error"]
        and row["phase_residual"] <= acceptance["maximum_phase_residual"]
        and row["neutral_multiplier_error"]
        <= acceptance["maximum_neutral_multiplier_error"]
        and abs(row["winding_number"] - 1.0)
        <= acceptance["maximum_winding_error"]
        for row in rows
    )
    independent_pass = all(
        row["success"]
        and row["state_difference"] <= acceptance["maximum_cross_solver_state_difference"]
        and row["period_difference"] <= acceptance["maximum_cross_solver_period_difference"]
        and row["closure_error"] <= acceptance["maximum_closure_error"]
        and row["neutral_multiplier_error"]
        <= acceptance["maximum_neutral_multiplier_error"]
        and abs(row["winding_number"] - 1.0)
        <= acceptance["maximum_winding_error"]
        for row in independent
    )
    passed = bool(
        len(rows) == acceptance["required_point_count"]
        and rows_pass
        and independent_pass
        and acceptance["minimum_amplitude_exponent"]
        <= power_law["exponent"]
        <= acceptance["maximum_amplitude_exponent"]
        and power_law["r_squared"] >= acceptance["minimum_amplitude_r_squared"]
        and abs(closest_hopf_row["period_time"] - hopf_period)
        <= acceptance["maximum_near_hopf_period_error"]
        and len(crossings_minus_one) >= acceptance["minimum_minus_one_crossings"]
        and abs(hub_row["parameters"]["c"] - manifest["continuation"]["hub_c"])
        <= 1e-13
    )
    receipt = {
        "schema": "butterfly.hopf-period1-to-hub-receipt.v1",
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
        "hopf": {
            "c": hopf_c,
            "angular_frequency": hopf.angular_frequency,
            "linear_period": hopf_period,
            "equilibrium_eigenvalues": [
                {"real": float(value.real), "imag": float(value.imag)}
                for value in equilibrium_eigenvalues(hopf.parameters)[hopf.equilibrium_index]
            ],
        },
        "seed": {
            "c": seed_c,
            "crossing_count": len(crossings.times),
            "recurrence_error": recurrence.recurrence_error,
        },
        "rows": rows,
        "near_hopf_amplitude_fit": power_law,
        "near_hopf_period_error": abs(closest_hopf_row["period_time"] - hopf_period),
        "minus_one_crossings": crossings_minus_one,
        "independent_solver_checks": independent,
        "hub_orbit": {
            "period_time": hub_row["period_time"],
            "minimum_equilibrium_distance": hub_row["minimum_equilibrium_distance"],
            "maximum_equilibrium_distance": hub_row["maximum_equilibrium_distance"],
            "winding_number": hub_row["winding_number"],
            "primary_nontrivial_multiplier": hub_row["primary_nontrivial_multiplier"],
        },
        "figure": str(args.figure),
        "figure_sha256": sha256_bytes(args.figure.read_bytes()),
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "scientific_scope": (
            "one-winding period-1 family from a qualified supercritical Hopf "
            "neighborhood to the reported hub coordinate; not a homoclinic orbit, "
            "topology-transition curve, or logistic-ordering proof"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {key: value for key, value in receipt.items() if key != "rows"},
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
