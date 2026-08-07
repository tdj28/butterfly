#!/usr/bin/env python3
"""Measure scale-dependent basin uncertainty with the qualified GPU crossing path."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import platform
import time

import numpy as np
import scipy
import torch
import triton

from butterfly import classify_fundamental_period, fit_uncertainty_exponent
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from gpu_crossing_qualify import integrate_gpu_crossings


def paired_states(
    plane: dict,
    *,
    epsilon: float,
    pairs: int,
    seed: int,
) -> np.ndarray:
    """Generate deterministic, exactly epsilon-separated pairs inside the plane."""

    x_min, x_max = map(float, plane["x"])
    y_min, y_max = map(float, plane["y"])
    z = float(plane["z"])
    half = 0.5 * epsilon
    if x_max - x_min <= epsilon or y_max - y_min <= epsilon:
        raise ValueError("epsilon must be smaller than both plane dimensions")
    rng = np.random.default_rng(seed)
    centers = np.column_stack(
        (
            rng.uniform(x_min + half, x_max - half, pairs),
            rng.uniform(y_min + half, y_max - half, pairs),
        )
    )
    angles = rng.uniform(0.0, 2.0 * np.pi, pairs)
    offsets = half * np.column_stack((np.cos(angles), np.sin(angles)))
    states = np.empty((2 * pairs, 3), dtype=np.float64)
    states[0::2, :2] = centers - offsets
    states[1::2, :2] = centers + offsets
    states[:, 2] = z
    return states


def classify_pairs(crossings: list[np.ndarray], classifier: dict) -> np.ndarray:
    periods = np.full(len(crossings), -1, dtype=np.int16)
    for index, states in enumerate(crossings):
        classification = classify_fundamental_period(
            states,
            max_period=int(classifier["max_period"]),
            required_repeats=int(classifier["required_repeats"]),
            atol=float(classifier["atol"]),
            rtol=float(classifier["rtol"]),
        )
        if classification.fundamental_period is not None:
            periods[index] = classification.fundamental_period
    return periods.reshape(-1, 2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.basin-uncertainty-manifest.v1":
        raise SystemExit("unsupported basin-uncertainty manifest")
    if len(args.source_commit) != 40 or any(
        character not in "0123456789abcdef" for character in args.source_commit.lower()
    ):
        raise SystemExit("--source-commit must be a full hexadecimal Git commit")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("declared source commit differs from the checked-out commit")
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available")

    parameters_config = manifest["parameters"]
    parameter_row = np.asarray(
        [parameters_config["a"], parameters_config["b"], parameters_config["c"]],
        dtype=np.float64,
    )
    sampling = manifest["sampling"]
    integration = manifest["integration"]
    classifier = manifest["classifier"]
    target_periods = np.asarray(manifest["target_periods"], dtype=np.int16)
    if len(target_periods) != 2 or len(np.unique(target_periods)) != 2:
        raise SystemExit("exactly two distinct target periods are required")
    pairs = int(sampling["pairs_per_seed_and_scale"])
    rows = []
    started = time.perf_counter()
    for epsilon_index, epsilon_value in enumerate(sampling["epsilons"]):
        epsilon = float(epsilon_value)
        for seed_value in sampling["seeds"]:
            seed = int(seed_value)
            states = paired_states(
                manifest["plane"], epsilon=epsilon, pairs=pairs, seed=seed
            )
            parameters = np.tile(parameter_row, (len(states), 1))
            input_hash = hashlib.sha256(states.tobytes(order="C")).hexdigest()
            crossings, performance = integrate_gpu_crossings(
                parameters,
                states,
                transient=float(integration["transient"]),
                observation_horizon=float(integration["observation_horizon"]),
                dt=float(integration["dt"]),
                chunk_steps=int(integration["chunk_steps"]),
                max_crossings=int(integration["max_crossings"]),
                dtype=torch.float64,
            )
            period_pairs = classify_pairs(crossings, classifier)
            resolved = np.all(np.isin(period_pairs, target_periods), axis=1)
            uncertain = resolved & (period_pairs[:, 0] != period_pairs[:, 1])
            period_counts = Counter(map(int, period_pairs.ravel()))
            rows.append(
                {
                    "epsilon_index": epsilon_index,
                    "epsilon": epsilon,
                    "seed": seed,
                    "pairs": pairs,
                    "input_states_sha256": input_hash,
                    "resolved_pairs": int(np.sum(resolved)),
                    "unresolved_pairs": int(np.sum(~resolved)),
                    "uncertain_pairs": int(np.sum(uncertain)),
                    "uncertain_fraction_among_resolved": (
                        float(np.mean(uncertain[resolved])) if np.any(resolved) else None
                    ),
                    "same_period_pairs": {
                        str(int(period)): int(
                            np.sum(
                                resolved
                                & (period_pairs[:, 0] == period)
                                & (period_pairs[:, 1] == period)
                            )
                        )
                        for period in target_periods
                    },
                    "state_period_counts": {
                        str(period): period_counts.get(period, 0)
                        for period in sorted(period_counts)
                    },
                    "performance": performance,
                }
            )

    epsilons = np.asarray(sampling["epsilons"], dtype=float)
    resolved_counts = np.asarray(
        [
            sum(row["resolved_pairs"] for row in rows if row["epsilon_index"] == index)
            for index in range(len(epsilons))
        ],
        dtype=np.int64,
    )
    uncertain_counts = np.asarray(
        [
            sum(row["uncertain_pairs"] for row in rows if row["epsilon_index"] == index)
            for index in range(len(epsilons))
        ],
        dtype=np.int64,
    )
    analysis = fit_uncertainty_exponent(
        epsilons,
        uncertain_counts,
        resolved_counts,
        bootstrap_samples=int(manifest["analysis"]["bootstrap_samples"]),
        bootstrap_seed=int(manifest["analysis"]["bootstrap_seed"]),
    )
    analysis["resolved_counts"] = resolved_counts.tolist()
    analysis["uncertain_counts"] = uncertain_counts.tolist()
    total_pairs_per_scale = pairs * len(sampling["seeds"])
    resolved_fractions = resolved_counts / total_pairs_per_scale
    passed = bool(
        np.all(resolved_fractions >= float(manifest["acceptance"]["minimum_resolved_fraction"]))
    )
    properties = torch.cuda.get_device_properties(0)
    receipt = {
        "schema": "butterfly.basin-uncertainty-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "passed": passed,
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source": {
            "commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "parameters": parameters_config,
        "plane": manifest["plane"],
        "target_periods": target_periods.tolist(),
        "rows": rows,
        "analysis": analysis,
        "resolved_fractions": resolved_fractions.tolist(),
        "elapsed_seconds": time.perf_counter() - started,
        "environment": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "triton": triton.__version__,
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_bytes": properties.total_memory,
            "gpu_compute_capability": [properties.major, properties.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "interpretation_gate": (
            "The exponent is descriptive unless the fit is stable under added scales, "
            "regions, directions, seeds, and integration horizons."
        ),
    }
    output_bytes = canonical_json(receipt)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": passed,
                "alpha": analysis["alpha"],
                "alpha_interval": analysis["alpha_bootstrap_95_interval"],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
