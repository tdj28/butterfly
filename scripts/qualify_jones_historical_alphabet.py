#!/usr/bin/env python3
"""Qualify a source-derived Jones alphabet without fitting Figure 6 words."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    collect_crossings,
    legacy_rossler_section,
    rossler_equilibria,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-historical-alphabet-manifest.v1"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one evidence file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nested_value(payload: dict, path: str):
    """Read a required dot-delimited field from a JSON object."""

    value = payload
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            raise ValueError(f"missing evidence field: {path}")
        value = value[key]
    return value


def classify_branch(value: float, partition: dict) -> int | None:
    """Classify a scalar return into a frozen branch, censoring boundaries."""

    lower, upper = (float(item) for item in partition["domain"])
    scalar = float(value)
    if not np.isfinite(scalar) or scalar < lower or scalar > upper:
        return None
    intervals = tuple(
        (float(interval[0]), float(interval[1]))
        for interval in partition["critical_intervals"]
    )
    if any(left <= scalar <= right for left, right in intervals):
        return None
    return sum(scalar > right for _left, right in intervals)


def classify_series(values: np.ndarray, partition: dict) -> np.ndarray:
    """Vectorize :func:`classify_branch`, using -1 for censored points."""

    return np.asarray(
        [
            -1 if (branch := classify_branch(value, partition)) is None else branch
            for value in np.asarray(values, dtype=float)
        ],
        dtype=np.int64,
    )


def analyze_segment(
    states: np.ndarray,
    equilibrium: np.ndarray,
    *,
    axis: int,
    partition: dict,
    pair_start: int,
    pair_count: int,
    acceptance: dict,
) -> tuple[dict, np.ndarray, np.ndarray]:
    """Measure branch transitions and physical target proximity."""

    stop = pair_start + pair_count
    if pair_start < 0 or pair_count < 1 or len(states) < stop + 1:
        raise ValueError("insufficient crossing states for frozen segment")
    source = classify_series(states[pair_start:stop, axis], partition)
    target = classify_series(states[pair_start + 1 : stop + 1, axis], partition)
    valid = (source >= 0) & (target >= 0)
    distances = np.linalg.norm(
        states[pair_start + 1 : stop + 1] - equilibrium,
        axis=1,
    )
    transition_counts = np.zeros((3, 3), dtype=np.int64)
    for source_branch, target_branch in zip(source[valid], target[valid], strict=True):
        transition_counts[source_branch, target_branch] += 1

    target_statistics = []
    for branch in range(3):
        selected = distances[valid & (target == branch)]
        if len(selected):
            quantiles = np.quantile(selected, (0.0, 0.1, 0.5, 0.9, 1.0))
            row = {
                "branch": f"B{branch}",
                "count": int(len(selected)),
                "distance_quantiles": [float(value) for value in quantiles],
            }
        else:
            row = {
                "branch": f"B{branch}",
                "count": 0,
                "distance_quantiles": None,
            }
        target_statistics.append(row)

    counts = [row["count"] for row in target_statistics]
    medians = [
        None if row["distance_quantiles"] is None else row["distance_quantiles"][2]
        for row in target_statistics
    ]
    distance_range = max(float(np.ptp(distances[valid])), np.finfo(float).eps)
    inner_median_gap = (
        min(float(medians[0]), float(medians[1])) - float(medians[2])
        if all(value is not None for value in medians)
        else float("-inf")
    )
    inner_normalized_median_gap = inner_median_gap / distance_range
    inner_maximum = target_statistics[2]["distance_quantiles"][4] if counts[2] else None
    next_minimum = (
        min(
            target_statistics[branch]["distance_quantiles"][0]
            for branch in (0, 1)
            if counts[branch]
        )
        if counts[0] and counts[1]
        else None
    )
    strict_inner_separation = bool(
        inner_maximum is not None
        and next_minimum is not None
        and inner_maximum < next_minimum
    )
    third_total = int(np.sum(transition_counts[0]))
    third_to_inner = int(transition_counts[0, 2])
    third_self_fraction = (
        float(transition_counts[0, 0] / third_total) if third_total else 1.0
    )
    passed = bool(
        int(np.sum(valid)) >= int(acceptance["minimum_resolved_pairs"])
        and min(counts, default=0) >= int(acceptance["minimum_target_branch_count"])
        and medians[2] is not None
        and int(np.argmin(np.asarray(medians, dtype=float))) == 2
        and inner_normalized_median_gap
        >= float(acceptance["minimum_inner_normalized_median_gap"])
        and (
            strict_inner_separation
            if acceptance["require_strict_inner_distance_separation"]
            else True
        )
        and third_to_inner >= int(acceptance["minimum_third_to_inner_transitions"])
        and third_self_fraction
        <= float(acceptance["maximum_third_self_transition_fraction"])
    )
    summary = {
        "resolved_pair_count": int(np.sum(valid)),
        "resolved_pair_fraction": float(np.mean(valid)),
        "transition_counts": transition_counts.tolist(),
        "target_distance_statistics": target_statistics,
        "distance_median_order_nearest_first": [
            f"B{index}" for index in np.argsort(np.asarray(medians, dtype=float))
        ],
        "inner_normalized_median_gap": float(inner_normalized_median_gap),
        "strict_inner_distance_separation": strict_inner_separation,
        "inner_distance_margin": (
            None
            if inner_maximum is None or next_minimum is None
            else float(next_minimum - inner_maximum)
        ),
        "third_to_inner_transitions": third_to_inner,
        "third_self_transition_fraction": third_self_fraction,
        "passed": passed,
    }
    return summary, source, target


def validate_evidence(manifest: dict) -> dict:
    """Hash and minimally validate every frozen parent/source record."""

    results = {}
    for record in manifest["evidence"]:
        path = Path(record["path"])
        actual = sha256_file(path)
        if actual != record["sha256"]:
            raise ValueError(f"evidence hash mismatch: {path}")
        payload = json.loads(path.read_text())
        pass_path = record.get("pass_path", "passed")
        if record.get("require_passed") and not nested_value(payload, pass_path):
            raise ValueError(f"parent evidence did not pass: {path}")
        results[str(path)] = {"sha256": actual, "schema": payload.get("schema")}

    semantic_path = Path(manifest["source_semantics"]["path"])
    semantic_hash = sha256_file(semantic_path)
    if semantic_hash != manifest["source_semantics"]["sha256"]:
        raise ValueError("source-semantics hash mismatch")
    semantics = json.loads(semantic_path.read_text())
    predictions = semantics["operational_predictions"]
    if predictions["critical_mapping"] != manifest["historical_mapping"]["critical"]:
        raise ValueError("critical mapping differs from frozen source semantics")
    if predictions["branch_mapping"] != manifest["historical_mapping"]["branch"]:
        raise ValueError("branch mapping differs from frozen source semantics")
    if semantics["blindness"]["figure6_words_used_to_choose_mapping"]:
        raise ValueError("source mapping is not blind to Figure 6 words")
    results[str(semantic_path)] = {
        "sha256": semantic_hash,
        "schema": semantics.get("schema"),
    }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported historical-alphabet manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    started = time.perf_counter()
    evidence = validate_evidence(manifest)
    parameters = RosslerParameters(**manifest["parameters"])
    base_section = legacy_rossler_section(parameters)
    section = PoincareSection(
        normal=base_section.normal,
        offset=base_section.offset,
        direction=int(manifest["section"]["direction"]),
        gate_axis=base_section.gate_axis,
        gate_upper=base_section.gate_upper,
        name="legacy-small-equilibrium-half-plane:negative",
    )
    equilibrium = rossler_equilibria(parameters)[0]
    integration = manifest["integration"]
    rows = []
    agreement_rows = []
    integrations_passed = True
    for profile in manifest["solver_profiles"]:
        crossings = collect_crossings(
            parameters,
            profile["initial_state"],
            section,
            transient=float(integration["transient"]),
            observation_horizon=float(integration["observation_horizon"]),
            max_crossings=int(integration["max_crossings"]),
            config=SolverConfig(**profile["solver"]),
        )
        integration_passed = bool(
            crossings.integration_success
            and len(crossings.times) >= int(integration["minimum_total_crossings"])
        )
        integrations_passed = integrations_passed and integration_passed
        print(
            json.dumps(
                {
                    "profile": profile["name"],
                    "crossing_count": len(crossings.times),
                    "integration_passed": integration_passed,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        for segment in manifest["segments"]:
            classifications = {}
            for coordinate in manifest["coordinates"]:
                name = coordinate["name"]
                summary, source_branches, target_branches = analyze_segment(
                    crossings.states,
                    equilibrium,
                    axis=int(coordinate["axis"]),
                    partition=coordinate["partition"],
                    pair_start=int(segment["pair_start"]),
                    pair_count=int(segment["pair_count"]),
                    acceptance=manifest["acceptance"],
                )
                row = {
                    "profile": profile["name"],
                    "crossing_count": len(crossings.times),
                    "segment": segment["name"],
                    "coordinate": name,
                    **summary,
                }
                rows.append(row)
                classifications[name] = (source_branches, target_branches)
                print(json.dumps(row, sort_keys=True), flush=True)

            x_source, x_target = classifications["x"]
            z_source, z_target = classifications["z"]
            jointly_resolved = (
                (x_source >= 0)
                & (x_target >= 0)
                & (z_source >= 0)
                & (z_target >= 0)
            )
            agreement = (
                (x_source == z_source) & (x_target == z_target) & jointly_resolved
            )
            denominator = int(np.sum(jointly_resolved))
            fraction = float(np.sum(agreement) / denominator) if denominator else 0.0
            agreement_row = {
                "profile": profile["name"],
                "segment": segment["name"],
                "jointly_resolved_pairs": denominator,
                "source_and_target_branch_agreement_fraction": fraction,
                "passed": bool(
                    denominator >= int(manifest["acceptance"]["minimum_resolved_pairs"])
                    and fraction
                    >= float(
                        manifest["acceptance"][
                            "minimum_cross_coordinate_pair_agreement"
                        ]
                    )
                ),
            }
            agreement_rows.append(agreement_row)
            print(json.dumps(agreement_row, sort_keys=True), flush=True)

    passed = bool(
        integrations_passed
        and all(row["passed"] for row in rows)
        and all(row["passed"] for row in agreement_rows)
    )
    output = {
        "schema": "butterfly.jones-historical-alphabet.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "evidence": evidence,
        "historical_mapping": manifest["historical_mapping"],
        "rows": rows,
        "cross_coordinate_agreement": agreement_rows,
        "acceptance": manifest["acceptance"],
        "claim_scope": manifest["claim_scope"],
        "passed": passed,
        "elapsed_seconds": time.perf_counter() - started,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "historical_mapping": manifest["historical_mapping"],
                "passed": passed,
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
