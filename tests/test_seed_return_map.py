"""Exact-map controls for the seed-level analysis, not flow replication."""
from dataclasses import replace
import numpy as np
import pytest

from butterfly.seed_return_map import MapOptions, audit_map


OPTIONS = MapOptions(minimum_seeds=64, bootstrap_samples=16)


def blocks(fn, seed, count=128):
    x = np.random.Generator(np.random.PCG64(seed)).random((count, 8))
    return np.stack((x, fn(x)), axis=-1)


def audit(cal, val, **kwargs):
    return audit_map(cal, val, calibration_ids=np.arange(len(cal)),
                     validation_ids=np.arange(len(val))+10000, options=OPTIONS, **kwargs)


def test_monotone_control_does_not_manufacture_critical_points():
    fn = lambda x: .2+.6*x
    result = audit(blocks(fn, 1), blocks(fn, 2))
    assert result["resolved"], result
    assert result["branch_count"] == 1 and result["critical_intervals"] == []


def test_two_critical_cubic_is_recovered_without_a_requested_branch_count():
    fn = lambda x: .5+4*(x-.5)**3-.75*(x-.5)
    result = audit(blocks(fn, 3, 256), blocks(fn, 4, 256))
    assert result["resolved"], result
    assert result["branch_count"] == 3
    assert all(v["heldout_affine_q90_error"] > v["heldout_q90_error"] for v in result["variants"])
    for (lo, hi), expected in zip(result["critical_intervals"], [.25, .75]):
        assert lo-.01 <= expected <= hi+.01 and hi-lo <= .04


def test_multi_valued_holdout_fails_even_when_calibration_is_a_perfect_graph():
    fn = lambda x: .2+.6*x
    cal, val = blocks(fn, 5), blocks(fn, 6)
    val[:, :, 1] += np.where(np.arange(len(val)) % 2, .25, -.25)[:, None]
    result = audit(cal, val)
    assert not result["resolved"]
    assert all(v["reason"] == "held-out graph/support gate failed" for v in result["variants"])


def test_holdout_does_not_change_normalization_or_training_critical_points():
    fn = lambda x: .2+.6*x
    cal, val = blocks(fn, 7), blocks(fn, 8)
    first = audit(cal, val)
    val[:, :, 1] += 1000
    second = audit(cal, val)
    assert first["calibration_bounds"] == second["calibration_bounds"]
    assert [v["critical_points"] for v in first["variants"]] == [v["critical_points"] for v in second["variants"]]
    assert first["resolved"] and not second["resolved"]


def test_few_seed_blocks_are_not_rescued_by_many_correlated_pairs():
    cal = blocks(lambda x: x, 9, 8)
    cal = np.tile(cal, (1, 100, 1))
    result = audit(cal, cal.copy())
    assert not result["resolved"] and result["reason"] == "insufficient independent seeds"


def test_seed_leakage_is_rejected():
    cal = blocks(lambda x: x, 10)
    with pytest.raises(ValueError, match="disjoint"):
        audit_map(cal, cal, calibration_ids=np.arange(128), validation_ids=np.arange(128), options=OPTIONS)


def test_unsupported_interior_gap_is_not_filled_silently():
    cal, val = blocks(lambda x: x, 11, 256), blocks(lambda x: x, 12, 256)
    # Keep 80% of domain, but leave a contiguous unsupported central region.
    for array in (cal, val):
        array[:] = np.where(array < .5, array*.8, .6+(array-.5)*.8)
    result = audit(cal, val)
    assert not result["resolved"]
    assert all(v["reason"] == "unsupported interior gap" for v in result["variants"])


def test_invalid_fraction_and_seed_options_fail():
    cal = blocks(lambda x: x, 13)
    for options in (replace(OPTIONS, minimum_coverage=float("nan")), replace(OPTIONS, bootstrap_samples=0)):
        with pytest.raises(ValueError):
            audit_map(cal, cal, calibration_ids=np.arange(128), validation_ids=np.arange(128)+1000, options=options)


def test_degenerate_target_is_not_a_qualified_partition():
    result = audit(blocks(lambda x: np.zeros_like(x), 14), blocks(lambda x: np.zeros_like(x), 15))
    assert not result["resolved"] and result["reason"] == "degenerate calibration range"


def test_stationary_inflection_is_not_a_turning_branch_boundary():
    fn = lambda x: .5+4*(x-.5)**3
    result = audit(blocks(fn, 16, 512), blocks(fn, 17, 512))
    assert result["resolved"], result
    assert result["branch_count"] == 1 and result["critical_intervals"] == []


def test_failed_bootstrap_replicates_remain_in_consensus_denominator(monkeypatch):
    from butterfly import seed_return_map as module
    original = module._fit
    def failed_resample(blocks, ids, *args):
        result = original(blocks, ids, *args)
        if len(np.unique(ids)) < len(ids):
            return {**result, "resolved": False, "reason": "controlled failed bootstrap"}
        return result
    monkeypatch.setattr(module, "_fit", failed_resample)
    fn = lambda x: .5+4*(x-.5)**3-.75*(x-.5)
    result = audit(blocks(fn, 3, 256), blocks(fn, 4, 256))
    assert not result["resolved"]
    for variant in result["variants"]:
        assert variant["bootstrap_critical_counts"] == [None]*OPTIONS.bootstrap_samples
        assert variant["bootstrap_consensus"] == 0.
        assert variant["reason"] == "seed-block branch stability failed"
