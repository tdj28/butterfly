#!/usr/bin/env python3
"""Audit burn-in, basin, topology, and Lyapunov identity at one path cell."""
from __future__ import annotations

import argparse
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    LyapunovConfig,
    OrbitLabel,
    PeriodClassification,
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    classify_with_lyapunov,
    collect_crossings,
    infer_return_map_branches_robust,
    largest_lyapunov_two_trajectory,
    lyapunov_block_estimates,
    lyapunov_spectrum,
    scrambled_sobol_section_states,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _initial_states(manifest, section):
    states = {}
    for declaration in manifest["initial_conditions"]:
        if declaration["kind"] == "explicit":
            states[declaration["id"]] = np.asarray(declaration["state"], dtype=float)
        elif declaration["kind"] == "sobol-section":
            samples = scrambled_sobol_section_states(
                section,
                first_coordinate_range=tuple(declaration["y_range"]),
                second_coordinate_range=tuple(declaration["z_range"]),
                sample_power=int(declaration["sample_power"]),
                scramble_seed=int(declaration["scramble_seed"]),
            )
            for index, state in enumerate(samples):
                states[f"{declaration['id']}-{index}"] = state
        else:
            raise ValueError(f"unsupported initial-condition kind: {declaration['kind']}")
    return states


def _common_branch_count(rows, coordinates, allowed_counts):
    counts = []
    for row in rows:
        for coordinate in coordinates:
            robust = row["coordinates"][coordinate["name"]]["robust_oracle"]
            if not robust["resolved"] or robust["branch_count"] is None:
                return None
            counts.append(int(robust["branch_count"]))
    unique = set(counts)
    if len(unique) != 1:
        return None
    count = unique.pop()
    return count if count in allowed_counts else None


