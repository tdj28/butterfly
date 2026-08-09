#!/usr/bin/env python3
"""Blindly classify the ten approximate parameter landmarks in Jones Figure 6."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import json
import os
import platform
from pathlib import Path
import time

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    closest_recurrence_candidate,
    collect_crossings,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-figure6-landmark-classification-manifest.v1"


def load_inputs(manifest_path: Path) -> tuple[dict, bytes, dict]:
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unsupported Jones Figure 6 landmark manifest")
    transcription_path = Path(manifest["source"]["transcription_path"])
    transcription_bytes = transcription_path.read_bytes()
    if sha256_bytes(transcription_bytes) != manifest["source"]["transcription_sha256"]:
        raise ValueError("source transcription hash does not match manifest")
    transcription = json.loads(transcription_bytes)
    return manifest, manifest_bytes, transcription


def _row_key(row: dict) -> tuple[int, int, str, str]:
    return (
        int(row["landmark_index"]),
        int(row["initial_state_index"]),
        str(row["profile"]),
        str(row["solver"]),
    )


def _signature(row: dict) -> tuple[str, int | None]:
    recurrence = row["recurrence"]
    return str(recurrence["label"]), recurrence["fundamental_period"]


def summarize_rows(rows: list[dict], manifest: dict) -> dict:
    acceptance = manifest["acceptance"]
    by_key = {_row_key(row): row for row in rows}
    landmark_indices = sorted({int(row["landmark_index"]) for row in rows})
    initial_indices = range(len(manifest["initial_states"]))
    minimum_crossings = int(acceptance["minimum_crossings"])
    all_integrations_successful = all(
        bool(row["integration_success"]) and int(row["crossing_count"]) >= minimum_crossings
        for row in rows
    )

    qualified_solver_checks = []
    profile_checks = []
    classifications = []
    for landmark_index in landmark_indices:
        initial_signatures = []
        for initial_index in initial_indices:
            qualified_dop = by_key[(landmark_index, initial_index, "qualified", "dop853")]
            qualified_radau = by_key[(landmark_index, initial_index, "qualified", "radau")]
            early_dop = by_key[(landmark_index, initial_index, "early", "dop853")]
            solver_agreement = _signature(qualified_dop) == _signature(qualified_radau)
            profile_agreement = _signature(early_dop) == _signature(qualified_dop)
            qualified_solver_checks.append(
                {
                    "landmark_index": landmark_index,
                    "initial_state_index": initial_index,
                    "passed": solver_agreement,
                    "dop853": _signature(qualified_dop),
                    "radau": _signature(qualified_radau),
                }
            )
            profile_checks.append(
                {
                    "landmark_index": landmark_index,
                    "initial_state_index": initial_index,
                    "passed": profile_agreement,
                    "early": _signature(early_dop),
                    "qualified": _signature(qualified_dop),
                }
            )
            initial_signatures.append(_signature(qualified_dop))

        if len(set(initial_signatures)) == 1:
            label, period = initial_signatures[0]
            case_label = label
            case_period = period
        else:
            case_label = "initial-condition-dependent"
            case_period = None
        classifications.append(
            {
                "landmark_index": landmark_index,
                "label": case_label,
                "fundamental_period": case_period,
                "initial_signatures": initial_signatures,
            }
        )

    qualified_solver_agreement = all(check["passed"] for check in qualified_solver_checks)
    dop853_profile_agreement = all(check["passed"] for check in profile_checks)
    passed = bool(
        len(landmark_indices) == int(acceptance["required_landmark_count"])
        and (
            all_integrations_successful
            or not acceptance["require_all_integrations_successful"]
        )
        and (
            qualified_solver_agreement
            or not acceptance["require_qualified_solver_agreement"]
        )
        and (
            dop853_profile_agreement
            or not acceptance["require_dop853_profile_agreement"]
        )
    )
    return {
        "passed": passed,
        "all_integrations_successful": all_integrations_successful,
        "qualified_solver_agreement": qualified_solver_agreement,
        "dop853_profile_agreement": dop853_profile_agreement,
        "qualified_solver_checks": qualified_solver_checks,
        "profile_checks": profile_checks,
        "classifications": classifications,
        "resolved_periodic_count": sum(
            row["label"] == "periodic" for row in classifications
        ),
        "initial_condition_dependent_count": sum(
            row["label"] == "initial-condition-dependent" for row in classifications
        ),
    }


def evaluate_task(task: tuple, manifest: dict) -> dict:
    landmark_index, landmark, initial_index, initial_state, profile, solver_name = task
    parameters = RosslerParameters(
        a=float(landmark["a"]), b=float(landmark["b"]), c=float(landmark["c"])
    )
    solver = SolverConfig(**manifest["solvers"][solver_name])
    started = time.perf_counter()
    crossings = collect_crossings(
        parameters,
        initial_state,
        legacy_rossler_section(parameters),
        transient=float(profile["transient"]),
        observation_horizon=float(profile["observation_horizon"]),
        max_crossings=int(profile["max_crossings"]),
        config=solver,
    )
    recurrence = classify_fundamental_period(
        crossings.states,
        **manifest["recurrence"],
    )
    candidate = closest_recurrence_candidate(
        crossings.states,
        max_period=int(manifest["recurrence"]["max_period"]),
        required_repeats=int(manifest["recurrence"]["required_repeats"]),
        atol=float(manifest["recurrence"]["atol"]),
        rtol=float(manifest["recurrence"]["rtol"]),
    )
    row = {
        "landmark_index": int(landmark_index),
        "parameters": {key: float(landmark[key]) for key in ("a", "b", "c")},
        "initial_state_index": int(initial_index),
        "initial_state": list(map(float, initial_state)),
        "profile": profile["id"],
        "solver": solver_name,
        "solver_config": manifest["solvers"][solver_name],
        "crossing_count": int(len(crossings.times)),
        "integration_success": bool(crossings.integration_success),
        "integration_message": crossings.integration_message,
        "recurrence": asdict(recurrence),
        "closest_candidate": asdict(candidate) if candidate is not None else None,
        "tail_state_minimum": (
            np.min(crossings.states, axis=0).tolist() if len(crossings.states) else None
        ),
        "tail_state_maximum": (
            np.max(crossings.states, axis=0).tolist() if len(crossings.states) else None
        ),
        "elapsed_seconds": time.perf_counter() - started,
    }
    print(
        json.dumps(
            {
                "landmark_index": row["landmark_index"],
                "initial_state_index": row["initial_state_index"],
                "profile": row["profile"],
                "solver": row["solver"],
                "crossings": row["crossing_count"],
                "label": recurrence.label.value,
                "period": recurrence.fundamental_period,
                "candidate_period": candidate.period if candidate else None,
                "candidate_ratio": candidate.normalized_error if candidate else None,
                "elapsed_seconds": row["elapsed_seconds"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest, manifest_bytes, transcription = load_inputs(args.manifest)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    landmarks = transcription["figure6"]["parameter_landmarks"]
    if len(landmarks) != manifest["acceptance"]["required_landmark_count"]:
        raise SystemExit("unexpected source landmark count")
    tasks = []
    for landmark_index, landmark in enumerate(landmarks):
        for initial_index, initial_state in enumerate(manifest["initial_states"]):
            for profile in manifest["profiles"]:
                for solver_name in profile["solvers"]:
                    tasks.append(
                        (
                            landmark_index,
                            landmark,
                            initial_index,
                            initial_state,
                            profile,
                            solver_name,
                        )
                    )
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=int(manifest["execution"]["workers"])) as pool:
        rows = list(pool.map(lambda task: evaluate_task(task, manifest), tasks))
    rows.sort(key=_row_key)
    summary = summarize_rows(rows, manifest)
    receipt = {
        "schema": "butterfly.jones-figure6-landmark-classification-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "workers": int(manifest["execution"]["workers"]),
            "cpu_count": os.cpu_count(),
        },
        "rows": rows,
        "summary": summary,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": summary["passed"],
        "scientific_scope": manifest["source"]["claim_scope"],
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {
                "experiment_id": receipt["experiment_id"],
                "row_count": len(rows),
                "summary": summary,
                "elapsed_seconds": receipt["elapsed_seconds"],
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
