"""Synthetic checks only: no research journals, integration or network."""
import numpy as np
import pytest
from scripts import diagnose_exp483_support as d
from butterfly.paired_sampling import section_pairs


def events(times, *, ids=None, accepted=None, ambiguous=None):
    times = np.asarray(times, float)
    n = len(times)
    return dict(global_seed_ids=np.zeros(n, dtype=int) if ids is None else np.asarray(ids, int),
        times=times, states=np.column_stack((times, times*0, times+1)),
        accepted=np.ones(n, bool) if accepted is None else np.asarray(accepted, bool),
        gate_unresolved=np.zeros(n, bool) if ambiguous is None else np.asarray(ambiguous, bool),
        orientation_unresolved=np.zeros(n, bool))


def test_true_consecutive_pairs_and_window_endpoints():
    data = events([0, 1, 2, 3, 4, 5], accepted=[1, 1, 0, 1, 1, 1])
    result = d.pairs_in_window(data, (1, 4))
    assert result["times"].tolist() == [[1, 3], [3, 4]]
    assert result["values"].tolist() == [[1, 3], [3, 4]]


def test_ambiguity_rejects_whole_seed_even_outside_window():
    data = events([0, 1, 2, 3, 4, 0, 1, 2], ids=[8, 8, 8, 8, 8, 9, 9, 9],
                  ambiguous=[1, 0, 0, 0, 0, 0, 0, 0])
    result = d.pairs_in_window(data, (1, 4))
    assert result["ids"].tolist() == [9]
    assert result["times"].tolist() == [[1, 2]]


def test_independent_stratum_selector_matches_original_with_interleaved_seeds():
    times = np.arange(0, 10, .5)
    data = events(np.repeat(times, 2), ids=np.tile([10, 20], len(times)))
    original = section_pairs(data, np.array([10, 20]), [(1, 9)], strata_per_window=4)
    indices = original["pair_indices"][:, 0].reshape(-1, 2)
    independent = d.pairs_in_window(data, (1, 9), first_per_stratum=True)
    assert np.array_equal(independent["times"], data["times"][indices])
    assert independent["ids"].tolist() == [10]*4+[20]*4


def test_empty_or_insufficient_window_is_not_interpolated():
    for data in (events([]), events([0, 20])):
        for first in (False, True):
            result = d.pairs_in_window(data, (1, 9), first_per_stratum=first)
            assert result["values"].shape == (0, 2)


def test_nonmonotonic_event_times_rejected():
    with pytest.raises(ValueError, match="increase"):
        d.pairs_in_window(events([0, 2, 1]), (0, 3))


def test_occupancy_counts_seeds_not_pairs_and_keeps_zero_pair_members():
    result = d.occupancy(np.array([[.1, 0], [.1, 0], [.8, 0]]),
                         np.array([4, 4, 8]), np.array([4, 8, 9]), [0, 1], 2)
    assert result["distinct_seeds_per_bin"] == [1, 1]
    assert result["pairs_per_seed_histogram"] == {"0": 1, "1": 1, "2": 1}
    assert result["observed_seeds"] == 2 and result["population_seeds"] == 3


def test_new_out_of_bounds_values_do_not_falsely_fill_edge_bins():
    result = d.occupancy(np.array([[-.1, 0], [1.1, 0], [0, 0], [1, 0]]),
                         np.arange(4), np.arange(4), [0, 1], 3)
    assert result["distinct_seeds_per_bin"] == [1, 0, 1]
    assert result["pairs_outside_original_bounds"] == 2


def test_unknown_seed_or_degenerate_bounds_rejected():
    with pytest.raises(ValueError, match="invalid"):
        d.occupancy(np.zeros((1, 2)), np.array([1]), np.array([2]), [0, 1], 3)
    with pytest.raises(ValueError, match="invalid"):
        d.occupancy(np.zeros((1, 2)), np.array([1]), np.array([1]), [0, 0], 3)


def test_unsupported_partition_is_disjoint_even_for_sparse_outside_bins():
    values = np.column_stack(([.01, .3, .5, .7, 1.1], np.zeros(5)))
    variant = dict(bins=4, normalized_domain=[.2, .8],
        model=dict(occupied_bins=[False, True, False, True]), heldout_unsupported_fraction=1-1/5)
    result = d.unsupported_parts(values, [0, 1], variant)
    assert result["outside_fitted_interval"] == 2
    assert result["inside_interval_unsupported_bin"] == 2
    assert result["supported"] == 1
    assert sum(result[k] for k in ("outside_fitted_interval", "inside_interval_unsupported_bin", "supported")) == 5


def test_missing_model_stays_not_evaluated_and_mismatch_fails():
    assert d.unsupported_parts(np.empty((0, 2)), [0, 1], dict(reason="gap"))["status"] == "not-evaluated"
    with pytest.raises(ValueError, match="differs"):
        d.unsupported_parts(np.array([[.5, .1]]), [0, 1], dict(bins=2,
            normalized_domain=[0, 1], model=dict(occupied_bins=[True, True]), heldout_unsupported_fraction=.1))


def test_capture_detection_partition_and_never_captured():
    times = np.array([[1, 2], [2, 3], [3, 4], [50, 60]])
    captures = np.array([[3, np.nan], [np.nan, 3], [3, 5], [np.nan, np.nan]])
    result = d.capture_phase(times, captures)
    assert result["before_detection"].tolist() == [True, False, False, True]
    assert result["straddling_detection"].tolist() == [False, True, False, False]
    assert result["at_or_after_detection"].tolist() == [False, False, True, False]
    assert np.all(sum(v.astype(int) for v in result.values()) == 1)


def test_population_partition_preserves_failures_and_ambiguity():
    state = dict(failed=np.array([1, 0, 0, 0, 0, 0, 0], bool),
        ambiguous=np.array([[1, 0], [1, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]], bool),
        capture_times=np.array([[1, 1], [1, 1], [1, np.nan], [np.nan, 1], [1, 2], [np.nan, np.nan], [np.nan, np.nan]]))
    profile = dict(state=state, retained=np.array([0, 0, 0, 0, 0, 0, 1], bool),
                   counts={k: 1 for k in d.GROUPS})
    groups, valid = d.populations(profile)
    assert all(mask.sum() == 1 for mask in groups.values())
    assert valid.tolist() == [False, False, True, True, True, True, True]
