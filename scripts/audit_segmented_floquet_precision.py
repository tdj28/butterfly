#!/usr/bin/env python3
"""Audit solver and multiplier-representation stability near a segmented flip."""
from __future__ import annotations

import argparse
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import correct_fixed_b, integrate_segment


def block_and_product_floquet(nodes, duration, parameters, solver, cyclic_shifts):
    segment_count = len(nodes)
    segment_duration = duration / segment_count
    transitions = [
        integrate_segment(node, segment_duration, parameters, solver)[1]
        for node in nodes
    ]
    block_map = np.zeros((3 * segment_count, 3 * segment_count))
    for index, transition in enumerate(transitions):
        target = (index + 1) % segment_count
        block_map[3 * target : 3 * target + 3, 3 * index : 3 * index + 3] = transition
    eigenvalues = np.linalg.eigvals(block_map)
    order = np.argsort(np.abs(eigenvalues))
    ordered = eigenvalues[order]
    clusters = []
    for index in range(3):
        values = ordered[index * segment_count : (index + 1) * segment_count]
        radii = np.abs(values)
        powered = values**segment_count
        clusters.append(
            {
                "root_radius_median": float(np.median(radii)),
                "root_radius_minimum": float(np.min(radii)),
                "root_radius_maximum": float(np.max(radii)),
                "floquet_modulus": float(np.median(radii) ** segment_count),
                "floquet_multiplier": {
                    "real": float(np.median(powered.real)),
                    "imag": float(np.median(powered.imag)),
                },
                "powered_root_maximum_deviation": float(
                    np.max(np.abs(powered - np.median(powered)))
                ),
            }
        )
    neutral_index = int(
        np.argmin([abs(item["floquet_modulus"] - 1.0) for item in clusters])
    )
    dominant_index = max(
        (
            (index, item["floquet_modulus"])
            for index, item in enumerate(clusters)
            if index != neutral_index
        ),
        key=lambda item: item[1],
    )[0]
    block = {
        "clusters": clusters,
        "neutral_cluster_index": neutral_index,
        "dominant_nontrivial_cluster_index": dominant_index,
        "dominant_nontrivial_multiplier": clusters[dominant_index]["floquet_multiplier"],
    }

    products = []
    for shift in cyclic_shifts:
        shifted = transitions[shift:] + transitions[:shift]
        monodromy = np.eye(3)
        for transition in shifted:
            monodromy = transition @ monodromy
        values = np.linalg.eigvals(monodromy)
        neutral = int(np.argmin(np.abs(values - 1.0)))
        nontrivial = [value for index, value in enumerate(values) if index != neutral]
        dominant = max(nontrivial, key=abs)
        products.append(
            {
                "cyclic_shift": shift,
                "eigenvalues": [
                    {"real": float(value.real), "imag": float(value.imag)}
                    for value in values
                ],
                "dominant_nontrivial_multiplier": {
                    "real": float(dominant.real),
                    "imag": float(dominant.imag),
                },
            }
        )
    return {"block": block, "direct_products": products}


