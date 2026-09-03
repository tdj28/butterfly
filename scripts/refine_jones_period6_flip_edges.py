#!/usr/bin/env python3
"""Refine fixed-c period-6 real-minus-one Floquet brackets in parameter a."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
import time
from types import SimpleNamespace

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period6-flip-refinement-manifest.v1"


def _one_period_section_states(parameters, correction, section, expected_count, solver):
    crossings = collect_crossings(
        parameters,
        correction.initial_state,
        section,
        transient=0.0,
        observation_horizon=correction.period_time * (1.0 + 1e-7),
        max_crossings=expected_count + 6,
        config=solver,
    )
    keep = (crossings.times > correction.period_time * 1e-7) & (
        crossings.times <= correction.period_time * (1.0 + 1e-7)
    )
    return crossings.states[keep], bool(crossings.integration_success)


def signed_dominant_nontrivial(multipliers):
    values = np.asarray(multipliers, dtype=np.complex128)
    if values.shape != (3,):
        raise ValueError("a three-dimensional flow must supply three multipliers")
    neutral_index = int(np.argmin(np.abs(values - 1.0)))
    transverse = np.delete(values, neutral_index)
    dominant = complex(transverse[int(np.argmax(np.abs(transverse)))])
    return dominant, complex(values[neutral_index]), neutral_index


def _evaluate(a, c, seed, solver, corrector):
    parameters = RosslerParameters(a=float(a), b=0.2, c=float(c))
    correction = correct_periodic_orbit(
        parameters,
        seed["correction"]["initial_state"],
        float(seed["correction"]["period_time"]),
        config=solver,
        max_evaluations=int(corrector["maximum_evaluations"]),
        tolerance=float(corrector["tolerance"]),
    )
    if not correction.success:
        raise RuntimeError("periodic-orbit correction failed")
    monodromy = flow_monodromy(
        parameters, correction.initial_state, correction.period_time, config=solver
    )
    dominant, neutral, _ = signed_dominant_nontrivial(monodromy.multipliers)
    return {
        "a": float(a),
        "c": float(c),
        "correction": {
            "initial_state": correction.initial_state.tolist(),
            "period_time": correction.period_time,
            "closure_error": correction.closure_error,
            "phase_residual": correction.phase_residual,
            "correction_norm": correction.correction_norm,
            "evaluations": correction.evaluations,
        },
        "dominant_multiplier": {
            "real": float(dominant.real),
            "imag": float(dominant.imag),
            "modulus": float(abs(dominant)),
        },
        "neutral_multiplier_error": float(abs(neutral - 1.0)),
        "seed": {
            "correction": {
                "initial_state": correction.initial_state.tolist(),
                "period_time": correction.period_time,
            }
        },
    }


def refine_event(event, lookup, manifest, solver):
    left = lookup[event["left_id"]]
    right = lookup[event["right_id"]]
    c = float(event["c"])
    if not np.isclose(left["parameters"]["c"], c, rtol=0.0, atol=1e-13) or not np.isclose(
        right["parameters"]["c"], c, rtol=0.0, atol=1e-13
    ):
        raise RuntimeError("event endpoint c mismatch")
    left_a = float(left["parameters"]["a"])
    right_a = float(right["parameters"]["a"])
    target = float(manifest["target_multiplier"])
    left_residual = float(left["dominant_nontrivial_multiplier"]["real"]) - target
    right_residual = float(right["dominant_nontrivial_multiplier"]["real"]) - target
    if left_residual * right_residual > 0.0:
        raise RuntimeError("declared event endpoints do not bracket -1")
    evaluations = []
    left_seed, right_seed = left, right
    for _ in range(int(manifest["refinement"]["maximum_iterations"])):
        if right_a - left_a <= float(manifest["refinement"]["a_tolerance"]):
            break
        middle_a = 0.5 * (left_a + right_a)
        seed = left_seed if middle_a - left_a <= right_a - middle_a else right_seed
        middle = _evaluate(middle_a, c, seed, solver, manifest["corrector"])
        middle_residual = middle["dominant_multiplier"]["real"] - target
        middle["multiplier_residual"] = float(middle_residual)
        evaluations.append(middle)
        if left_residual * middle_residual <= 0.0:
            right_a = middle_a
            right_residual = middle_residual
            right_seed = middle["seed"]
        else:
            left_a = middle_a
            left_residual = middle_residual
            left_seed = middle["seed"]
    best = min(evaluations, key=lambda row: abs(row["multiplier_residual"]))
    parameters = RosslerParameters(a=best["a"], b=0.2, c=c)
    correction = SimpleNamespace(
        initial_state=np.asarray(best["correction"]["initial_state"], dtype=float),
        period_time=float(best["correction"]["period_time"]),
    )
    historical, historical_success = _one_period_section_states(
        parameters,
        correction,
        legacy_rossler_section(parameters),
        int(manifest["acceptance"]["historical_phase_count"]),
        solver,
    )
    barrio, barrio_success = _one_period_section_states(
        parameters,
        correction,
        barrio_rossler_section(parameters),
        int(manifest["acceptance"]["barrio_phase_count"]),
        solver,
    )
    acceptance = manifest["acceptance"]
    bracket_width = right_a - left_a
    passed = bool(
        bracket_width <= float(acceptance["maximum_a_bracket_width"])
        and abs(best["multiplier_residual"])
        <= float(acceptance["maximum_multiplier_residual"])
        and abs(best["dominant_multiplier"]["imag"])
        <= float(acceptance["maximum_multiplier_imaginary_part"])
        and best["correction"]["closure_error"]
        <= float(acceptance["maximum_closure_error"])
        and best["neutral_multiplier_error"]
        <= float(acceptance["maximum_neutral_multiplier_error"])
        and historical_success
        and len(historical) == int(acceptance["historical_phase_count"])
        and barrio_success
        and len(barrio) == int(acceptance["barrio_phase_count"])
    )
    best.pop("seed", None)
    return {
        "id": event["id"],
        "c": c,
        "a_bracket": [left_a, right_a],
        "a_estimate": 0.5 * (left_a + right_a),
        "bracket_width": bracket_width,
        "best_evaluation": best,
        "historical_phase_count": len(historical),
        "barrio_phase_count": len(barrio),
        "evaluation_count": len(evaluations),
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-6 flip refinement manifest")
    candidate_path = Path(manifest["candidate_input"]["path"])
    candidate_bytes = candidate_path.read_bytes()
    if sha256_bytes(candidate_bytes) != manifest["candidate_input"]["sha256"]:
        raise SystemExit("candidate input hash mismatch")
    for evidence in manifest["evidence"]:
        if sha256_bytes(Path(evidence["path"]).read_bytes()) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("flip refinement requires clean source")
    candidates = json.loads(candidate_bytes)["candidates"]
    lookup = {row["id"]: row for row in candidates}
    solver = SolverConfig(**manifest["solver"])
    started = time.perf_counter()
    results = [refine_event(event, lookup, manifest, solver) for event in manifest["events"]]
    passed = bool(
        len(results) == int(manifest["acceptance"]["required_events"])
        and all(row["passed"] for row in results)
    )
    output = {
        "schema": "butterfly.jones-period6-flip-refinement.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "candidate_input_sha256": sha256_bytes(candidate_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "target_multiplier": manifest["target_multiplier"],
        "results": results,
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
                "events": [
                    {"id": row["id"], "a": row["a_estimate"], "width": row["bracket_width"], "passed": row["passed"]}
                    for row in results
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
