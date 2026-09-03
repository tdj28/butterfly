#!/usr/bin/env python3
"""Qualify coexisting periodic cycles with closure and Floquet diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    flow_monodromy,
    legacy_rossler_section,
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
    if manifest.get("schema") != "butterfly.periodic-coexistence-manifest.v1":
        raise SystemExit("unsupported periodic coexistence manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("periodic coexistence qualification requires clean source")

    solver = SolverConfig(**manifest["solver"])
    crossing_config = manifest["crossings"]
    acceptance = manifest["acceptance"]
    results = []
    for case in manifest["cases"]:
        parameters = RosslerParameters(
            a=float(case["a"]), b=float(case["b"]), c=float(case["c"])
        )
        basins = []
        for basin in case["basins"]:
            initial_state = tuple(map(float, basin["initial_state"]))
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
            period = recurrence.fundamental_period
            orbit = None
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
                orbit = {
                    "period_time": period_time,
                    "section_state": crossings.states[start_index].tolist(),
                    "crossing_closure_error": float(
                        np.linalg.norm(crossings.states[-1] - crossings.states[start_index])
                    ),
                    "flow_closure_error": monodromy.closure_error,
                    "multipliers": complex_values(monodromy.multipliers),
                    "neutral_multiplier_error": float(
                        abs(monodromy.multipliers[neutral_index] - 1.0)
                    ),
                    "max_nontrivial_multiplier_modulus": float(np.max(np.abs(nontrivial))),
                    "predicted_determinant": monodromy.predicted_determinant,
                    "computed_determinant": monodromy.computed_determinant,
                    "integration_success": monodromy.success,
                }
            checks = {
                "integration_success": crossings.integration_success,
                "periodic_label": recurrence.label == OrbitLabel.PERIODIC,
                "expected_period": period == int(basin["expected_period"]),
                "orbit_available": orbit is not None,
                "flow_closure": (
                    orbit is not None
                    and orbit["flow_closure_error"] <= float(acceptance["max_flow_closure_error"])
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
            basins.append(
                {
                    "id": basin["id"],
                    "initial_state": list(initial_state),
                    "expected_period": int(basin["expected_period"]),
                    "label": recurrence.label.value,
                    "fundamental_period": period,
                    "recurrence_error": recurrence.recurrence_error,
                    "recurrence_tolerance": recurrence.recurrence_tolerance,
                    "crossing_count": len(crossings.times),
                    "orbit": orbit,
                    "checks": checks,
                    "passed": all(checks.values()),
                }
            )
        distinct_periods = len({basin["fundamental_period"] for basin in basins}) == len(basins)
        results.append(
            {
                "id": case["id"],
                "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
                "basins": basins,
                "distinct_periods": distinct_periods,
                "passed": distinct_periods and all(basin["passed"] for basin in basins),
            }
        )
    receipt = {
        "schema": "butterfly.periodic-coexistence-receipt.v1",
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
        "interpretation_limit": (
            "Two stable near-closed cycles support persistent multistability for "
            "the sampled basins but do not yet map the basin boundary or certify "
            "the cycles with interval arithmetic."
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({"output": str(args.output), "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
