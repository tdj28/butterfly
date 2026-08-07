#!/usr/bin/env python3
"""Compare segmented periodic orbits with continuous phase alignment."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def segmented_dense(nodes, duration, parameters, solver):
    segment_duration = duration / len(nodes)
    solutions = []
    endpoint_errors = []
    for index, node in enumerate(nodes):
        result = solve_ivp(
            lambda time, state: rossler_rhs(time, state, parameters),
            (0.0, segment_duration),
            node,
            method=solver.method,
            rtol=solver.rtol,
            atol=solver.atol,
            max_step=solver.max_step,
            dense_output=True,
        )
        if not result.success:
            raise RuntimeError(result.message)
        solutions.append(result.sol)
        endpoint_errors.append(
            np.linalg.norm(result.y[:, -1] - nodes[(index + 1) % len(nodes)])
        )

    def evaluate(phases):
        normalized = np.mod(np.asarray(phases, dtype=float), 1.0)
        coordinates = normalized * len(nodes)
        indices = np.floor(coordinates).astype(int)
        local_times = (coordinates - indices) * segment_duration
        states = np.empty((3, normalized.size))
        for index in np.unique(indices):
            mask = indices == index
            states[:, mask] = solutions[index](local_times[mask])
        return states

    return evaluate, float(max(endpoint_errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.segmented-orbit-identity-manifest.v1":
        raise SystemExit("unsupported segmented identity manifest")
    qualification_bytes = args.qualification.read_bytes()
    if sha256_bytes(qualification_bytes) != manifest["qualification_receipt_sha256"]:
        raise SystemExit("qualification receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    qualification = json.loads(qualification_bytes)
    candidates = sorted(
        qualification["corrected_candidates"], key=lambda row: row["direction"]
    )
    if len(candidates) != 2 or {row["direction"] for row in candidates} != {-1, 1}:
        raise SystemExit("qualification must contain exactly two switch signs")
    parameters = RosslerParameters(
        a=manifest["fixed_a"], b=qualification["target_b"], c=manifest["fixed_c"]
    )
    solver = SolverConfig(**manifest["solver"])
    dense = []
    endpoint_errors = []
    for candidate in candidates:
        evaluate, endpoint_error = segmented_dense(
            np.asarray(candidate["nodes"]),
            candidate["period_time"],
            parameters,
            solver,
        )
        dense.append(evaluate)
        endpoint_errors.append(endpoint_error)
    phases = np.linspace(0.0, 1.0, manifest["phase_samples"], endpoint=False)
    left = dense[0](phases)

    def rms(shift):
        right = dense[1]((phases + shift) % 1.0)
        return float(np.sqrt(np.mean((left - right) ** 2)))

    shifts = np.linspace(0.0, 1.0, manifest["coarse_shifts"], endpoint=False)
    values = np.asarray([rms(shift) for shift in shifts])
    best = int(np.argmin(values))
    spacing = 1.0 / manifest["coarse_shifts"]
    refinement = minimize_scalar(
        lambda shift: rms(shift % 1.0),
        bounds=(float(shifts[best] - spacing), float(shifts[best] + spacing)),
        method="bounded",
        options={"xatol": manifest["shift_tolerance"]},
    )
    identity = {
        "rms": float(refinement.fun),
        "phase_shift": float(refinement.x % 1.0),
        "coarse_rms": float(values[best]),
        "coarse_phase_shift": float(shifts[best]),
    }
    acceptance = manifest["acceptance"]
    moduli = [
        row["floquet"]["dominant_nontrivial_modulus"] for row in candidates
    ]
    output = {
        "schema": "butterfly.segmented-orbit-identity.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "target_b": qualification["target_b"],
        "identity": identity,
        "maximum_segment_endpoint_error": max(endpoint_errors),
        "period_difference": abs(
            candidates[0]["period_time"] - candidates[1]["period_time"]
        ),
        "dominant_nontrivial_moduli": moduli,
        "block_validation_modulus_error": qualification["block_floquet_validation"][
            "absolute_modulus_error"
        ],
    }
    output["passed"] = bool(
        identity["rms"] <= acceptance["max_identity_rms"]
        and output["maximum_segment_endpoint_error"]
        <= acceptance["max_segment_endpoint_error"]
        and output["period_difference"] <= acceptance["max_period_difference"]
        and max(moduli) <= acceptance["maximum_stable_modulus"]
        and output["block_validation_modulus_error"]
        <= acceptance["max_validation_modulus_error"]
    )
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
