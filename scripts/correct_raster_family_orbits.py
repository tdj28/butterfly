#!/usr/bin/env python3
"""Correct and Floquet-test periodic cycles along persistent raster-family paths."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    correct_periodic_orbit,
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
    if manifest.get("schema") != "butterfly.raster-family-orbit-manifest.v1":
        raise SystemExit("unsupported raster-family orbit manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("raster-family correction requires clean source")

    solver = SolverConfig(**manifest["solver"])
    crossing_config = manifest["crossings"]
    corrector = manifest["corrector"]
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    families = []
    for family in manifest["families"]:
        expected_period = int(family["period"])
        points = []
        for point in family["points"]:
            parameters = RosslerParameters(
                a=float(point["a"]), b=float(point["b"]), c=float(point["c"])
            )
            crossings = collect_crossings(
                parameters,
                tuple(map(float, crossing_config["initial_state"])),
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
            correction = None
            orbit = None
            if (
                recurrence.fundamental_period == expected_period
                and len(crossings.times) >= expected_period + 1
            ):
                start_index = -expected_period - 1
                seed_state = crossings.states[start_index]
                seed_time = float(crossings.times[-1] - crossings.times[start_index])
                corrected = correct_periodic_orbit(
                    parameters,
                    seed_state,
                    seed_time,
                    config=solver,
                    max_evaluations=int(corrector["max_evaluations"]),
                    tolerance=float(corrector["tolerance"]),
                )
                correction = {
                    "initial_state": corrected.initial_state.tolist(),
                    "period_time": corrected.period_time,
                    "closure_error": corrected.closure_error,
                    "phase_residual": corrected.phase_residual,
                    "correction_norm": corrected.correction_norm,
                    "evaluations": corrected.evaluations,
                    "success": corrected.success,
                    "message": corrected.message,
                }
                monodromy = flow_monodromy(
                    parameters,
                    corrected.initial_state,
                    corrected.period_time,
                    config=solver,
                )
                neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
                nontrivial = np.delete(monodromy.multipliers, neutral_index)
                orbit = {
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
                "expected_period": recurrence.label == OrbitLabel.PERIODIC
                and recurrence.fundamental_period == expected_period,
                "correction_available": correction is not None,
                "correction_success": correction is not None and correction["success"],
                "closure": correction is not None
                and correction["closure_error"] <= float(acceptance["max_closure_error"]),
                "phase": correction is not None
                and correction["phase_residual"] <= float(acceptance["max_phase_residual"]),
                "neutral_multiplier": orbit is not None
                and orbit["neutral_multiplier_error"]
                <= float(acceptance["max_neutral_multiplier_error"]),
                "transverse_stability": orbit is not None
                and orbit["max_nontrivial_multiplier_modulus"] < 1.0,
            }
            points.append(
                {
                    "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
                    "expected_period": expected_period,
                    "recurrence_label": recurrence.label.value,
                    "fundamental_period": recurrence.fundamental_period,
                    "recurrence_error": recurrence.recurrence_error,
                    "crossing_count": len(crossings.times),
                    "correction": correction,
                    "orbit": orbit,
                    "checks": checks,
                    "passed": all(checks.values()),
                }
            )
        families.append(
            {
                "id": family["id"],
                "raster_component_id": int(family["raster_component_id"]),
                "period": expected_period,
                "points": points,
                "passed": all(point["passed"] for point in points),
            }
        )
    receipt = {
        "schema": "butterfly.raster-family-orbit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "families": families,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(family["passed"] for family in families),
        "interpretation_limit": (
            "Corrected stable cycles along representative raster paths support family "
            "persistence but do not continue saddle-node or period-doubling boundaries."
        ),
    }
    output_bytes = canonical_json(receipt)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": receipt["passed"],
                "elapsed_seconds": receipt["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
