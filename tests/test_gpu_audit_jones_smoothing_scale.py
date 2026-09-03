import numpy as np

from scripts.gpu_audit_jones_smoothing_scale import nested_pairs, transition_summary


def test_transition_summary_accepts_monotone_with_unresolved_gap():
    result = transition_summary([3, 3, None, 2, 2], [1e-6, 3e-6, 1e-5, 3e-5, 1e-4])
    assert result["resolved"]
    assert result["lower_index"] == 1
    assert result["upper_index"] == 3


def test_transition_summary_rejects_reversal_and_extra_branch_count():
    assert not transition_summary([3, 2, 3], [1e-6, 1e-5, 1e-4])["resolved"]
    assert not transition_summary([3, 4, 2], [1e-6, 1e-5, 1e-4])["resolved"]


def test_nested_pairs_uses_rectangular_seed_strides():
    states = [np.column_stack((np.zeros(3), np.zeros(3), np.arange(3) + seed)) for seed in range(8)]
    record = {"seed_ids": np.arange(8), "states": states}
    source, target = nested_pairs(record, axis=2, z_count=4, x_stride=2, z_stride=2)
    assert source.tolist() == [0.0, 1.0, 2.0, 3.0]
    assert target.tolist() == [1.0, 2.0, 3.0, 4.0]
