#!/usr/bin/env python3
"""Track ambiguous atlas targets across long transient checkpoints."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import platform
from typing import Any

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


def final_outcome(initial_results: list[dict[str, Any]]) -> dict[str, Any]:
    finals = [item["timeline"][-1] for item in initial_results]
    periods = [
        item["fundamental_period"]
        for item in finals
        if item["label"] == "periodic" and item["fundamental_period"] is not None
    ]
    if len(periods) == len(finals) and len(set(periods)) == 1:
        status = "common_periodic_capture"
        consensus = periods[0]
    elif len(periods) == len(finals) and len(set(periods)) > 1:
        status = "distinct_periodic_endpoints"
        consensus = None
    else:
        status = "unresolved_or_nonperiodic"
        consensus = None
    return {
        "status": status,
        "consensus_period": consensus,
        "final_labels": [item["label"] for item in finals],
        "final_periods": [item["fundamental_period"] for item in finals],
    }


def evaluate_checkpoint(
    case: dict[str, Any],
    initial_state_value: list[float],
    transient: float,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    parameters = RosslerParameters(
        a=float(case["a"]), b=float(case["b"]), c=float(case["c"])
    )
    initial_state = tuple(map(float, initial_state_value))
    solver = SolverConfig(**manifest["solver"])
    crossings = collect_crossings(
        parameters,
        initial_state,
        legacy_rossler_section(parameters),
        transient=float(transient),
        observation_horizon=float(manifest["observation_horizon"]),
        max_crossings=int(manifest["max_crossings"]),
        config=solver,
    )
    classifier = manifest["classifier"]
    classification = classify_fundamental_period(
        crossings.states,
        max_period=int(classifier["max_period"]),
        required_repeats=int(classifier["required_repeats"]),
        atol=float(classifier["atol"]),
        rtol=float(classifier["rtol"]),
    )
    return {
        "transient": float(transient),
        "label": classification.label.value,
        "fundamental_period": classification.fundamental_period,
        "recurrence_error": classification.recurrence_error,
        "recurrence_tolerance": classification.recurrence_tolerance,
        "crossing_count": len(crossings.times),
        "integration_success": crossings.integration_success,
        "integration_message": crossings.integration_message,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if args.workers < 1:
        raise SystemExit("--workers must be positive")

    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.atlas-transient-manifest.v1":
        raise SystemExit("unsupported atlas transient manifest")
    source_bytes = args.source_result.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_result"]["sha256"]:
        raise SystemExit("source result hash does not match manifest")
    source_result = json.loads(source_bytes)
    if source_result.get("experiment_id") != manifest["source_result"]["experiment_id"]:
        raise SystemExit("source experiment does not match manifest")
    source_rows = {row["point_index"]: row for row in source_result["rows"]}
    for case in manifest["cases"]:
        source_row = source_rows.get(case["point_index"])
        if source_row is None:
            raise SystemExit(f"case {case['id']} is absent from source result")
        for key in ("a", "b", "c"):
            if float(source_row[key]) != float(case[key]):
                raise SystemExit(f"case {case['id']} {key} differs from source result")

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("atlas transient qualification requires clean source")

    tasks = [
        (case, initial_state, float(transient))
        for case in manifest["cases"]
        for initial_state in case["initial_states"]
        for transient in manifest["transient_checkpoints"]
    ]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        values = list(
            executor.map(
                lambda task: evaluate_checkpoint(*task, manifest),
                tasks,
            )
        )
    lookup = {
        (case["id"], tuple(map(float, initial_state)), transient): value
        for (case, initial_state, transient), value in zip(tasks, values, strict=True)
    }
    cases = []
    for case in manifest["cases"]:
        initial_results = []
        for initial_state_value in case["initial_states"]:
            initial_state = tuple(map(float, initial_state_value))
            timeline = [
                lookup[(case["id"], initial_state, float(transient))]
                for transient in manifest["transient_checkpoints"]
            ]
            initial_results.append(
                {
                    "initial_state": list(initial_state),
                    "timeline": timeline,
                    "label_changed": len(
                        {(item["label"], item["fundamental_period"]) for item in timeline}
                    )
                    > 1,
                }
            )
        cases.append(
            {
                "id": case["id"],
                "point_index": case["point_index"],
                "parameters": {key: float(case[key]) for key in ("a", "b", "c")},
                "initial_conditions": initial_results,
                "final_outcome": final_outcome(initial_results),
            }
        )
    receipt = {
        "schema": "butterfly.atlas-transient-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source_result_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "case_count": len(cases),
        "checkpoint_run_count": len(tasks),
        "cases": cases,
        "outcome_counts": {
            status: sum(case["final_outcome"]["status"] == status for case in cases)
            for status in sorted({case["final_outcome"]["status"] for case in cases})
        },
        "all_integrations_succeeded": all(
            item["integration_success"]
            for case in cases
            for initial in case["initial_conditions"]
            for item in initial["timeline"]
        ),
        "interpretation_limit": (
            "Distinct finite checkpoints do not prove persistent multistability; "
            "common periodic capture rejects it for the sampled initial states."
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {
                "output": str(args.output),
                "outcome_counts": receipt["outcome_counts"],
                "all_integrations_succeeded": receipt["all_integrations_succeeded"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["all_integrations_succeeded"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