def _critical_convergence(rows, coordinates, branch_count):
    output = {}
    for coordinate in coordinates:
        name = coordinate["name"]
        coordinate_rows = [row["coordinates"][name] for row in rows]
        domain_range = max(row["source_maximum"] for row in coordinate_rows) - min(
            row["source_minimum"] for row in coordinate_rows
        )
        intervals = []
        spans = []
        for index in range(branch_count - 1):
            lower = min(
                row["robust_oracle"]["critical_point_intervals"][index][0]
                for row in coordinate_rows
            )
            upper = max(
                row["robust_oracle"]["critical_point_intervals"][index][1]
                for row in coordinate_rows
            )
            intervals.append((lower, upper))
            spans.append((upper - lower) / max(domain_range, np.finfo(float).eps))
        output[name] = {
            "critical_point_intervals": intervals,
            "normalized_critical_point_spans": spans,
            "maximum_normalized_critical_point_span": max(spans, default=0.0),
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.invariant-identity-audit-manifest.v1":
        raise SystemExit("unsupported invariant-identity audit manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    parameters = RosslerParameters(**manifest["parameters"])
    section = barrio_rossler_section(parameters)
    states = _initial_states(manifest, section)
    solver = SolverConfig(**manifest["solver"])
    crossing = manifest["crossings"]
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    rows = []
    for dataset in manifest["datasets"]:
        initial = states[dataset["initial_state_id"]]
        crossings = collect_crossings(
            parameters,
            initial,
            section,
            transient=float(dataset["transient"]),
            observation_horizon=float(crossing["observation_horizon"]),
            max_crossings=int(crossing["max_crossings"]),
            config=solver,
        )
        recurrence = classify_fundamental_period(
            crossings.states, **manifest["recurrence"]
        )
        coordinates = {}
        for coordinate in manifest["coordinates"]:
            values = crossings.states[:, int(coordinate["axis"])]
            pair_count = max(0, len(values) - 1)
            if pair_count >= int(acceptance["minimum_return_pairs"]):
                robust = asdict(
                    infer_return_map_branches_robust(
                        values[:-1],
                        values[1:],
                        variants=manifest["oracle_variants"],
                        common_options=manifest["oracle_common"],
                        minimum_variant_consensus=float(
                            acceptance["minimum_oracle_variant_consensus"]
                        ),
                        maximum_normalized_critical_point_span=float(
                            acceptance[
                                "maximum_within_dataset_normalized_critical_span"
                            ]
                        ),
                    )
                )
            else:
                robust = {
                    "resolved": False,
                    "branch_count": None,
                    "critical_point_intervals": (),
                    "reason": "insufficient return pairs",
                }
            coordinates[coordinate["name"]] = {
                "pair_count": pair_count,
                "source_minimum": float(np.min(values[:-1])) if pair_count else None,
                "source_maximum": float(np.max(values[:-1])) if pair_count else None,
                "robust_oracle": robust,
            }
        row = {
            "id": dataset["id"],
            "initial_state_id": dataset["initial_state_id"],
            "initial_state": initial.tolist(),
            "transient": float(dataset["transient"]),
            "integration_success": crossings.integration_success,
            "crossing_count": len(crossings.states),
            "recurrence": asdict(recurrence),
            "coordinates": coordinates,
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "dataset": row["id"],
                    "transient": row["transient"],
                    "recurrence": recurrence.label.value,
                    "branch_counts": {
                        name: value["robust_oracle"].get("branch_count")
                        for name, value in coordinates.items()
                    },
                },
                sort_keys=True,
            ),
            flush=True,
        )

    observed = _common_branch_count(
        rows,
        manifest["coordinates"],
        {int(value) for value in acceptance["allowed_branch_counts"]},
    )
    critical = (
        _critical_convergence(rows, manifest["coordinates"], observed)
        if observed is not None
        else {
            coordinate["name"]: {
                "critical_point_intervals": [],
                "normalized_critical_point_spans": [],
                "maximum_normalized_critical_point_span": 1e300,
            }
            for coordinate in manifest["coordinates"]
        }
    )

    lyapunov_rows = []
    lyapunov_config_value = manifest["lyapunov"]
    lyapunov_config = LyapunovConfig(
        transient=float(lyapunov_config_value["transient"]),
        duration=float(lyapunov_config_value["duration"]),
        qr_interval=float(lyapunov_config_value["qr_interval"]),
        solver=solver,
    )
    dataset_by_id = {row["id"]: row for row in rows}
    for case in lyapunov_config_value["cases"]:
        initial = states[case["initial_state_id"]]
        spectrum = lyapunov_spectrum(parameters, initial, config=lyapunov_config)
        blocks = lyapunov_block_estimates(
            spectrum, blocks=int(lyapunov_config_value["blocks"])
        )
        standard_error = np.std(blocks, axis=0, ddof=1) / np.sqrt(len(blocks))
        recurrence = dataset_by_id[case["recurrence_dataset_id"]]["recurrence"]
        recurrence_object = PeriodClassification(**recurrence)
        classification = classify_with_lyapunov(
            recurrence_object, spectrum.exponents, standard_error
        )
        independent = largest_lyapunov_two_trajectory(
            parameters,
            initial,
            config=lyapunov_config,
            perturbation=float(lyapunov_config_value["two_trajectory_perturbation"]),
        )
        row = {
            "id": case["id"],
            "initial_state_id": case["initial_state_id"],
            "classification": asdict(classification),
            "variational_success": spectrum.success,
            "exponents": spectrum.exponents.tolist(),
            "block_standard_errors": standard_error.tolist(),
            "trace_identity_error": spectrum.trace_identity_error,
            "independent_success": independent.success,
            "independent_largest_exponent": independent.exponent,
            "largest_exponent_difference": abs(
                independent.exponent - float(spectrum.exponents[0])
            ),
        }
        row["passed"] = bool(
            spectrum.success
            and independent.success
            and classification.label == OrbitLabel.CHAOTIC
            and spectrum.trace_identity_error
            <= float(acceptance["maximum_trace_identity_error"])
            and row["largest_exponent_difference"]
            <= float(acceptance["maximum_largest_exponent_difference"])
        )
        lyapunov_rows.append(row)
        print(
            json.dumps(
                {
                    "lyapunov_case": row["id"],
                    "classification": classification.label.value,
                    "exponents": row["exponents"],
                    "independent_largest": row["independent_largest_exponent"],
                    "passed": row["passed"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    topology_passed = bool(
        observed is not None
        and all(
            row["integration_success"]
            and row["crossing_count"] >= int(acceptance["minimum_crossings"])
            and row["recurrence"]["label"] != OrbitLabel.PERIODIC.value
            for row in rows
        )
        and all(
            coordinate["maximum_normalized_critical_point_span"]
            <= float(acceptance["maximum_across_dataset_normalized_critical_span"])
            for coordinate in critical.values()
        )
    )
    output = {
        "schema": "butterfly.invariant-identity-audit.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": asdict(parameters),
        "elapsed_seconds": time.perf_counter() - started,
        "datasets": rows,
        "observed_branch_count": observed,
        "critical_point_convergence": critical,
        "topology_passed": topology_passed,
        "lyapunov": lyapunov_rows,
        "passed": bool(topology_passed and all(row["passed"] for row in lyapunov_rows)),
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "observed_branch_count": observed,
                "topology_passed": topology_passed,
                "passed": output["passed"],
                "elapsed_seconds": output["elapsed_seconds"],
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
