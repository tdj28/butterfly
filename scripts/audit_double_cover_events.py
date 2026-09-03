#!/usr/bin/env python3
"""Audit whether +1 event orbits are double covers of fundamental flip cycles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, flow_monodromy, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def select_event(specification: dict, receipts: dict[str, dict]) -> dict:
    source = receipts[specification["source"]]
    if specification["source"] == "source_event":
        return {
            "a": float(source["fixed_a"]),
            "b": float(source["corrected_b"]),
            "c": float(source["fixed_c"]),
            "initial_state": source["initial_state"],
            "period_time": float(source["period_time"]),
        }
    if specification.get("selector") == "minimum_b":
        row = min(source["rows"], key=lambda candidate: float(candidate["b"]))
    else:
        row = next(
            candidate
            for candidate in source["rows"]
            if abs(float(candidate["a"]) - float(specification["a"])) < 1e-12
            and abs(
                float(candidate.get("c", source.get("fixed_c")))
                - float(specification["c"])
            )
            < 1e-12
        )
    return {
        "a": float(row["a"]),
        "b": float(row["b"]),
        "c": float(row.get("c", source.get("fixed_c"))),
        "initial_state": row["initial_state"],
        "period_time": float(row["period_time"]),
    }


def closure_at_times(
    event: dict, times: list[float], solver: SolverConfig
) -> list[float]:
    parameters = RosslerParameters(a=event["a"], b=event["b"], c=event["c"])
    state = np.asarray(event["initial_state"], dtype=float)
    integration = solve_ivp(
        lambda time, current: rossler_rhs(time, current, parameters),
        (0.0, max(times)),
        state,
        t_eval=sorted(times),
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not integration.success:
        raise RuntimeError(f"divisor integration failed: {integration.message}")
    by_time = {
        float(time): float(np.linalg.norm(integration.y[:, index] - state))
        for index, time in enumerate(sorted(times))
    }
    return [by_time[float(time)] for time in times]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-event", type=Path, required=True)
    parser.add_argument("--source-surface", type=Path, required=True)
    parser.add_argument("--source-curve", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.double-cover-audit-manifest.v1":
        raise SystemExit("unsupported double-cover audit manifest")
    paths = {
        "source_event": args.source_event,
        "source_surface": args.source_surface,
        "source_curve": args.source_curve,
    }
    raw_receipts = {name: path.read_bytes() for name, path in paths.items()}
    for name, raw in raw_receipts.items():
        if sha256_bytes(raw) != manifest["source_receipt_sha256"][name]:
            raise SystemExit(f"{name} receipt hash does not match manifest")
    receipts = {name: json.loads(raw) for name, raw in raw_receipts.items()}
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("double-cover audit requires clean source")

    solver = SolverConfig(**manifest["solver"])
    divisors = list(map(int, manifest["divisors_to_exclude"]))
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    rows = []
    for specification in manifest["events"]:
        event = select_event(specification, receipts)
        state = np.asarray(event["initial_state"], dtype=float)
        parameters = RosslerParameters(a=event["a"], b=event["b"], c=event["c"])
        half_period = event["period_time"] / 2.0
        half = flow_monodromy(parameters, state, half_period, config=solver)
        full = flow_monodromy(parameters, state, event["period_time"], config=solver)
        half_neutral = int(np.argmin(np.abs(half.multipliers - 1.0)))
        half_nontrivial = np.delete(half.multipliers, half_neutral)
        half_flip = complex(half_nontrivial[int(np.argmin(np.abs(half_nontrivial + 1.0)))])
        full_neutral = int(np.argmin(np.abs(full.multipliers - 1.0)))
        full_nontrivial = np.delete(full.multipliers, full_neutral)
        full_unit = complex(full_nontrivial[int(np.argmin(np.abs(full_nontrivial - 1.0)))])
        divisor_times = [event["period_time"] / divisor for divisor in divisors]
        divisor_closures = closure_at_times(event, divisor_times, solver)
        monodromy_square_residual = float(
            np.linalg.norm(full.monodromy - half.monodromy @ half.monodromy)
        )
        row = {
            "id": specification["id"],
            "parameters": {"a": event["a"], "b": event["b"], "c": event["c"]},
            "stored_period": event["period_time"],
            "fundamental_period_candidate": half_period,
            "half_period_closure": half.closure_error,
            "full_period_closure": full.closure_error,
            "half_period_multipliers": [
                {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
                for value in half.multipliers
            ],
            "full_period_multipliers": [
                {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
                for value in full.multipliers
            ],
            "half_period_flip_multiplier": {
                "real": float(half_flip.real),
                "imag": float(half_flip.imag),
                "distance_to_minus_one": float(abs(half_flip + 1.0)),
            },
            "full_period_unit_multiplier": {
                "real": float(full_unit.real),
                "imag": float(full_unit.imag),
                "distance_to_plus_one": float(abs(full_unit - 1.0)),
            },
            "monodromy_square_residual": monodromy_square_residual,
            "other_divisor_closures": {
                str(divisor): closure
                for divisor, closure in zip(divisors, divisor_closures, strict=True)
            },
            "minimum_other_divisor_closure": min(divisor_closures),
        }
        row["passed"] = bool(
            row["half_period_closure"]
            <= float(acceptance["max_half_period_closure"])
            and row["half_period_flip_multiplier"]["distance_to_minus_one"]
            <= float(acceptance["max_half_period_minus_one_distance"])
            and row["full_period_unit_multiplier"]["distance_to_plus_one"]
            <= float(acceptance["max_full_period_plus_one_distance"])
            and row["monodromy_square_residual"]
            <= float(acceptance["max_monodromy_square_residual"])
            and row["minimum_other_divisor_closure"]
            >= float(acceptance["minimum_other_divisor_closure"])
        )
        rows.append(row)

    receipt = {
        "schema": "butterfly.double-cover-audit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": {
            name: sha256_bytes(raw) for name, raw in raw_receipts.items()
        },
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation_limit": "Numerical double-cover and flip identities reclassify the local event; interval validation and surface-wide audits remain open.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
