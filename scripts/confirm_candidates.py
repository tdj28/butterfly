#!/usr/bin/env python3
"""Confirm a hash-bound candidate set with spectra and multiple initial states."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

import numpy as np
import scipy

from butterfly import (
    DynamicsClassification,
    LyapunovConfig,
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    classify_with_lyapunov,
    closest_recurrence_candidate,
    collect_crossings,
    combine_initial_conditions,
    legacy_rossler_section,
    lyapunov_block_estimates,
    lyapunov_spectrum,
    select_low_score_with_neighbors,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from butterfly.tiles import verify_completed_aggregate, verify_completed_tile


def load_inputs(manifest_path: Path, source_result_path: Path) -> tuple[dict, dict, bytes]:
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.candidate-confirmation-manifest.v1":
        raise ValueError("unsupported candidate confirmation manifest")
    source_bytes = source_result_path.read_bytes()
    source_hash = sha256_bytes(source_bytes)
    if source_hash != manifest["source_result"]["sha256"]:
        raise ValueError("candidate source result hash does not match manifest")
    result = json.loads(source_bytes)
    if result.get("experiment_id") != manifest["source_result"]["experiment_id"]:
        raise ValueError("candidate source experiment does not match manifest")
    return manifest, result, raw_manifest


def source_state(require_clean: bool) -> dict[str, Any]:
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None:
        raise RuntimeError("candidate confirmation requires a Git commit")
    if require_clean and source["dirty"]:
        raise RuntimeError("candidate confirmation requires a clean source tree")
    return source


def partition(total: int, index: int, count: int) -> tuple[int, ...]:
    if count < 1 or index < 0 or index >= count:
        raise ValueError("invalid tile index or count")
    quotient, remainder = divmod(total, count)
    start = index * quotient + min(index, remainder)
    length = quotient + (1 if index < remainder else 0)
    return tuple(range(start, start + length))


def tile_directory(output_root: Path, index: int, count: int) -> Path:
    return output_root / f"tile-{index:05d}-of-{count:05d}"


def confirmation_plan_hash(raw_manifest: bytes) -> str:
    return sha256_bytes(raw_manifest)


def target_classification(
    classifications: list[DynamicsClassification],
) -> DynamicsClassification:
    combined = combine_initial_conditions(classifications)
    if any(item.label == OrbitLabel.NUMERICAL_FAILURE for item in classifications):
        return DynamicsClassification(
            OrbitLabel.NUMERICAL_FAILURE,
            None,
            0.0,
            "at least one initial-condition computation failed",
            tuple(item.reason for item in classifications),
        )
    if any(item.label == OrbitLabel.UNRESOLVED for item in classifications):
        return DynamicsClassification(
            OrbitLabel.UNRESOLVED,
            None,
            0.0,
            "at least one initial condition remained unresolved",
            tuple(item.reason for item in classifications),
        )
    return combined


def evaluate_target(
    source_row: dict[str, Any],
    *,
    manifest: dict[str, Any],
    parent_core_indices: tuple[int, ...],
    core_indices: set[int],
) -> dict[str, Any]:
    parameters = RosslerParameters(
        a=float(source_row["a"]),
        b=float(source_row["b"]),
        c=float(source_row["c"]),
    )
    solver = SolverConfig(**manifest["solver"])
    crossing_config = manifest["crossings"]
    lyapunov_config = manifest["lyapunov"]
    initial_results = []
    classifications = []
    for initial_state_value in manifest["initial_states"]:
        initial_state = tuple(map(float, initial_state_value))
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
        candidate = closest_recurrence_candidate(
            crossings.states,
            max_period=int(crossing_config["max_period"]),
            required_repeats=int(crossing_config["required_repeats"]),
            atol=float(crossing_config["atol"]),
            rtol=float(crossing_config["rtol"]),
        )
        spectrum = lyapunov_spectrum(
            parameters,
            initial_state,
            config=LyapunovConfig(
                transient=float(lyapunov_config["transient"]),
                duration=float(lyapunov_config["duration"]),
                qr_interval=float(lyapunov_config["qr_interval"]),
                solver=solver,
            ),
        )
        standard_error = None
        if crossings.integration_success and spectrum.success:
            blocks = lyapunov_block_estimates(
                spectrum, blocks=int(lyapunov_config["blocks"])
            )
            standard_error_array = np.std(blocks, axis=0, ddof=1) / math.sqrt(
                len(blocks)
            )
            standard_error = standard_error_array.tolist()
            classification = classify_with_lyapunov(
                recurrence, spectrum.exponents, standard_error_array
            )
        else:
            classification = DynamicsClassification(
                OrbitLabel.NUMERICAL_FAILURE,
                None,
                0.0,
                crossings.integration_message if not crossings.integration_success else spectrum.message,
                ("confirmation-integration-failure",),
            )
        classifications.append(classification)
        initial_results.append(
            {
                "initial_state": list(initial_state),
                "label": classification.label.value,
                "fundamental_period": classification.fundamental_period,
                "confidence": classification.confidence,
                "reason": classification.reason,
                "evidence": list(classification.evidence),
                "crossing_count": len(crossings.times),
                "crossing_integration_success": crossings.integration_success,
                "recurrence_label": recurrence.label.value,
                "recurrence_error": recurrence.recurrence_error,
                "recurrence_tolerance": recurrence.recurrence_tolerance,
                "candidate_period": candidate.period if candidate else None,
                "candidate_normalized_error": (
                    candidate.normalized_error if candidate else None
                ),
                "lyapunov_success": spectrum.success,
                "lyapunov_exponents": spectrum.exponents.tolist(),
                "lyapunov_block_standard_error": standard_error,
                "trace_identity_error": spectrum.trace_identity_error,
            }
        )
    combined = target_classification(classifications)
    return {
        "point_index": source_row["point_index"],
        "a": parameters.a,
        "b": parameters.b,
        "c": parameters.c,
        "selected_as_core": source_row["point_index"] in core_indices,
        "parent_core_indices": list(parent_core_indices),
        "discovery_candidate_period": source_row["candidate_period"],
        "discovery_normalized_error": source_row["candidate_normalized_error"],
        "label": combined.label.value,
        "fundamental_period": combined.fundamental_period,
        "confidence": combined.confidence,
        "reason": combined.reason,
        "evidence": list(combined.evidence),
        "initial_conditions": initial_results,
    }


def execute_tile(args: argparse.Namespace, *, require_clean: bool) -> dict[str, Any]:
    manifest, source_result, raw_manifest = load_inputs(args.manifest, args.source_result)
    source = source_state(require_clean)
    selection_config = manifest["selection"]
    selection = select_low_score_with_neighbors(
        source_result,
        fraction=float(selection_config["finite_score_fraction"]),
        neighbor_radius=int(selection_config["neighbor_radius"]),
    )
    positions = partition(len(selection.selected_indices), args.tile_index, args.tile_count)
    target_indices = tuple(selection.selected_indices[position] for position in positions)
    plan_hash = confirmation_plan_hash(raw_manifest)
    tile_id = sha256_bytes(
        canonical_json(
            {
                "schema": "butterfly.candidate-confirmation-tile-plan.v1",
                "plan_hash": plan_hash,
                "source_commit": source["commit"],
                "tile_index": args.tile_index,
                "tile_count": args.tile_count,
                "target_indices": list(target_indices),
            }
        )
    )
    directory = tile_directory(args.output_root, args.tile_index, args.tile_count)
    if (directory / "complete.json").exists():
        if not args.resume:
            raise FileExistsError(f"completed tile already exists: {directory}")
        return verify_completed_tile(directory, expected_tile_id=tile_id)
    if directory.exists() and any(directory.iterdir()) and not args.resume:
        raise FileExistsError(f"incomplete tile directory exists: {directory}")

    by_index = {row["point_index"]: row for row in source_result["rows"]}
    started = time.perf_counter()
    rows = [
        evaluate_target(
            by_index[index],
            manifest=manifest,
            parent_core_indices=selection.parent_core_indices[index],
            core_indices=set(selection.core_indices),
        )
        for index in target_indices
    ]
    result = {
        "schema": "butterfly.candidate-confirmation-tile-result.v1",
        "experiment_id": manifest["experiment_id"],
        "plan_hash": plan_hash,
        "tile_id": tile_id,
        "tile_index": args.tile_index,
        "tile_count": args.tile_count,
        "target_indices": list(target_indices),
        "row_count": len(rows),
        "rows": rows,
    }
    result_bytes = canonical_json(result)
    result_hash = sha256_bytes(result_bytes)
    receipt = {
        "schema": "butterfly.candidate-confirmation-tile-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "plan_hash": plan_hash,
        "tile_id": tile_id,
        "tile_index": args.tile_index,
        "tile_count": args.tile_count,
        "target_indices": list(target_indices),
        "row_count": len(rows),
        "result_sha256": result_hash,
        "elapsed_seconds": time.perf_counter() - started,
        "source": source,
        "source_result_sha256": manifest["source_result"]["sha256"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "label_counts": {
            label: sum(row["label"] == label for row in rows)
            for label in sorted({row["label"] for row in rows})
        },
    }
    receipt_bytes = canonical_json(receipt)
    completion = {
        "schema": "butterfly.scan-tile-completion.v1",
        "tile_id": tile_id,
        "result_sha256": result_hash,
        "receipt_sha256": sha256_bytes(receipt_bytes),
    }
    atomic_write(directory / "result.json", result_bytes)
    atomic_write(directory / "receipt.json", receipt_bytes)
    atomic_write(directory / "complete.json", canonical_json(completion))
    return receipt


def aggregate(args: argparse.Namespace, *, require_clean: bool) -> dict[str, Any]:
    manifest, source_result, raw_manifest = load_inputs(args.manifest, args.source_result)
    source = source_state(require_clean)
    selection_config = manifest["selection"]
    selection = select_low_score_with_neighbors(
        source_result,
        fraction=float(selection_config["finite_score_fraction"]),
        neighbor_radius=int(selection_config["neighbor_radius"]),
    )
    rows = []
    tile_receipts = []
    for tile_index in range(args.tile_count):
        directory = tile_directory(args.output_root, tile_index, args.tile_count)
        receipt = verify_completed_tile(directory)
        tile_receipts.append(receipt)
        rows.extend(json.loads((directory / "result.json").read_bytes())["rows"])
    rows.sort(key=lambda row: row["point_index"])
    if [row["point_index"] for row in rows] != list(selection.selected_indices):
        raise ValueError("confirmation tiles do not exactly cover selected targets")
    result = {
        "schema": "butterfly.candidate-confirmation-result.v1",
        "experiment_id": manifest["experiment_id"],
        "plan_hash": confirmation_plan_hash(raw_manifest),
        "source_result_sha256": manifest["source_result"]["sha256"],
        "core_indices": list(selection.core_indices),
        "selected_indices": list(selection.selected_indices),
        "row_count": len(rows),
        "rows": rows,
    }
    result_bytes = canonical_json(result)
    result_hash = sha256_bytes(result_bytes)
    receipt = {
        "schema": "butterfly.candidate-confirmation-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "plan_hash": confirmation_plan_hash(raw_manifest),
        "source_result_sha256": manifest["source_result"]["sha256"],
        "core_count": len(selection.core_indices),
        "selected_count": len(selection.selected_indices),
        "tile_count": args.tile_count,
        "tile_ids": [item["tile_id"] for item in tile_receipts],
        "tile_result_sha256": [item["result_sha256"] for item in tile_receipts],
        "row_count": len(rows),
        "result_sha256": result_hash,
        "source": source,
        "label_counts": {
            label: sum(row["label"] == label for row in rows)
            for label in sorted({row["label"] for row in rows})
        },
    }
    directory = args.output_root / "aggregate"
    completion_path = directory / "complete.json"
    if completion_path.exists():
        existing = verify_completed_aggregate(directory)
        if existing.get("result_sha256") != result_hash:
            raise ValueError("completed confirmation aggregate has a different result")
        return existing
    receipt_bytes = canonical_json(receipt)
    completion = {
        "schema": "butterfly.tiled-scan-completion.v1",
        "result_sha256": result_hash,
        "receipt_sha256": sha256_bytes(receipt_bytes),
    }
    atomic_write(directory / "result.json", result_bytes)
    atomic_write(directory / "receipt.json", receipt_bytes)
    atomic_write(completion_path, canonical_json(completion))
    return receipt


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--manifest", type=Path, required=True)
    root.add_argument("--source-result", type=Path, required=True)
    root.add_argument("--output-root", type=Path, required=True)
    root.add_argument("--tile-count", type=int, required=True)
    root.add_argument("--tile-index", type=int)
    root.add_argument("--workers", type=int, default=1)
    root.add_argument("--resume", action="store_true")
    root.add_argument("--allow-dirty", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    if args.tile_count < 1 or args.workers < 1:
        raise SystemExit("tile count and workers must be positive")
    require_clean = not args.allow_dirty
    if args.tile_index is not None:
        if args.workers != 1:
            raise SystemExit("--workers applies only when executing all tiles")
        receipt = execute_tile(args, require_clean=require_clean)
    else:
        if args.workers == 1:
            for tile_index in range(args.tile_count):
                args.tile_index = tile_index
                execute_tile(args, require_clean=require_clean)
        else:
            def run_child(tile_index: int) -> None:
                command = [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--manifest",
                    str(args.manifest),
                    "--source-result",
                    str(args.source_result),
                    "--output-root",
                    str(args.output_root),
                    "--tile-count",
                    str(args.tile_count),
                    "--tile-index",
                    str(tile_index),
                ]
                if args.resume:
                    command.append("--resume")
                if args.allow_dirty:
                    command.append("--allow-dirty")
                completed = subprocess.run(
                    command, capture_output=True, text=True, check=False
                )
                if completed.returncode != 0:
                    raise RuntimeError(
                        f"confirmation tile {tile_index} failed: "
                        f"{completed.stderr.strip()}"
                    )

            with ThreadPoolExecutor(max_workers=args.workers) as executor:
                futures = [
                    executor.submit(run_child, tile_index)
                    for tile_index in range(args.tile_count)
                ]
                for future in futures:
                    future.result()
        args.tile_index = None
        receipt = aggregate(args, require_clean=require_clean)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
