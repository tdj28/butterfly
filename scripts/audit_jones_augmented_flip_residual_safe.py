#!/usr/bin/env python3
"""Audit a residual-qualified augmented flip with segmented independent solver."""

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


SCHEMA = "butterfly.jones-augmented-flip-residual-safe-audit-manifest.v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported residual-safe augmented-flip audit manifest")
    event_bytes = args.event.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    event = json.loads(event_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event must be the failed source receipt")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    segment_count = int(event["segment_count"])
    nodes = np.asarray(event["nodes"], dtype=float)
    tangents = np.asarray(event["tangent_nodes"], dtype=float)
    fixed_b = float(event["fixed_b"])
    fixed_c = float(event["fixed_c"])
    corrected_a = float(event["corrected_a"])
    period_time = float(event["period_time"])
    parameters = RosslerParameters(a=corrected_a, b=fixed_b, c=fixed_c)
    phase_reference = nodes[0].copy()
    phase = rossler_rhs(0.0, phase_reference, parameters)
    phase /= np.linalg.norm(phase)
    variables = np.r_[nodes.ravel(), period_time, corrected_a, tangents.ravel()]
    independent_solver = SolverConfig(**manifest["independent_solver"])
    started = time.perf_counter()
    independent_residual, _ = augmented_flip_system(
        variables,
        segment_count=segment_count,
        a=None,
        c=fixed_c,
        phase=phase,
        phase_reference=phase_reference,
        solver=independent_solver,
        continuation_parameter="a",
        fixed_b=fixed_b,
    )
    state_count = 3 * segment_count
    independent_components = {
        "orbit_matching": float(np.linalg.norm(independent_residual[:state_count])),
        "phase": float(abs(independent_residual[state_count])),
        "tangent_transport": float(
            np.linalg.norm(independent_residual[state_count + 1 : -1])
        ),
        "normalization": float(abs(independent_residual[-1])),
    }
    independent_floquet = block_and_product_floquet(
        nodes,
        period_time,
        parameters,
        independent_solver,
        manifest["cyclic_shifts"],
    )
    independent_spectrum = flip_spectrum_metrics(independent_floquet)
    acceptance = manifest["acceptance"]
    source_residuals = event["residuals"]
    allowed_stop = manifest["allowed_source_stop"] in event["solver"]["message"]
    source_residual_qualified = bool(
        allowed_stop
        and source_residuals["orbit_matching"]
        <= float(acceptance["maximum_orbit_residual"])
        and source_residuals["phase"] <= float(acceptance["maximum_phase_residual"])
        and source_residuals["tangent_transport"]
        <= float(acceptance["maximum_tangent_residual"])
        and source_residuals["normalization"]
        <= float(acceptance["maximum_normalization_residual"])
        and abs(float(event["flip_spectrum"]["direct_flip_residual"]))
        <= float(acceptance["maximum_reference_flip_residual"])
    )
    checks = {
        "source_residual_qualified": source_residual_qualified,
        "independent_orbit": independent_components["orbit_matching"]
        <= float(acceptance["maximum_independent_orbit_residual"]),
        "independent_phase": independent_components["phase"]
        <= float(acceptance["maximum_independent_phase_residual"]),
        "independent_tangent": independent_components["tangent_transport"]
        <= float(acceptance["maximum_independent_tangent_residual"]),
        "independent_normalization": independent_components["normalization"]
        <= float(acceptance["maximum_independent_normalization_residual"]),
        "independent_flip": abs(
            float(independent_spectrum["direct_flip_residual"])
        )
        <= float(acceptance["maximum_independent_flip_residual"]),
        "independent_real": independent_spectrum["maximum_direct_imaginary"]
        <= float(acceptance["maximum_multiplier_imaginary"]),
        "independent_cyclic": independent_spectrum["cyclic_product_spread"]
        <= float(acceptance["maximum_cyclic_product_spread"]),
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
        "schema": "butterfly.jones-augmented-flip-residual-safe-audit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "source": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__},
        "segment_count": segment_count,
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "corrected_a": corrected_a,
        "period_time": period_time,
        "source_solver_status": event["solver"],
        "source_residuals": source_residuals,
        "source_flip_spectrum": event["flip_spectrum"],
        "source_residual_qualified": source_residual_qualified,
        "independent_residuals": independent_components,
        "independent_floquet": independent_floquet,
        "independent_flip_spectrum": independent_spectrum,
        "minimum_proper_subperiod_closure": event["minimum_proper_subperiod_closure"],
        "section_identity": event["section_identity"],
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    printed = {key: value for key, value in output.items() if key != "independent_floquet"}
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
