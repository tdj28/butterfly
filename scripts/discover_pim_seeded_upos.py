#!/usr/bin/env python3
"""Recover candidate UPOs from exact-flow checks of PIM close-return seeds."""

from __future__ import annotations

import argparse
import io
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    next_section_return,
    select_close_return_candidates,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _complex_rows(values):
    return [
        {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
        for value in values
    ]


def _exact_return_seed(parameters, section, state, lag, solver, maximum_flight_time):
    current = np.asarray(state, dtype=np.float64)
    elapsed = 0.0
    for _ in range(lag):
        returned = next_section_return(
            parameters,
            current,
            section,
            config=solver,
            maximum_flight_time=maximum_flight_time,
        )
        if not returned.success:
            return None
        current = returned.state
        elapsed += returned.flight_time
    return current, elapsed


def _crossing_count(parameters, section, state, period, solver, maximum_crossings):
    crossings = collect_crossings(
        parameters,
        state,
        section,
        transient=0.0,
        observation_horizon=period * (1.0 + 1e-8),
        max_crossings=maximum_crossings,
        config=solver,
    )
    keep = (crossings.times > period * 1e-7) & (
        crossings.times <= period * (1.0 + 1e-8)
    )
    return int(np.count_nonzero(keep)), bool(crossings.integration_success)


def _recover_candidate(case, candidate, states, manifest, solver):
    parameters = RosslerParameters(
        a=float(case["a"]), b=float(case["b"]), c=float(case["c"])
    )
    section = barrio_rossler_section(parameters)
    scales = np.asarray(manifest["selection"]["coordinate_scales"], dtype=float)
    state = states[candidate.start_index]
    exact = _exact_return_seed(
        parameters,
        section,
        state,
        candidate.lag,
        solver,
        float(manifest["exact_return"]["maximum_flight_time"]),
    )
    row = {"seed": asdict(candidate), "exact_return_success": exact is not None}
    if exact is None:
        row["accepted"] = False
        row["reason"] = "one or more exact section returns failed"
        return row
    final_state, period_seed = exact
    exact_distance = float(np.linalg.norm((final_state - state) / scales))
    row["exact_return_normalized_closure"] = exact_distance
    row["period_time_seed"] = period_seed
    if exact_distance > float(
        manifest["acceptance"]["maximum_exact_return_normalized_closure"]
    ):
        row["accepted"] = False
        row["reason"] = "PIM close return does not close under the exact return map"
        return row

    correction = correct_periodic_orbit(
        parameters,
        state,
        period_seed,
        config=solver,
        max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
        tolerance=float(manifest["corrector"]["tolerance"]),
    )
    correction_row = asdict(correction)
    correction_row["initial_state"] = correction.initial_state.tolist()
    correction_row["final_state"] = correction.final_state.tolist()
    row["correction"] = correction_row
    if not correction.success:
        row["accepted"] = False
        row["reason"] = "phase-conditioned periodic shooting did not converge"
        return row

    monodromy = flow_monodromy(
        parameters,
        correction.initial_state,
        correction.period_time,
        config=solver,
    )
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    nontrivial = np.delete(monodromy.multipliers, neutral_index)
    crossing_count, crossing_success = _crossing_count(
        parameters,
        section,
        correction.initial_state,
        correction.period_time,
        solver,
        candidate.lag + 4,
    )
    neutral_error = float(abs(monodromy.multipliers[neutral_index] - 1.0))
    maximum_transverse_modulus = float(np.max(np.abs(nontrivial)))
    row["monodromy"] = {
        "success": monodromy.success,
        "closure_error": monodromy.closure_error,
        "multipliers": _complex_rows(monodromy.multipliers),
        "neutral_multiplier_error": neutral_error,
        "maximum_nontrivial_multiplier_modulus": maximum_transverse_modulus,
        "divergence_integral": monodromy.divergence_integral,
        "predicted_determinant": monodromy.predicted_determinant,
        "computed_determinant": monodromy.computed_determinant,
    }
    row["one_period_section_crossing_count"] = crossing_count
    row["crossing_integration_success"] = crossing_success
    acceptance = manifest["acceptance"]
    checks = {
        "shooting_closure": correction.closure_error
        <= float(acceptance["maximum_flow_closure"]),
        "phase_residual": correction.phase_residual
        <= float(acceptance["maximum_phase_residual"]),
        "monodromy_integration": monodromy.success,
        "neutral_multiplier": neutral_error
        <= float(acceptance["maximum_neutral_multiplier_error"]),
        "crossing_identity": crossing_success and crossing_count == candidate.lag,
        "transverse_instability": maximum_transverse_modulus
        >= 1.0 + float(acceptance["minimum_instability_margin"]),
    }
    row["checks"] = checks
    row["accepted"] = all(checks.values())
    row["reason"] = (
        "identity-qualified unstable periodic orbit"
        if row["accepted"]
        else "one or more orbit-qualification gates failed"
    )
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.pim-seeded-upo-discovery-manifest.v1":
        raise SystemExit("unsupported PIM-seeded UPO manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["reference_solver"])
    selection = manifest["selection"]
    case_rows = []
    started = time.perf_counter()
    for case in manifest["cases"]:
        artifact_bytes = Path(case["states_artifact"]).read_bytes()
        artifact_hash = sha256_bytes(artifact_bytes)
        if artifact_hash != case["states_artifact_sha256"]:
            raise SystemExit(f"state artifact hash mismatch for {case['id']}")
        with np.load(io.BytesIO(artifact_bytes)) as archive:
            selected_keys = sorted(
                key for key in archive.files if key.startswith(case["key_prefix"])
            )
            state_sequences = {key: archive[key] for key in selected_keys}
        candidates = []
        burn_in = int(selection["burn_in_returns"])
        for key, values in state_sequences.items():
            retained = values[burn_in:]
            rows = select_close_return_candidates(
                retained,
                coordinate_scales=selection["coordinate_scales"],
                minimum_lag=int(selection["minimum_lag"]),
                maximum_lag=int(selection["maximum_lag"]),
                candidates_per_lag=int(selection["candidates_per_lag_per_line"]),
                exclusion_radius=int(selection["exclusion_radius"]),
            )
            for row in rows:
                if row.normalized_distance <= float(
                    selection["maximum_pim_normalized_distance"]
                ):
                    candidates.append((row.normalized_distance, key, retained, row))
        candidates.sort(key=lambda item: (item[0], item[1], item[3].lag, item[3].start_index))
        candidates = candidates[: int(selection["maximum_candidates_per_case"])]
        recoveries = []
        for _distance, key, values, candidate in candidates:
            recovered = _recover_candidate(case, candidate, values, manifest, solver)
            recovered["state_key"] = key
            recoveries.append(recovered)
            print(
                json.dumps(
                    {
                        "case": case["id"],
                        "state_key": key,
                        "lag": candidate.lag,
                        "distance": candidate.normalized_distance,
                        "accepted": recovered["accepted"],
                        "reason": recovered["reason"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        accepted = [row for row in recoveries if row["accepted"]]
        case_rows.append(
            {
                "id": case["id"],
                "parameters": {name: float(case[name]) for name in ("a", "b", "c")},
                "states_artifact": case["states_artifact"],
                "states_artifact_sha256": artifact_hash,
                "selected_state_keys": selected_keys,
                "candidate_count": len(candidates),
                "recoveries": recoveries,
                "accepted_upo_count": len(accepted),
                "accepted_lags": sorted({row["seed"]["lag"] for row in accepted}),
                "passed": len(accepted)
                >= int(manifest["acceptance"]["minimum_accepted_upos_per_case"]),
            }
        )
    receipt = {
        "schema": "butterfly.pim-seeded-upo-discovery-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "cases": case_rows,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(case["passed"] for case in case_rows),
        "scientific_scope": "discovery of finite UPO seeds, not a manifold event or TBA continuation",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key != "cases"}, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
