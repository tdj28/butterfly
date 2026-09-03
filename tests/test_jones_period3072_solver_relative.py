from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.audit_jones_period3072_solver_relative_criticality import (
    selected_child_seed,
    solver_parent_seed,
    solver_target_a,
)


def manifest() -> dict:
    return {
        "source_candidate": {"step_length": 0.0005, "direction": -1},
        "solver_targets": {
            "dop853": {
                "parent_seed_iteration": 1,
                "event_upper_a": 1.25,
                "offset_from_upper_bound": 0.125,
                "target_a": 1.375,
            }
        },
    }


def refinement() -> dict:
    return {
        "results": {
            "dop853": {
                "refined_bracket": {
                    "upper_a": 1.25,
                    "upper_residual": 0.01,
                },
                "evaluations": [
                    {
                        "iteration": 1,
                        "a": 1.25,
                        "residual": 0.01,
                        "evaluation": {"nodes": [[1, 2, 3]], "period_time": 4},
                    }
                ],
            }
        }
    }


def test_multiplier_blind_child_selection_is_unique() -> None:
    switch = {
        "accepted_candidates": [
            {"step_length": 0.0005, "direction": -1, "nodes": []},
            {"step_length": 0.0005, "direction": 1, "nodes": []},
        ]
    }
    assert selected_child_seed(switch, manifest())["direction"] == -1


def test_parent_seed_is_positive_upper_endpoint() -> None:
    seed = solver_parent_seed(refinement(), "dop853", manifest())
    assert seed["period_time"] == 4


def test_solver_relative_target_replays() -> None:
    assert solver_target_a(refinement(), "dop853", manifest()) == 1.375


def test_parent_seed_rejects_nonpositive_upper_residual() -> None:
    receipt = refinement()
    receipt["results"]["dop853"]["refined_bracket"]["upper_residual"] = -0.01
    with pytest.raises(ValueError, match="positive side"):
        solver_parent_seed(receipt, "dop853", manifest())
