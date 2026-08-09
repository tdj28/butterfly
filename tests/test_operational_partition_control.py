from __future__ import annotations

import numpy as np
import pytest

from scripts.qualify_operational_partition_control import (
    compile_joint_partition,
    segment_pairs,
)


def _summary(lower_shift=0.0, upper_shift=0.0):
    return {
        "resolved": True,
        "branch_count": 3,
        "domain": [0.0, 1.0],
        "critical_point_intervals": [
            [0.24 + lower_shift, 0.26 + upper_shift],
            [0.74 + lower_shift, 0.76 + upper_shift],
        ],
    }


def test_segment_pairs_uses_exact_frozen_indices() -> None:
    source, target = segment_pairs(np.arange(12.0), pair_start=3, pair_count=4)
    np.testing.assert_array_equal(source, [3.0, 4.0, 5.0, 6.0])
    np.testing.assert_array_equal(target, [4.0, 5.0, 6.0, 7.0])


def test_segment_pairs_rejects_an_underfilled_segment() -> None:
    with pytest.raises(ValueError, match="insufficient crossing values"):
        segment_pairs(np.arange(5.0), pair_start=2, pair_count=3)


def test_joint_partition_unions_segment_uncertainty_without_relabeling() -> None:
    partition = compile_joint_partition(
        "x",
        [_summary(), _summary(-0.01, 0.015)],
        branch_symbols=("B0", "B1", "B2"),
        critical_symbols=("K0", "K1"),
        section_orientation=-1,
    )
    assert partition["resolved"]
    np.testing.assert_allclose(
        partition["critical_intervals"], ((0.23, 0.275), (0.73, 0.775))
    )
    assert partition["branch_symbols"] == ("B0", "B1", "B2")
    assert partition["critical_symbols"] == ("K0", "K1")
    assert partition["historical_mapping"] is None


def test_joint_partition_refuses_a_contradictory_segment() -> None:
    contradiction = _summary()
    contradiction["branch_count"] = 2
    partition = compile_joint_partition(
        "x",
        [_summary(), contradiction],
        branch_symbols=("B0", "B1", "B2"),
        critical_symbols=("K0", "K1"),
        section_orientation=-1,
    )
    assert not partition["resolved"]
    assert partition["critical_intervals"] == ()


def test_joint_partition_supports_a_two_branch_control() -> None:
    summaries = [
        {
            "resolved": True,
            "branch_count": 2,
            "domain": [0.0, 1.0],
            "critical_point_intervals": [[0.48, 0.51]],
        },
        {
            "resolved": True,
            "branch_count": 2,
            "domain": [-0.01, 1.01],
            "critical_point_intervals": [[0.49, 0.52]],
        },
    ]
    partition = compile_joint_partition(
        "x",
        summaries,
        branch_symbols=("B0", "B1"),
        critical_symbols=("K0",),
        section_orientation=-1,
    )
    assert partition["resolved"]
    assert partition["domain"] == (-0.01, 1.01)
    assert partition["critical_intervals"] == ((0.48, 0.52),)
