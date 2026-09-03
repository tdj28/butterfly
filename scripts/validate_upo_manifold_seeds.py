#!/usr/bin/env python3
"""Validate section-tangent unstable Floquet seeds for the local UPO census."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    collect_crossings,
    flow_monodromy,
    next_section_return,
    project_floquet_direction_to_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _receipt_sources(manifest):
    receipts = {}
    hashes = {}
    for source in manifest["source_receipts"]:
        path = Path(source["path"])
        payload = path.read_bytes()
        digest = sha256_bytes(payload)
        if digest != source["sha256"]:
            raise SystemExit(f"source receipt hash mismatch: {source['id']}")
        receipts[source["id"]] = json.loads(payload)
        hashes[source["id"]] = digest
    return receipts, hashes


def _source_row(receipt, branch_id, target_a, tolerance):
    branch = next(row for row in receipt["branches"] if row["id"] == branch_id)
    row = min(branch["rows"], key=lambda value: abs(value["a"] - target_a))
    if abs(float(row["a"]) - target_a) > tolerance:
        raise ValueError(f"branch {branch_id} does not contain target a={target_a}")
    if not row["audit"]["passed"]:
        raise ValueError(f"branch {branch_id} target row is not orbit-qualified")
    return row


def _advance_returns(parameters, section, state, count, solver, maximum_flight_time):
    current = np.asarray(state, dtype=float)
    flight_times = []
    for _ in range(count):
        result = next_section_return(
            parameters,
            current,
            section,
            config=solver,
            maximum_flight_time=maximum_flight_time,
        )
        if not result.success:
            return current, flight_times, False, result.message
        current = result.state
        flight_times.append(result.flight_time)
    return current, flight_times, True, "all exact section returns located"


def _complex_row(value):
    return {
        "real": float(value.real),
        "imag": float(value.imag),
        "modulus": float(abs(value)),
    }


def _validate_instance(family, case, receipts, manifest, solver):
    target_a = float(case["a"])
    source = receipts[family["source_receipt_id"]]
    row = _source_row(
        source,
        family["source_branch_id"],
        target_a,
        float(manifest["source_parameter_tolerance"]),
    )
    parameters = RosslerParameters(a=target_a, b=float(row["b"]), c=float(row["c"]))
    section = barrio_rossler_section(parameters)
    period = float(row["period_time"])
    lag = int(family["fundamental_lag"])
    crossing_search = manifest["crossing_search"]
    crossings = collect_crossings(
        parameters,
        np.asarray(row["initial_state"], dtype=float),
        section,
        transient=period * float(crossing_search["transient_period_fraction"]),
        observation_horizon=period
        * float(crossing_search["observation_period_fraction"]),
        max_crossings=lag + 2,
        config=solver,
    )
    if not crossings.integration_success or not len(crossings.states):
        return {
            "case_id": case["id"],
            "family_id": family["id"],
            "fundamental_lag": lag,
            "passed": False,
            "failure": "no qualified base section crossing",
        }
    base = np.asarray(crossings.states[0], dtype=float)
    monodromy = flow_monodromy(parameters, base, period, config=solver)
    eigenvalues, eigenvectors = np.linalg.eig(monodromy.monodromy)
    unstable_index = int(np.argmax(np.abs(eigenvalues)))
    unstable_multiplier = complex(eigenvalues[unstable_index])
    raw_direction = eigenvectors[:, unstable_index]
    acceptance = manifest["acceptance"]
    real_direction = bool(
        abs(unstable_multiplier.imag)
        <= float(acceptance["maximum_unstable_multiplier_imaginary_part"])
        and np.linalg.norm(raw_direction.imag)
        <= float(acceptance["maximum_unstable_direction_imaginary_norm"])
    )
    flow = rossler_rhs(0.0, base, parameters)
    scales = np.asarray(manifest["coordinate_scales"], dtype=float)
    direction = project_floquet_direction_to_section(
        raw_direction.real,
        flow,
        section.normal,
        coordinate_scales=scales,
    )
    normal = np.asarray(section.normal, dtype=float)
    tangent_residual = float(abs(np.dot(normal, direction)))
    scaled_direction = direction / scales
    scaled_direction_norm_error = float(abs(np.linalg.norm(scaled_direction) - 1.0))
    section_speed = float(np.dot(normal, flow))

    reference_final, reference_times, reference_success, reference_message = (
        _advance_returns(
            parameters,
            section,
            base,
            lag,
            solver,
            float(crossing_search["maximum_flight_time"]),
        )
    )
    section_axes = np.flatnonzero(np.abs(normal) < 0.5)
    if len(section_axes) != 2:
        raise ValueError("manifold validation currently requires an axis-aligned plane")
    base_return_closure = float(
        np.linalg.norm(
            (reference_final[section_axes] - base[section_axes]) / scales[section_axes]
        )
    )
    direction_in_section = scaled_direction[section_axes]
    direction_in_section /= np.linalg.norm(direction_in_section)
    perturbations = []
    sign_pass_counts = {-1: 0, 1: 0}
    for epsilon in manifest["perturbation_sizes"]:
        for sign in (-1, 1):
            amplitude = sign * float(epsilon)
            seed = base + amplitude * direction
            seed -= normal * (section.value(seed) / float(np.dot(normal, normal)))
            final, flight_times, success, message = _advance_returns(
                parameters,
                section,
                seed,
                lag,
                solver,
                float(crossing_search["maximum_flight_time"]),
            )
            if success and reference_success:
                delta = (
                    final[section_axes] - reference_final[section_axes]
                ) / scales[section_axes]
                observed_multiplier = float(
                    np.dot(delta, direction_in_section) / amplitude
                )
                predicted = float(unstable_multiplier.real)
                relative_error = float(
                    abs(observed_multiplier - predicted) / abs(predicted)
                )
                transverse = delta - observed_multiplier * amplitude * direction_in_section
                transverse_ratio = float(
                    np.linalg.norm(transverse)
                    / max(abs(observed_multiplier * amplitude), np.finfo(float).tiny)
                )
                passed = bool(
                    relative_error
                    <= float(acceptance["maximum_relative_multiplier_error"])
                    and transverse_ratio
                    <= float(acceptance["maximum_transverse_residual_ratio"])
                )
            else:
                observed_multiplier = None
                relative_error = None
                transverse_ratio = None
                passed = False
            if passed:
                sign_pass_counts[sign] += 1
            perturbations.append(
                {
                    "epsilon": float(epsilon),
                    "sign": sign,
                    "return_success": success,
                    "message": message,
                    "total_flight_time": float(sum(flight_times)),
                    "observed_signed_multiplier": observed_multiplier,
                    "relative_multiplier_error": relative_error,
                    "transverse_residual_ratio": transverse_ratio,
                    "passed": passed,
                }
            )
    checks = {
        "base_crossing_integration": crossings.integration_success,
        "monodromy_integration": monodromy.success,
        "real_unstable_direction": real_direction,
        "transverse_instability": abs(unstable_multiplier)
        >= 1.0 + float(acceptance["minimum_instability_margin"]),
        "positive_section_speed": section_speed
        >= float(acceptance["minimum_section_speed"]),
        "section_tangent_projection": tangent_residual
        <= float(acceptance["maximum_section_tangent_residual"]),
        "scaled_direction_normalization": scaled_direction_norm_error
        <= float(acceptance["maximum_scaled_direction_norm_error"]),
        "base_lag_return": reference_success
        and base_return_closure
        <= float(acceptance["maximum_base_lag_return_scaled_closure"]),
        "negative_branch_linearization": sign_pass_counts[-1]
        >= int(acceptance["minimum_passing_sizes_per_sign"]),
        "positive_branch_linearization": sign_pass_counts[1]
        >= int(acceptance["minimum_passing_sizes_per_sign"]),
    }
    return {
        "case_id": case["id"],
        "family_id": family["id"],
        "source_receipt_id": family["source_receipt_id"],
        "source_branch_id": family["source_branch_id"],
        "parameters": {"a": target_a, "b": parameters.b, "c": parameters.c},
        "fundamental_lag": lag,
        "period_time": period,
        "base_section_state": base.tolist(),
        "section_speed": section_speed,
        "unstable_multiplier": _complex_row(unstable_multiplier),
        "section_unstable_direction": direction.tolist(),
        "section_tangent_residual": tangent_residual,
        "scaled_direction_norm_error": scaled_direction_norm_error,
        "base_lag_return_scaled_closure": base_return_closure,
        "base_lag_return_total_flight_time": float(sum(reference_times)),
        "base_lag_return_message": reference_message,
        "perturbations": perturbations,
        "passing_sizes_by_sign": {
            "negative": sign_pass_counts[-1],
            "positive": sign_pass_counts[1],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.upo-manifold-seed-manifest.v1":
        raise SystemExit("unsupported UPO manifold-seed manifest")
    receipts, receipt_hashes = _receipt_sources(manifest)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    solver = SolverConfig(**manifest["reference_solver"])
    started = time.perf_counter()
    instances = []
    for case in manifest["cases"]:
        for family in manifest["families"]:
            row = _validate_instance(family, case, receipts, manifest, solver)
            instances.append(row)
            print(
                json.dumps(
                    {
                        "case": case["id"],
                        "family": family["id"],
                        "lag": family["fundamental_lag"],
                        "passed": row["passed"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    receipt = {
        "schema": "butterfly.upo-manifold-seed-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": receipt_hashes,
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "instances": instances,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(instances and all(row["passed"] for row in instances)),
        "scientific_scope": (
            "local unstable-manifold seed validation, not a global connection event"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {key: value for key, value in receipt.items() if key != "instances"},
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
