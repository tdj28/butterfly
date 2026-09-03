#!/usr/bin/env python3
"""Distinguish persistent multistability from long transient periodic capture."""

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
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.transient-capture-manifest.v1":
        raise SystemExit("unsupported transient-capture manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("transient-capture qualification requires clean source")
    solver = SolverConfig(**manifest["solver"])
    classifier = manifest["classifier"]
    case_results = []
    for case in manifest["cases"]:
        parameters = RosslerParameters(
            a=float(case["a"]), b=float(case["b"]), c=float(case["c"])
        )
        initial_results = []
        for initial_state_value in case["initial_states"]:
            initial_state = tuple(map(float, initial_state_value))
            timeline = []
            for transient in manifest["transient_checkpoints"]:
                crossings = collect_crossings(
                    parameters,
                    initial_state,
                    legacy_rossler_section(parameters),
                    transient=float(transient),
                    observation_horizon=float(manifest["observation_horizon"]),
                    max_crossings=int(manifest["max_crossings"]),
                    config=solver,
                )
                classification = classify_fundamental_period(
                    crossings.states,
                    max_period=int(classifier["max_period"]),
                    required_repeats=int(classifier["required_repeats"]),
                    atol=float(classifier["atol"]),
                    rtol=float(classifier["rtol"]),
                )
                timeline.append(
                    {
                        "transient": transient,
                        "label": classification.label.value,
                        "fundamental_period": classification.fundamental_period,
                        "recurrence_error": classification.recurrence_error,
                        "recurrence_tolerance": classification.recurrence_tolerance,
                        "crossing_count": len(crossings.times),
                        "integration_success": crossings.integration_success,
                    }
                )
            final = timeline[-1]
            initial_results.append(
                {
                    "initial_state": list(initial_state),
                    "timeline": timeline,
                    "final_expected_period": (
                        final["label"] == OrbitLabel.PERIODIC.value
                        and final["fundamental_period"] == case["expected_period"]
                    ),
                    "had_earlier_unresolved_window": any(
                        item["label"] == OrbitLabel.UNRESOLVED.value
                        for item in timeline[:-1]
                    ),
                }
            )
        case_passed = all(
            item["final_expected_period"] for item in initial_results
        ) and any(item["had_earlier_unresolved_window"] for item in initial_results)
        case_results.append(
            {
                "id": case["id"],
                "parameters": {
                    "a": parameters.a,
                    "b": parameters.b,
                    "c": parameters.c,
                },
                "expected_period": case["expected_period"],
                "initial_conditions": initial_results,
                "passed": case_passed,
            }
        )
    receipt = {
        "schema": "butterfly.transient-capture-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "results": case_results,
        "passed": all(case["passed"] for case in case_results),
        "interpretation_limit": (
            "Unresolved-to-periodic finite-time capture supports long transient "
            "dynamics but does not by itself certify a chaotic saddle."
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({"output": str(args.output), "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
