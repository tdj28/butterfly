#!/usr/bin/env python3
"""Recompute two released numerical examples, not their discovery history.

The atlas wrapper calls this after verifying the release. This entry point also
verifies the bundle itself. These are same-method reproduction checks, not an
independent validation of a bifurcation or a homoclinic orbit.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
import subprocess
import time

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, flow_monodromy

try:
    from scripts.research_bundle import verify_bundle, check_replay_environment
    from scripts.multiple_shooting_core import integrate_segment
    from scripts.refine_jones_period6_flip_edges import _evaluate, _one_period_section_states
    from scripts.scan_jones_homoclinic_manifold_match import (
        align_local_geometry, stable_manifold_targets,
    )
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
except ModuleNotFoundError:  # Direct script invocation from the repository.
    from research_bundle import verify_bundle, check_replay_environment
    from multiple_shooting_core import integrate_segment
    from refine_jones_period6_flip_edges import _evaluate, _one_period_section_states
    from scan_jones_homoclinic_manifold_match import align_local_geometry, stable_manifold_targets
    from scan_jones_homoclinic_unstable_angles import eigenspaces

from butterfly import barrio_rossler_section, legacy_rossler_section
from types import SimpleNamespace


def read_json(root: Path, name: str) -> dict:
    return json.loads((root / name).read_text())


def flip_identity_checks(correction, seed, policy):
    period_difference = abs(correction.period_time - seed["period_time"]) / seed["period_time"]
    state_difference = float(np.linalg.norm(np.asarray(correction.initial_state) - seed["initial_state"]))
    return {
        "same_seed_period": bool(period_difference <= policy["maximum_relative_period_difference"]),
        "same_phase_fixed_state": bool(state_difference <= policy["maximum_phase_fixed_state_difference"]),
    }


def segment_residuals(starts, destinations, duration, parameters, solver):
    """Reintegrate every short arc; do not substitute stored residuals."""
    starts = np.asarray(starts, dtype=float)
    destinations = np.asarray(destinations, dtype=float)
    if (
        starts.ndim != 2 or starts.shape[1] != 3
        or starts.shape != destinations.shape or not len(starts)
        or not np.all(np.isfinite(starts))
        or not np.all(np.isfinite(destinations))
        or not np.isfinite(duration) or duration <= 0
    ):
        raise ValueError("finite equal-sized three-dimensional arcs and positive duration required")
    residuals = []
    for start, destination in zip(starts, destinations, strict=True):
        endpoint, _, _ = integrate_segment(
            start, duration, parameters, solver, continuation_parameter="a"
        )
        residuals.append(endpoint - destination)
    residuals = np.asarray(residuals)
    if not np.all(np.isfinite(residuals)):
        raise ValueError("nonfinite reintegration result")
    return np.linalg.norm(residuals, axis=1)


def replay_flip(root: Path) -> dict:
    manifest = read_json(root, "experiments/manifests/EXP-205-lower-c-period6-flip-refinement.json")
    receipt = read_json(root, "artifacts/EXP-205/receipt.json")
    matches = [row for row in receipt["results"] if row["id"] == "flip-c7192"]
    if len(matches) != 1:
        raise ValueError("unique released flip-c7192 seed required")
    seed = matches[0]["best_evaluation"]
    solver = SolverConfig(**manifest["solver"])
    result = _evaluate(seed["a"], seed["c"], seed, solver, manifest["corrector"])
    # Check neutral/flip values only. A tiny third eigenvalue is not a zero
    # multiplier or a superstability measurement in this dissipative flow.
    correction = SimpleNamespace(**result["correction"])
    parameters = RosslerParameters(a=result["a"], b=0.2, c=result["c"])
    monodromy = flow_monodromy(parameters, correction.initial_state, correction.period_time, config=solver)
    gate = manifest["acceptance"]
    counts, integrations = {}, {}
    for name, section, expected in (
        ("historical", legacy_rossler_section(parameters), gate["historical_phase_count"]),
        ("barrio", barrio_rossler_section(parameters), gate["barrio_phase_count"]),
    ):
        states, success = _one_period_section_states(parameters, correction, section, expected, solver)
        counts[name], integrations[name] = len(states), success
    checks = {
        "monodromy_integration": bool(monodromy.success),
        "flow_closure": monodromy.closure_error <= gate["maximum_closure_error"],
        "corrector_closure": correction.closure_error <= gate["maximum_closure_error"],
        "phase_condition": correction.phase_residual <= max(10 * manifest["corrector"]["tolerance"], 1e-10),
        "neutral_multiplier": result["neutral_multiplier_error"] <= gate["maximum_neutral_multiplier_error"],
        "real_flip_multiplier": abs(result["dominant_multiplier"]["imag"]) <= gate["maximum_multiplier_imaginary_part"],
        "flip_multiplier": abs(result["dominant_multiplier"]["real"] - manifest["target_multiplier"]) <= gate["maximum_multiplier_residual"],
        "historical_section": integrations["historical"] and counts["historical"] == gate["historical_phase_count"],
        "barrio_section": integrations["barrio"] and counts["barrio"] == gate["barrio_phase_count"],
    }
    identity_policy = read_json(root, "experiments/core-bundle.json")["numerical_replay"]["flip_identity"]
    checks.update(flip_identity_checks(correction, seed["correction"], identity_policy))
    result.pop("seed")
    return {
        "kind": "fixed-seed periodic correction and Floquet/section recomputation",
        "source": "EXP-205/flip-c7192", "checks": checks, "passed": all(checks.values()),
        "evaluation": result, "section_counts": counts,
        "flow_closure_error": monodromy.closure_error,
        "period_difference_from_saved_seed": abs(correction.period_time - seed["correction"]["period_time"]),
        "phase_fixed_state_difference_from_saved_seed": float(np.linalg.norm(np.asarray(correction.initial_state) - seed["correction"]["initial_state"])),
        "identity_policy": identity_policy,
        "limitation": "Does not repeat bracket discovery or prove bifurcation transversality.",
    }


def replay_homoclinic(root: Path) -> dict:
    manifest = read_json(root, "experiments/manifests/EXP-342-jones-homoclinic-radau-32-segment.json")
    receipt = read_json(root, "artifacts/EXP-342/receipt.json")
    variables = receipt["final_variables"]
    parameters = RosslerParameters(a=variables["a"], **manifest["fixed_parameters"])
    reference = RosslerParameters(a=manifest["reference_a"], **manifest["fixed_parameters"])
    _, _, reference_stable, reference_plane = eigenspaces(reference)
    equilibrium, _, stable, plane = align_local_geometry(parameters, reference_stable, reference_plane)
    angle = variables["angle"]
    initial = equilibrium + manifest["unstable_seed_radius"] * (
        np.cos(angle) * plane[:, 0] + np.sin(angle) * plane[:, 1]
    )
    targets = [row for row in stable_manifold_targets(parameters, equilibrium, stable, manifest)
               if row["status"] == "completed" and row["branch_sign"] == manifest["stable_branch_sign"]]
    if len(targets) != 1:
        raise ValueError("stable-manifold endpoint reconstruction failed")
    target = np.asarray(targets[0]["state"])
    nodes = np.asarray(receipt["final_nodes"], dtype=float)
    count = manifest["segment_count"]
    if nodes.shape != (count - 1, 3):
        raise ValueError("released homoclinic node count mismatch")
    residuals = segment_residuals(
        np.vstack((initial, nodes)), np.vstack((nodes, target)),
        variables["total_flight_time"] / count, parameters, SolverConfig(**manifest["solver"]),
    )
    maximum = float(max(residuals))
    target_difference = float(np.linalg.norm(target - receipt["final_stable_target"]))
    threshold = manifest["acceptance"]["maximum_root_block_residual"]
    checks = {"all_short_arcs_close": maximum <= threshold,
              "stable_target_reproduced": target_difference <= threshold}
    return {
        "kind": "fixed-node Radau reintegration with reconstructed endpoint geometry",
        "source": "EXP-342", "checks": checks, "passed": all(checks.values()),
        "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
        "flight_time": variables["total_flight_time"], "segment_count": count,
        "block_residual_norms": residuals.tolist(), "maximum_block_residual": maximum,
        "stored_maximum_block_residual": receipt["final_maximum_block_residual"],
        "gate": threshold, "stable_target_difference": target_difference,
        "limitation": "Same boundary formulation and saved nodes, not a new root search, parameter-error bound, or proof of an infinite-time homoclinic orbit. Long direct forward replay is ill-conditioned.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    index = verify_bundle(args.bundle_dir)
    root = Path(__file__).resolve().parents[1]
    check_replay_environment(args.bundle_dir, root)
    if args.output_dir.resolve() == args.bundle_dir.resolve() or args.bundle_dir.resolve() in args.output_dir.resolve().parents:
        raise ValueError("replay output must not be inside the input bundle")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()
    results = {}
    for name, replay in (("flip", replay_flip), ("homoclinic", replay_homoclinic)):
        try:
            results[name] = replay(args.bundle_dir)
        except Exception as error:
            results[name] = {"passed": False, "error": f"{type(error).__name__}: {error}"}
    output = {
        "schema": "butterfly.core-numerical-replay.v1",
        "source_commit": revision,
        "bundle_schema": index.get("schema"),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "elapsed_seconds": time.perf_counter() - started, "results": results,
        "passed": all(row["passed"] for row in results.values()),
    }
    with (args.output_dir / "receipt.json").open("x") as handle:
        json.dump(output, handle, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"passed": output["passed"], "results": {k: v["passed"] for k, v in results.items()}}))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
