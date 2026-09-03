#!/usr/bin/env python3
"""Re-evaluate a near-threshold augmented flip under tighter solver steps."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from audit_segmented_floquet_precision import block_and_product_floquet
from butterfly import RosslerParameters, SolverConfig, augmented_flip_system, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from solve_analytic_augmented_flip import flip_spectrum_metrics


SCHEMA = "butterfly.jones-augmented-flip-precision-audit-manifest.v1"


def evaluate_family(event: dict, solver: SolverConfig, cyclic_shifts: list[int]) -> dict:
    nodes = np.asarray(event["nodes"], dtype=float)
    tangents = np.asarray(event["tangent_nodes"], dtype=float)
    count = int(event["segment_count"])
    parameters = RosslerParameters(
        a=float(event["corrected_a"]),
        b=float(event["fixed_b"]),
        c=float(event["fixed_c"]),
    )
    phase_reference = nodes[0].copy()
    phase = rossler_rhs(0.0, phase_reference, parameters)
    phase /= np.linalg.norm(phase)
    variables = np.r_[
        nodes.ravel(),
        float(event["period_time"]),
        float(event["corrected_a"]),
        tangents.ravel(),
    ]
    residual, _ = augmented_flip_system(
        variables,
        segment_count=count,
        a=None,
        c=float(event["fixed_c"]),
        phase=phase,
        phase_reference=phase_reference,
        solver=solver,
        continuation_parameter="a",
        fixed_b=float(event["fixed_b"]),
    )
    state_count = 3 * count
    floquet = block_and_product_floquet(
        nodes,
        float(event["period_time"]),
        parameters,
        solver,
        cyclic_shifts,
    )
    return {
        "residuals": {
            "orbit_matching": float(np.linalg.norm(residual[:state_count])),
            "phase": float(abs(residual[state_count])),
            "tangent_transport": float(
                np.linalg.norm(residual[state_count + 1 : -1])
            ),
            "normalization": float(abs(residual[-1])),
        },
        "flip_spectrum": flip_spectrum_metrics(floquet),
        "floquet": floquet,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported augmented-flip precision audit manifest")
    event_bytes = args.event.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    event = json.loads(event_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event must be the failed source receipt")
    expected_checks = {
        key: key != manifest["isolated_failed_check"] for key in event["checks"]
    }
    if event["checks"] != expected_checks:
        raise SystemExit("source failure is not isolated as declared")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    started = time.perf_counter()
    results = {
        name: evaluate_family(
            event, SolverConfig(**profile), manifest["cyclic_shifts"]
        )
        for name, profile in manifest["solvers"].items()
    }
    acceptance = manifest["acceptance"]
    checks = {
        "source_failure_isolated": True,
        "orbit": max(row["residuals"]["orbit_matching"] for row in results.values())
        <= float(acceptance["maximum_orbit_residual"]),
        "phase": max(row["residuals"]["phase"] for row in results.values())
        <= float(acceptance["maximum_phase_residual"]),
        "tangent": max(row["residuals"]["tangent_transport"] for row in results.values())
        <= float(acceptance["maximum_tangent_residual"]),
        "normalization": max(row["residuals"]["normalization"] for row in results.values())
        <= float(acceptance["maximum_normalization_residual"]),
        "flip": max(
            abs(float(row["flip_spectrum"]["direct_flip_residual"]))
            for row in results.values()
        ) <= float(acceptance["maximum_flip_residual"]),
        "real": max(
            row["flip_spectrum"]["maximum_direct_imaginary"]
            for row in results.values()
        ) <= float(acceptance["maximum_multiplier_imaginary"]),
        "cyclic": max(
            row["flip_spectrum"]["cyclic_product_spread"]
            for row in results.values()
        ) <= float(acceptance["maximum_cyclic_product_spread"]),
        "cross_solver_flip": abs(
            float(results[manifest["reference_solver"]]["flip_spectrum"]["direct_flip_median"])
            - float(results[manifest["independent_solver"]]["flip_spectrum"]["direct_flip_median"])
        ) <= float(acceptance["maximum_cross_solver_flip_difference"]),
        "primitive": float(event["minimum_proper_subperiod_closure"])
        >= float(acceptance["minimum_proper_subperiod_closure"]),
        "section_identity": bool(
            event["section_identity"]["historical_integration_success"]
            and event["section_identity"]["barrio_integration_success"]
            and int(event["section_identity"]["historical_phase_count"])
            == int(manifest["identity"]["historical_phase_count"])
            and int(event["section_identity"]["barrio_phase_count"])
            == int(manifest["identity"]["barrio_phase_count"])
        ),
    }
    output = {
        "schema": "butterfly.jones-augmented-flip-precision-audit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "segment_count": event["segment_count"],
        "fixed_b": event["fixed_b"],
        "fixed_c": event["fixed_c"],
        "corrected_a": event["corrected_a"],
        "period_time": event["period_time"],
        "source_checks": event["checks"],
        "results": results,
        "minimum_proper_subperiod_closure": event["minimum_proper_subperiod_closure"],
        "section_identity": event["section_identity"],
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {
        **output,
        "results": {
            key: {field: value for field, value in row.items() if field != "floquet"}
            for key, row in results.items()
        },
    }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
