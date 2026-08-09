#!/usr/bin/env python3
"""Qualify the GPU Barrio-section survivor map against the CPU reference."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    collect_crossings,
    correct_periodic_orbit,
    infer_return_map_branches_robust,
    legacy_rossler_section,
    sprinkler_survivors,
    survivor_return_pairs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.gpu_scan_jones_two_critical_residuals import (
    _initial_ensemble,
    _pairs,
    integrate_gpu,
)

try:  # pragma: no cover - CUDA worker only
    import torch
    import triton
except ImportError:  # pragma: no cover - helpers remain testable locally
    torch = None
    triton = None


SCHEMA = "butterfly.gpu-barrio-section-qualification-manifest.v1"


def normalized_critical_midpoints(partition: dict, domain) -> np.ndarray:
    """Return ordered critical midpoints normalized to one source domain."""

    lower, upper = map(float, domain)
    width = upper - lower
    intervals = np.asarray(partition["critical_point_intervals"], dtype=float)
    if width <= 0.0 or intervals.ndim != 2 or intervals.shape[1] != 2:
        raise ValueError("invalid critical intervals or source domain")
    return (np.mean(intervals, axis=1) - lower) / width


def _partition(source, target, manifest) -> dict:
    variants = tuple(
        {**manifest["oracle_common"], **variant["options"]}
        for variant in manifest["oracle_variants"]
    )
    robust = infer_return_map_branches_robust(
        source,
        target,
        variants=variants,
        minimum_variant_consensus=1.0,
        maximum_normalized_critical_point_span=float(
            manifest["acceptance"]["maximum_normalized_critical_span"]
        ),
    )
    return asdict(robust)


def _anchor_cycle(manifest: dict) -> dict:
    parameters = RosslerParameters(**manifest["anchor"]["parameters"])
    expected_historical_period = int(manifest["anchor"]["historical_period"])
    expected_barrio_count = int(manifest["anchor"]["barrio_phase_count"])
    solver = SolverConfig(**manifest["cpu_solver"])
    integration = manifest["anchor"]["integration"]
    crossings = collect_crossings(
        parameters,
        integration["initial_state"],
        legacy_rossler_section(parameters),
        transient=float(integration["transient"]),
        observation_horizon=float(integration["observation_horizon"]),
        max_crossings=int(integration["max_crossings"]),
        config=solver,
    )
    classification = classify_fundamental_period(
        crossings.states,
        max_period=32,
        required_repeats=8,
        atol=1e-6,
        rtol=1e-7,
    )
    if classification.fundamental_period != expected_historical_period:
        raise RuntimeError("anchor historical period mismatch")
    seed_index = -expected_historical_period - 1
    correction = correct_periodic_orbit(
        parameters,
        crossings.states[seed_index],
        float(crossings.times[-1] - crossings.times[seed_index]),
        config=solver,
        max_evaluations=int(manifest["anchor"]["corrector"]["maximum_evaluations"]),
        tolerance=float(manifest["anchor"]["corrector"]["tolerance"]),
    )
    barrio = collect_crossings(
        parameters,
        correction.initial_state,
        barrio_rossler_section(parameters),
        transient=0.0,
        observation_horizon=correction.period_time * (1.0 + 1e-7),
        max_crossings=expected_barrio_count + 4,
        config=solver,
    )
    keep = (barrio.times > correction.period_time * 1e-7) & (
        barrio.times <= correction.period_time * (1.0 + 1e-7)
    )
    states = barrio.states[keep]
    if not correction.success or len(states) != expected_barrio_count:
        raise RuntimeError("anchor correction or Barrio phase count failed")
    return {
        "parameters": manifest["anchor"]["parameters"],
        "section_states": states.tolist(),
        "correction": {
            "initial_state": correction.initial_state.tolist(),
            "period_time": correction.period_time,
            "closure_error": correction.closure_error,
            "phase_residual": correction.phase_residual,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported GPU Barrio qualification manifest")
    if len(args.source_commit) != 40 or any(
        character not in "0123456789abcdef" for character in args.source_commit.lower()
    ):
        raise SystemExit("a full source commit is required")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("source commit mismatch")
    for evidence in manifest.get("evidence", ()):
        raw = Path(evidence["path"]).read_bytes()
        if sha256_bytes(raw) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    if torch is None or triton is None or not torch.cuda.is_available():
        raise SystemExit("CUDA, PyTorch, and Triton are required")
    candidate = _anchor_cycle(manifest)
    parameters = RosslerParameters(**candidate["parameters"])
    section = barrio_rossler_section(parameters)
    initial = _initial_ensemble([candidate], manifest["ensemble"])[0]
    acceptance = manifest["acceptance"]
    profiles = []
    for profile in manifest["profiles"]:
        dt = float(profile["dt"])
        cpu = sprinkler_survivors(
            parameters,
            initial,
            section,
            candidate["section_states"],
            dt=dt,
            horizon=float(manifest["ensemble"]["horizon"]),
            capture_coordinate_axes=(1, 2),
            capture_coordinate_scales=tuple(manifest["capture"]["coordinate_scales"]),
            capture_radius=float(manifest["capture"]["radius"]),
            required_capture_crossings=int(manifest["capture"]["required_crossings"]),
            checkpoint_times=manifest["ensemble"]["checkpoint_times"],
            midpoint_window=tuple(manifest["ensemble"]["midpoint_window"]),
            escape_radius=float(manifest["ensemble"]["escape_radius"]),
        )
        gpu = integrate_gpu(
            [candidate],
            dt=dt,
            horizon=float(manifest["ensemble"]["horizon"]),
            checkpoints=manifest["ensemble"]["checkpoint_times"],
            midpoint=manifest["ensemble"]["midpoint_window"],
            ensemble=manifest["ensemble"],
            capture=manifest["capture"],
            gpu_options=manifest["gpu"],
            section_name="barrio_positive_x",
            section_code=1,
            target_cycle_state_count=8,
        )
        cpu_source, cpu_target = survivor_return_pairs(cpu, 2)
        gpu_source, gpu_target = _pairs(gpu["records"][0], axis=2)
        cpu_partition = _partition(cpu_source, cpu_target, manifest)
        gpu_partition = _partition(gpu_source, gpu_target, manifest)
        if cpu_partition.get("resolved") and gpu_partition.get("resolved"):
            cpu_domain = (float(np.min(cpu_source)), float(np.max(cpu_source)))
            gpu_domain = (float(np.min(gpu_source)), float(np.max(gpu_source)))
            critical_difference = float(
                np.max(
                    np.abs(
                        normalized_critical_midpoints(cpu_partition, cpu_domain)
                        - normalized_critical_midpoints(gpu_partition, gpu_domain)
                    )
                )
            )
        else:
            critical_difference = None
        initial_count = len(initial)
        survivor_difference = float(
            np.max(
                np.abs(cpu.survivor_counts - gpu["survivor_counts"][0])
                / initial_count
            )
        )
        checks = {
            "cpu_failures": not bool(np.any(cpu.failed)),
            "gpu_failures": int(gpu["failed_counts"][0]) == 0,
            "cpu_survivors": int(cpu.survivor_counts[-1])
            >= int(acceptance["minimum_final_survivors"]),
            "gpu_survivors": int(gpu["survivor_counts"][0, -1])
            >= int(acceptance["minimum_final_survivors"]),
            "cpu_pairs": len(cpu_source) >= int(acceptance["minimum_return_pairs"]),
            "gpu_pairs": len(gpu_source) >= int(acceptance["minimum_return_pairs"]),
            "cpu_three_branch": cpu_partition.get("resolved")
            and cpu_partition.get("branch_count") == 3,
            "gpu_three_branch": gpu_partition.get("resolved")
            and gpu_partition.get("branch_count") == 3,
            "survivor_parity": survivor_difference
            <= float(acceptance["maximum_survivor_fraction_difference"]),
            "critical_parity": critical_difference is not None
            and critical_difference
            <= float(acceptance["maximum_cpu_gpu_critical_midpoint_difference"]),
        }
        profiles.append(
            {
                "name": profile["name"],
                "dt": dt,
                "cpu": {
                    "survivor_counts": cpu.survivor_counts.tolist(),
                    "failed_count": int(np.count_nonzero(cpu.failed)),
                    "pair_count": len(cpu_source),
                    "partition": cpu_partition,
                },
                "gpu": {
                    "survivor_counts": gpu["survivor_counts"][0].tolist(),
                    "failed_count": int(gpu["failed_counts"][0]),
                    "pair_count": len(gpu_source),
                    "partition": gpu_partition,
                    "elapsed_seconds": gpu["elapsed_seconds"],
                    "state_steps_per_second": gpu["state_steps_per_second"],
                },
                "survivor_fraction_difference": survivor_difference,
                "maximum_normalized_critical_midpoint_difference": critical_difference,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
        print(
            json.dumps(
                {
                    "profile": profile["name"],
                    "passed": profiles[-1]["passed"],
                    "cpu_branch_count": cpu_partition.get("branch_count"),
                    "gpu_branch_count": gpu_partition.get("branch_count"),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    props = torch.cuda.get_device_properties(0)
    output = {
        "schema": "butterfly.gpu-barrio-section-qualification.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": {
            "declared_commit": args.source_commit,
            "observed_git_commit": observed_commit,
        },
        "anchor_cycle": candidate,
        "profiles": profiles,
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
            "gpu_memory_bytes": props.total_memory,
            "gpu_compute_capability": [props.major, props.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "passed": all(profile["passed"] for profile in profiles),
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": output["passed"],
            },
            sort_keys=True,
        )
    )
    return 0 if output["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
