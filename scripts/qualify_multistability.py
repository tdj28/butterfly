#!/usr/bin/env python3
"""Replicate focused periodic/chaotic coexistence with Floquet diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from butterfly import (
    LyapunovConfig,
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    classify_with_lyapunov,
    collect_crossings,
    flow_monodromy,
    largest_lyapunov_two_trajectory,
    legacy_rossler_section,
    lyapunov_block_estimates,
    lyapunov_spectrum,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def complex_values(values: np.ndarray) -> list[dict[str, float]]:
    return [
        {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
        for value in values
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.focused-multistability-manifest.v1":
        raise SystemExit("unsupported focused multistability manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("focused multistability qualification requires clean source")

    solver = SolverConfig(**manifest["solver"])
    crossing_config = manifest["crossings"]
    lyapunov_config_value = manifest["lyapunov"]
    lyapunov_config = LyapunovConfig(
        transient=float(lyapunov_config_value["transient"]),
        duration=float(lyapunov_config_value["duration"]),
        qr_interval=float(lyapunov_config_value["qr_interval"]),
        solver=solver,
    )
    acceptance = manifest["acceptance"]
    results = []
    for case in manifest["cases"]:
        parameters = RosslerParameters(
            a=float(case["a"]), b=float(case["b"]), c=float(case["c"])
        )
        state_results = {}
        for role in ("chaotic", "periodic"):
            initial_state = tuple(map(float, case[f"{role}_initial_state"]))
            crossings = collect_crossings(
                parameters,
                initial_state,
                legacy_rossler_section(parameters),
                transient=float(crossing_config["transient"]),
                observation_horizon=float(crossing_config["observation_horizon"]),
                max_crossings=int(crossing_config["max_crossings"]),
                config=solver,
            )
            recurrence = classify_fundamental_period(
                crossings.states,
                max_period=int(crossing_config["max_period"]),
                required_repeats=int(crossing_config["required_repeats"]),
                atol=float(crossing_config["atol"]),
                rtol=float(crossing_config["rtol"]),
            )
            spectrum = lyapunov_spectrum(
                parameters, initial_state, config=lyapunov_config
            )
            blocks = lyapunov_block_estimates(
                spectrum, blocks=int(lyapunov_config_value["blocks"])
            )
            standard_error = np.std(blocks, axis=0, ddof=1) / np.sqrt(len(blocks))
            classification = classify_with_lyapunov(
                recurrence, spectrum.exponents, standard_error
            )
            state_result = {
                "initial_state": list(initial_state),
                "label": classification.label.value,
                "fundamental_period": classification.fundamental_period,
                "recurrence_error": recurrence.recurrence_error,
                "recurrence_tolerance": recurrence.recurrence_tolerance,
                "crossing_count": len(crossings.times),
                "lyapunov_exponents": spectrum.exponents.tolist(),
                "lyapunov_block_standard_error": standard_error.tolist(),
                "trace_identity_error": spectrum.trace_identity_error,
            }
            if role == "chaotic":
                independent = largest_lyapunov_two_trajectory(
                    parameters,
                    initial_state,
                    config=lyapunov_config,
                    perturbation=float(
                        lyapunov_config_value["two_trajectory_perturbation"]
                    ),
                )
                state_result["independent_largest_exponent"] = independent.exponent
                state_result["largest_exponent_difference"] = abs(
                    independent.exponent - float(spectrum.exponents[0])
                )
            else:
                period = recurrence.fundamental_period
                if period is not None and len(crossings.times) >= period + 1:
                    start_index = -period - 1
                    period_time = float(crossings.times[-1] - crossings.times[start_index])
                    monodromy = flow_monodromy(
                        parameters,
                        crossings.states[start_index],
                        period_time,
                        config=solver,
                    )
                    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
                    nontrivial = np.delete(monodromy.multipliers, neutral_index)
                    state_result["orbit"] = {
                        "period_time": period_time,
                        "crossing_closure_error": float(
                            np.linalg.norm(
                                crossings.states[-1] - crossings.states[start_index]
                            )
                        ),
                        "flow_closure_error": monodromy.closure_error,
                        "multipliers": complex_values(monodromy.multipliers),
                        "neutral_multiplier_error": float(
                            abs(monodromy.multipliers[neutral_index] - 1.0)
                        ),
                        "max_nontrivial_multiplier_modulus": float(
                            np.max(np.abs(nontrivial))
                        ),
                        "predicted_determinant": monodromy.predicted_determinant,
                        "computed_determinant": monodromy.computed_determinant,
                    }
            state_results[role] = state_result

        chaotic = state_results["chaotic"]
        periodic = state_results["periodic"]
        orbit = periodic.get("orbit")
        checks = {
            "chaotic_label": chaotic["label"] == OrbitLabel.CHAOTIC.value,
            "periodic_label": periodic["label"] == OrbitLabel.PERIODIC.value,
            "expected_period": periodic["fundamental_period"] == case["expected_period"],
            "trace_identity": max(
                chaotic["trace_identity_error"], periodic["trace_identity_error"]
            )
            <= float(acceptance["max_trace_identity_error"]),
            "independent_largest_exponent": (
                chaotic["independent_largest_exponent"] > 0.0
                and chaotic["largest_exponent_difference"]
                <= float(acceptance["max_largest_exponent_difference"])
            ),
            "neutral_multiplier": (
                orbit is not None
                and orbit["neutral_multiplier_error"]
                <= float(acceptance["max_neutral_multiplier_error"])
            ),
            "transverse_stability": (
                orbit is not None
                and orbit["max_nontrivial_multiplier_modulus"]
                < float(acceptance["max_nontrivial_multiplier_modulus"])
            ),
        }
        results.append(
            {
                "id": case["id"],
                "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
                "expected_period": case["expected_period"],
                "chaotic": chaotic,
                "periodic": periodic,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    receipt = {
        "schema": "butterfly.focused-multistability-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "results": results,
        "passed": all(result["passed"] for result in results),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({"output": str(args.output), "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
