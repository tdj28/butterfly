from __future__ import annotations

import numpy as np

from scripts.qualify_jones_historical_alphabet import (
    analyze_segment,
    classify_branch,
    nested_value,
)


PARTITION = {
    "domain": [0.0, 1.0],
    "critical_intervals": [[0.2, 0.3], [0.7, 0.8]],
}


def test_classify_branch_censors_domain_and_critical_intervals() -> None:
    assert classify_branch(-0.1, PARTITION) is None
    assert classify_branch(0.1, PARTITION) == 0
    assert classify_branch(0.25, PARTITION) is None
    assert classify_branch(0.5, PARTITION) == 1
    assert classify_branch(0.75, PARTITION) is None
    assert classify_branch(0.9, PARTITION) == 2


def test_nested_evidence_pass_field() -> None:
    assert nested_value({"gates": {"passed": True}}, "gates.passed") is True


def test_geometry_summary_recovers_inner_and_third_branch_semantics() -> None:
    values = np.asarray([0.1, 0.9, 0.5, 0.9, 0.1, 0.9, 0.5, 0.9, 0.1])
    states = np.column_stack((values, np.zeros_like(values), np.zeros_like(values)))
    acceptance = {
        "minimum_resolved_pairs": 8,
        "minimum_target_branch_count": 2,
        "minimum_inner_normalized_median_gap": 0.2,
        "require_strict_inner_distance_separation": True,
        "minimum_third_to_inner_transitions": 2,
        "maximum_third_self_transition_fraction": 0.0,
    }
    # Distance is measured from x=1, so high-coordinate B2 is the inner branch.
    summary, source, target = analyze_segment(
        states,
        np.asarray([1.0, 0.0, 0.0]),
        axis=0,
        partition=PARTITION,
        pair_start=0,
        pair_count=8,
        acceptance=acceptance,
    )
    assert summary["passed"]
    assert summary["distance_median_order_nearest_first"][0] == "B2"
    assert summary["third_to_inner_transitions"] == 2
    assert source.shape == target.shape == (8,)
