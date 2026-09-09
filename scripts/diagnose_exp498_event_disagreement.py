#!/usr/bin/env python3
"""Exploratory saved-event decomposition; never changes EXP-498 decisions.

Delta q = f(midpoint) delta t + remainder is a first-order diagnostic, not
an integration-error bound or a replacement section-state acceptance test.
Every paired accepted event is retained, including passing comparisons.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly._paired_startup import sha256, write_json
from scripts import plot_exp498_boundary_transport as plot

SOURCE_SHA = "f327a6acb9bb72cd0286ff41090f38e12e3b10a0ff9f476b0a6b2f705e176344"


def decompose(first, second, field, scales):
    a, b = np.asarray(first["state"]), np.asarray(second["state"])
    delta = a - b
    dt = first["time"] - second["time"]
    velocity = np.asarray(field((a + b) / 2))
    phase = velocity * dt
    residual = delta - phase
    norm = lambda v: float(np.max(np.abs(v / scales)))
    return dict(time_difference=dt, state_difference=delta.tolist(),
        midpoint_velocity=velocity.tolist(), first_order_phase=phase.tolist(),
        remainder=residual.tolist(), scaled_state_difference=norm(delta),
        scaled_first_order_phase=norm(phase), scaled_remainder=norm(residual),
        normal_to_z_amplification=float(abs(velocity[2] / velocity[1])) if velocity[1] else None)


def diagnose(result):
    plan, _ = plot.validate(result)
    parameters = RosslerParameters(**plan["anchor_parameters"])
    rows = []
    for candidate in result["rows"]:
        for side in candidate["boundary"]["sides"]:
            events = [[e for e in r["reconstructed"] if e["accepted"]] for r in side["reports"]]
            pairs = []
            if len(events[0]) == len(events[1]):
                for index, (a, b) in enumerate(zip(*events, strict=True)):
                    value = decompose(a, b, lambda q: rossler_rhs(0, q, parameters),
                                      np.asarray(plan["boundary"]["scales"]))
                    pairs.append(dict(index=index, **value,
                        original_state_gate_passed=value["scaled_state_difference"] <= plan["boundary"]["side_solver_scaled_state"],
                        original_time_gate_passed=abs(value["time_difference"]) <= plan["boundary"]["side_solver_time"]))
            rows.append(dict(id=candidate["id"], dose=side["dose"],
                event_counts=[len(e) for e in events], pairs=pairs))
    return dict(experiment_id="EXP-498", analysis="post-outcome-first-order-event-diagnostic",
        new_integrations=0, changes_parent_decisions=False, symbolic_chains_verified=False,
        scope="Algebra on all saved accepted event pairs, not a new accuracy qualification or rigorous error bound.",
        parent_result_sha256=SOURCE_SHA, producer_sha256=sha256(Path(__file__)), rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    path = plot.run.ROOT / "docs/experiments/receipts/EXP-498-boundary-transport-result.json"
    if sha256(path) != SOURCE_SHA:
        raise ValueError("parent result anchor differs")
    write_json(args.output, diagnose(json.loads(path.read_bytes())))


if __name__ == "__main__":
    main()
