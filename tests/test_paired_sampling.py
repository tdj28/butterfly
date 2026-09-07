"""Outcome-free controls; no nominated Rössler trajectory is evaluated."""
import numpy as np
import pytest

from butterfly.paired_sampling import (SECTIONS, seed_table, seed_commitment,
    section_pairs, common_sample, block_bootstrap_indices)


def events(ids, times):
    seed_ids = np.repeat(ids, len(times))
    t = np.tile(times, len(ids))
    return {"global_seed_ids": seed_ids, "times": t, "states": np.column_stack((t, t, t)),
            "accepted": np.ones(len(t), dtype=bool), "gate_unresolved": np.zeros(len(t), dtype=bool),
            "orientation_unresolved": np.zeros(len(t), dtype=bool)}


def test_seed_plan_is_exact_reproducible_and_has_no_outcomes():
    a, b = seed_table(), seed_table()
    assert set(a) == {"global_seed_ids", "xz", "holdout"}
    for key in a:
        np.testing.assert_array_equal(a[key], b[key])
    assert len(a["xz"]) == 8192 and a["holdout"].sum() == 4096
    assert np.all(a["xz"] > [-14, .008]) and np.all(a["xz"] < [-.2, .55])
    assert len(np.unique(a["xz"], axis=0)) == 8192
    assert seed_commitment(a) == seed_commitment(b)
    assert seed_commitment(a) != seed_commitment(seed_table(random_seed=481002))


def test_true_consecutive_pair_identity_and_physical_strata():
    raw = events([901, 17], np.arange(0., 5.1, .5))
    result = section_pairs(raw, [901, 17], [[0, 2], [2, 4]], strata_per_window=2)
    assert result["sufficient"].all()
    np.testing.assert_array_equal(result["pair_indices"][0], [[[0, 1], [2, 3]], [[4, 5], [6, 7]]])
    assert (result["eligible_counts"] == 2).all()


def test_do_not_invent_last_window_successor():
    raw = events([1], [0, 1, 2, 3, 5])
    result = section_pairs(raw, [1], [[0, 4]], strata_per_window=4)
    assert not result["sufficient"][0] and (result["pair_indices"][0, 0, 3] == -1).all()


def test_rejected_direction_is_not_a_return_but_unresolved_root_blocks_seed():
    raw = events([7], [0, .25, .5, 1., 1.5, 2.])
    raw["accepted"][1] = False
    result = section_pairs(raw, [7], [[0, 2]], strata_per_window=2)
    np.testing.assert_array_equal(result["pair_indices"][0, 0, 0], [0, 2])
    raw["orientation_unresolved"][1] = True
    result = section_pairs(raw, [7], [[0, 2]], strata_per_window=2)
    assert not result["sufficient"].any()


def test_unknown_seed_duplicate_time_and_nonboolean_masks_rejected():
    for kind in ("id", "time", "mask"):
        raw = events([7], [0, 1, 2])
        if kind == "id":
            raw["global_seed_ids"][0] = 9
        elif kind == "time":
            raw["times"][1] = 0
        else:
            raw["accepted"] = np.ones(3)
        with pytest.raises(ValueError):
            section_pairs(raw, [7], [[0, 2]])


def test_common_cohort_partitions_all_cases_and_preserves_global_ids():
    ids = np.array([99, 2, 55, 11, 42, 9, 28])
    raw = {name: events(ids, np.arange(0., 4.5, .5)) for name in SECTIONS}
    # Missing final stratum on only one section excludes that seed from BOTH.
    last = (raw[SECTIONS[1]]["global_seed_ids"] == 28) & (raw[SECTIONS[1]]["times"] >= 3)
    raw[SECTIONS[1]]["accepted"][last] = False
    state = {"failed": np.array([True, False, False, False, False, False, False]),
             "ambiguous": np.zeros((7, 2), dtype=bool), "capture_times": np.full((7, 2), np.nan)}
    state["ambiguous"][1, 0] = True
    state["capture_times"][2, 0] = 3.
    state["capture_times"][3, 1] = 3.
    state["capture_times"][4] = [2., 3.]
    sample = common_sample(ids, state, raw, [[0, 4]], horizon=4.)
    assert sample["counts"] == {"total": 7, "failed": 1, "ambiguous_nonfailed": 1,
        "historical_only": 1, "barrio_only": 1, "both": 1, "neither_insufficient": 1, "retained": 1}
    assert sample["global_seed_ids"][sample["retained"]].tolist() == [9]
    for value in raw.values():
        assert len(value["times"]) == 63  # raw failed/captured records untouched


def test_faster_section_receives_no_more_selected_weight():
    raw = {SECTIONS[0]: events([10, 20], np.arange(0., 4.1, 1.)),
           SECTIONS[1]: events([10, 20], np.arange(0., 4.1, .25))}
    state = {"failed": np.zeros(2, bool), "ambiguous": np.zeros((2, 2), bool),
             "capture_times": np.full((2, 2), np.nan)}
    sample = common_sample([10, 20], state, raw, [[0, 4]], horizon=4.)
    assert sample["retained"].all()
    for indices in sample["section_pair_indices"].values():
        assert indices.shape == (2, 1, 4, 2) and (indices >= 0).all()


def test_seed_permutation_and_event_interleaving_preserve_selected_pairs():
    ids = [20, 7]
    raw = events(ids, [0, 1, 2, 3, 4])
    base = section_pairs(raw, ids, [[0, 4]])
    order = np.argsort(raw["times"], kind="stable")
    reordered = {k: v[order] for k, v in raw.items()}
    other = section_pairs(reordered, ids[::-1], [[0, 4]])
    np.testing.assert_array_equal(raw["times"][base["pair_indices"]],
                                  reordered["times"][other["pair_indices"]][::-1])


def test_block_bootstrap_is_reproducible_and_resamples_whole_seeds():
    draw = block_bootstrap_indices(20, 100, random_seed=481002)
    np.testing.assert_array_equal(draw, block_bootstrap_indices(20, 100, random_seed=481002))
    pairs = np.arange(20*8).reshape(20, 8)
    resampled = pairs[draw]
    assert resampled.shape == (100, 20, 8)
    assert np.all(np.diff(resampled, axis=-1) == 1)
    assert len(np.unique(draw[0])) < 20
