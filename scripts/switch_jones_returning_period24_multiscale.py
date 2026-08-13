#!/usr/bin/env python3
"""Probe period-24 branch switching at the exact EXP-232 period-12 flip."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.qualify_jones_period12_children import _closure_at_fraction
from scripts.switch_jones_period6_flip_curve import _switch_event


SCHEMA = "butterfly.jones-returning-period24-multiscale-switch-manifest.v1"


def source_event(receipt, solver_name):
    """Convert one qualified EXP-232 child root to a generic flip event."""

    root = receipt["root_results"][solver_name]
    child = root["root_full"]["child"]
    return {
        "a": float(root["root"]["a"]),
        "b": float(root["root_full"]["b"]),
        "c": float(root["root"]["c"]),
        "initial_state": child["initial_state"],
        "period_time": float(child["period_time"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-24 multiscale switch manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    receipt = json.loads(source_bytes)
    if not receipt.get("passed"):
        raise SystemExit("period-24 switching requires passed period-12 flip")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("period-24 switching requires clean source")

    event = source_event(receipt, manifest["source_solver"])
    solver = SolverConfig(**manifest["solver"])
    parameters = RosslerParameters(a=event["a"], b=event["b"], c=event["c"])
    acceptance = manifest["candidate_acceptance"]
    trials = []
    started = time.perf_counter()
    for step_length in manifest["step_lengths"]:
        trial_manifest = json.loads(json.dumps(manifest))
        trial_manifest["continuation"] = {
            **manifest["continuation"],
            "step_length": float(step_length),
        }
        switched = _switch_event(event, trial_manifest, solver)
        candidates = []
        for branch in switched["branches"]:
            for row in branch["rows"]:
                orbit = SimpleNamespace(
                    initial_state=np.asarray(row["initial_state"], dtype=float),
                    period_time=float(row["period_time"]),
                )
                half_period_closure = _closure_at_fraction(
                    RosslerParameters(a=row["a"], b=row["b"], c=row["c"]),
                    orbit,
                    0.5,
                    solver,
                )
                period_ratio = float(row["period_time"]) / float(event["period_time"])
                parameter_displacement = float(row["a"]) - float(event["a"])
                candidate = {
                    "step_length": float(step_length),
                    "direction": int(branch["direction"]),
                    **row,
                    "period_ratio_to_parent": period_ratio,
                    "half_period_closure": half_period_closure,
                    "parameter_displacement": parameter_displacement,
                }
                candidate["accepted"] = bool(
                    float(row["closure_error"])
                    <= float(acceptance["maximum_closure_error"])
                    and int(row["historical_phase_count"])
                    == int(acceptance["historical_child_phase_count"])
                    and int(row["barrio_phase_count"])
                    == int(acceptance["barrio_child_phase_count"])
                    and row["historical_integration_success"]
                    and row["barrio_integration_success"]
                    and abs(period_ratio - 2.0)
                    <= float(acceptance["maximum_period_ratio_error"])
                    and half_period_closure
                    >= float(acceptance["minimum_half_period_closure"])
                    and abs(parameter_displacement)
                    >= float(acceptance["minimum_parameter_displacement"])
                    and float(branch["endpoint_distance_from_doubled_primary"])
                    >= float(acceptance["minimum_primary_distance"])
                )
                candidates.append(candidate)
        trials.append(
            {
                "step_length": float(step_length),
                "shooting_singular_values": switched["shooting_singular_values"],
                "absolute_tangent_dot": switched["absolute_tangent_dot"],
                "primary_rows": switched["primary_rows"],
                "primary_correction_statuses": switched[
                    "primary_correction_statuses"
                ],
                "branches": [
                    {
                        "direction": branch["direction"],
                        "point_count": branch["point_count"],
                        "statuses": branch["statuses"],
                        "endpoint_distance_from_doubled_primary": branch[
                            "endpoint_distance_from_doubled_primary"
                        ],
                        "maximum_a_separation": branch["maximum_a_separation"],
                    }
                    for branch in switched["branches"]
                ],
                "candidates": candidates,
            }
        )

    candidates = [candidate for trial in trials for candidate in trial["candidates"]]
    accepted = [candidate for candidate in candidates if candidate["accepted"]]
    minimum_singular = min(
        float(trial["shooting_singular_values"][-1]) for trial in trials
    )
    maximum_tangent_dot = max(float(trial["absolute_tangent_dot"]) for trial in trials)
    passed = bool(
        minimum_singular <= float(acceptance["maximum_small_singular_value"])
        and maximum_tangent_dot <= float(acceptance["maximum_tangent_dot"])
        and len(accepted) >= int(acceptance["minimum_accepted_candidates"])
    )
    output = {
        "schema": "butterfly.jones-returning-period24-multiscale-switch-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "event": event,
        "trials": trials,
        "candidate_count": len(candidates),
        "accepted_candidates": accepted,
        "minimum_small_singular_value": minimum_singular,
        "maximum_tangent_dot": maximum_tangent_dot,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": passed,
                "candidate_count": len(candidates),
                "accepted_candidate_count": len(accepted),
                "minimum_small_singular_value": minimum_singular,
                "maximum_tangent_dot": maximum_tangent_dot,
                "accepted": [
                    {
                        "step_length": candidate["step_length"],
                        "direction": candidate["direction"],
                        "a": candidate["a"],
                        "multiplier_modulus": candidate["dominant_multiplier"][
                            "modulus"
                        ],
                        "half_period_closure": candidate["half_period_closure"],
                    }
                    for candidate in accepted
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