def evaluate_task(task):
    profile = task["profile"]
    b = float(task["b"])
    a = float(task["a"])
    c = float(task["c"])
    solver = SolverConfig(**profile["solver"])
    nodes = np.asarray(task["seed_nodes"], dtype=float)
    segment_count = len(nodes)
    variables = np.r_[nodes.ravel(), task["seed_period_time"]]
    phase_reference = np.asarray(task["phase_reference"], dtype=float)
    phase_parameters = RosslerParameters(a=a, b=b, c=c)
    phase = rossler_rhs(0.0, phase_reference, phase_parameters)
    phase /= np.linalg.norm(phase)
    corrected, status = correct_fixed_b(
        variables,
        b,
        segment_count=segment_count,
        a=a,
        c=c,
        phase=phase,
        phase_reference=phase_reference,
        solver=solver,
        tolerance=profile["corrector"]["tolerance"],
        max_evaluations=profile["corrector"]["max_evaluations"],
    )
    corrected_nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
    duration = float(corrected[3 * segment_count])
    parameters = RosslerParameters(a=a, b=b, c=c)
    floquet = block_and_product_floquet(
        corrected_nodes,
        duration,
        parameters,
        solver,
        task["cyclic_shifts"],
    )
    return {
        "profile": profile["name"],
        "b": b,
        "status": status,
        "period_time": duration,
        "half_node_rms": float(
            np.sqrt(
                np.mean(
                    (corrected_nodes[: segment_count // 2]
                    - corrected_nodes[segment_count // 2 :]) ** 2
                )
            )
        ),
        "floquet": floquet,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--refinement", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.segmented-floquet-precision-audit-manifest.v1":
        raise SystemExit("unsupported segmented Floquet audit manifest")
    scan_bytes = args.scan.read_bytes()
    refinement_bytes = args.refinement.read_bytes()
    if sha256_bytes(scan_bytes) != manifest["scan_receipt_sha256"]:
        raise SystemExit("scan receipt hash mismatch")
    if sha256_bytes(refinement_bytes) != manifest["refinement_receipt_sha256"]:
        raise SystemExit("refinement receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    scan = json.loads(scan_bytes)
    refinement = json.loads(refinement_bytes)
    if scan.get("schema") != manifest["scan_schema"]:
        raise SystemExit("bound scan schema mismatch")
    if refinement.get("schema") != manifest["refinement_schema"]:
        raise SystemExit("bound refinement schema mismatch")
    if scan["segment_count"] != manifest["segment_count"]:
        raise SystemExit("scan segment count mismatch")
    scan_rows = {float(row["b"]): row for row in scan["rows"]}
    center = refinement["best_evaluation"]
    seed_rows = {
        float(manifest["b_values"][0]): scan_rows[float(manifest["b_values"][0])],
        float(manifest["b_values"][1]): center,
        float(manifest["b_values"][2]): scan_rows[float(manifest["b_values"][2])],
    }
    phase_reference = center["nodes"][0]
    tasks = []
    for profile in manifest["profiles"]:
        for b in manifest["b_values"]:
            seed = seed_rows[float(b)]
            tasks.append(
                {
                    "profile": profile,
                    "b": b,
                    "a": manifest["fixed_a"],
                    "c": manifest["fixed_c"],
                    "seed_nodes": seed["nodes"],
                    "seed_period_time": seed["period_time"],
                    "phase_reference": phase_reference,
                    "cyclic_shifts": manifest["cyclic_shifts"],
                }
            )
    with ProcessPoolExecutor(max_workers=manifest["workers"]) as executor:
        rows = list(executor.map(evaluate_task, tasks))
    rows.sort(key=lambda row: (row["profile"], row["b"]))

    profile_summaries = []
    for profile in manifest["profiles"]:
        selected = [row for row in rows if row["profile"] == profile["name"]]
        selected.sort(key=lambda row: row["b"])
        block_values = [
            row["floquet"]["block"]["dominant_nontrivial_multiplier"]["real"]
            for row in selected
        ]
        endpoint_bracket = (block_values[0] + 1.0) * (block_values[-1] + 1.0) <= 0.0
        product_differences = []
        product_spreads = []
        for row in selected:
            block_value = row["floquet"]["block"]["dominant_nontrivial_multiplier"]["real"]
            product_values = [
                item["dominant_nontrivial_multiplier"]["real"]
                for item in row["floquet"]["direct_products"]
            ]
            product_differences.append(abs(block_value - float(np.median(product_values))))
            product_spreads.append(max(product_values) - min(product_values))
        profile_summaries.append(
            {
                "profile": profile["name"],
                "endpoint_signed_bracket": endpoint_bracket,
                "block_multipliers": block_values,
                "maximum_block_product_difference": max(product_differences),
                "maximum_cyclic_product_spread": max(product_spreads),
            }
        )
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.segmented-floquet-precision-audit.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "segment_count": manifest["segment_count"],
        "b_values": manifest["b_values"],
        "rows": rows,
        "profile_summaries": profile_summaries,
    }
    output["passed"] = bool(
        all(
            row["status"]["success"]
            and row["status"]["matching_residual"] <= acceptance["max_matching_residual"]
            and row["half_node_rms"] >= acceptance["minimum_half_node_rms"]
            for row in rows
        )
        and all(summary["endpoint_signed_bracket"] for summary in profile_summaries)
        and all(
            summary["maximum_block_product_difference"]
            <= acceptance["max_block_product_difference"]
            and summary["maximum_cyclic_product_spread"]
            <= acceptance["max_cyclic_product_spread"]
            for summary in profile_summaries
        )
    )
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
