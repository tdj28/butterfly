"""Analytic controls for complete-grid decisions; not Rössler evidence."""
import copy
import json

import numpy as np
import pytest

from butterfly.paired_decisions import (_model, analyze_case, critical_matrix,
                                       joint_primary, primary_keys)
from butterfly.paired_sampling import SECTIONS
from butterfly.seed_return_map import MapOptions, VARIANTS, _fit, audit_map


OPTIONS = MapOptions(minimum_seeds=64, bootstrap_samples=8)
KEYS = primary_keys(["coarse", "fine"], 2)


def blocks(fn, seed):
    x = np.random.Generator(np.random.PCG64(seed)).random((256, 8))
    return np.stack((x, fn(x)), axis=-1)


@pytest.fixture(scope="module")
def cubic():
    fn = lambda x: .5+4*(x-.5)**3-.75*(x-.5)
    cal, val = blocks(fn, 3), blocks(fn, 4)
    args = dict(calibration_ids=np.arange(256), validation_ids=np.arange(256)+256,
                options=OPTIONS)
    audit = audit_map(cal, val, **args, retain_models=True)
    assert audit["resolved"], audit
    return cal, val, args, audit


def grid(audit):
    return {key: copy.deepcopy(audit) for key in KEYS}


def test_model_retention_changes_no_analysis_results_and_roundtrips(cubic):
    cal, val, args, retained = cubic
    plain = audit_map(cal, val, **args)
    stripped = copy.deepcopy(retained)
    for record in stripped["variants"]:
        del record["model"], record["critical_intervals"]
    assert stripped == plain
    # JSON round-trip is the eventual receipt boundary; no pickled fitter.
    retained = json.loads(json.dumps(retained, allow_nan=False))
    lower, upper = retained["calibration_bounds"]
    for record in retained["variants"]:
        fitted = _fit(cal, args["calibration_ids"], (lower, upper-lower),
                      record["bins"], record["smoothing"], OPTIONS)
        restored, occupied = _model(record)
        x = np.linspace(*record["normalized_domain"], 111)
        np.testing.assert_array_equal(restored(x), fitted["spline"](x))
        np.testing.assert_array_equal(restored.derivative()(x), fitted["spline"].derivative()(x))
        np.testing.assert_array_equal(occupied, fitted["occupied"])
        assert len(record["critical_intervals"]) == 2


def test_complete_point_region_matrix_keeps_misses_and_unsupported_points(cubic):
    audits = grid(cubic[3])
    joint = joint_primary(audits, KEYS, {"joint_population_passed": True})
    assert joint["resolved"] and joint["branch_count"] == 3
    points = [.25, .75, .5, -1, 2, .1]
    result = critical_matrix(joint, audits, points)
    assert result["near_every_primary_model"] == [[True, False], [False, True],
        [False, False], [False, False], [False, False], [False, False]]
    assert len(result["models"]) == 20
    assert result["orbit_values"] == points
    for model in result["models"]:
        assert model["slopes"][3:5] == [None, None]
        assert np.asarray(model["normalized_distances"]).shape == (6, 2)
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("kind", ["missing-map", "extra-map", "missing-variant", "empty-variants",
                                 "changed-family", "unresolved-variant"])
def test_incomplete_or_changed_grid_cannot_pass(cubic, kind):
    audits = grid(cubic[3])
    joint = joint_primary(audits, KEYS, {"joint_population_passed": True})
    if kind == "missing-map":
        del audits[KEYS[0]]
    elif kind == "extra-map":
        audits["other"] = copy.deepcopy(cubic[3])
    elif kind == "missing-variant":
        audits[KEYS[0]]["variants"].pop()
    elif kind == "empty-variants":
        audits[KEYS[0]]["variants"] = []
    elif kind == "changed-family":
        audits[KEYS[0]]["variants"][0]["bins"] += 1
    else:
        audits[KEYS[0]]["variants"][0]["resolved"] = False
    with pytest.raises(ValueError):
        critical_matrix(joint, audits, [.25, .75])


def test_failed_population_or_primary_cannot_be_rescued(cubic):
    audits = grid(cubic[3])
    failed = joint_primary(audits, KEYS, {"joint_population_passed": False})
    assert not failed["resolved"]
    assert critical_matrix(failed, audits, None)["status"] == "not-evaluated"
    audits[KEYS[0]]["resolved"] = False
    assert not joint_primary(audits, KEYS, {"joint_population_passed": True})["resolved"]


@pytest.mark.parametrize("kind", ["count", "wide", "overlap"])
def test_disagreement_is_reported_not_best_fit_selected(cubic, kind):
    audits = grid(cubic[3])
    if kind == "count":
        audits[KEYS[0]]["branch_count"] = 2
    elif kind == "wide":
        audits[KEYS[0]]["critical_intervals"][0][0] -= .1
    else:
        audits[KEYS[0]]["critical_intervals"][0][1] = .8
    assert not joint_primary(audits, KEYS, {"joint_population_passed": True})["resolved"]


def test_monotone_map_is_not_a_criticality_claim():
    fn = lambda x: .2+.6*x
    audit = audit_map(blocks(fn, 1), blocks(fn, 2), calibration_ids=np.arange(256),
        validation_ids=np.arange(256)+256, options=OPTIONS, retain_models=True)
    audits = grid(audit)
    joint = joint_primary(audits, KEYS, {"joint_population_passed": True})
    assert joint["resolved"] and joint["branch_count"] == 1
    result = critical_matrix(joint, audits, [.25, .75])
    assert result["status"] == "no-turning-regions"
    assert result["near_every_primary_model"] == [[], []]


@pytest.mark.parametrize("kind", ["knots", "coefficients", "occupied", "degree", "intervals"])
def test_invalid_retained_model_cannot_produce_proximity(cubic, kind):
    audits = grid(cubic[3])
    joint = joint_primary(audits, KEYS, {"joint_population_passed": True})
    record = audits[KEYS[0]]["variants"][0]
    if kind in ("knots", "coefficients"):
        record["model"][kind][0] = float("nan")
    elif kind == "occupied":
        record["model"]["occupied_bins"] = [True]
    elif kind == "degree":
        record["model"]["degree"] = 2
    else:
        record["critical_intervals"] = []
    with pytest.raises(ValueError):
        critical_matrix(joint, audits, [.25, .75])


def test_all_projections_run_but_good_diagnostic_never_rescues_primary(cubic):
    cal, val, _, _ = cubic
    pairs = np.concatenate([cal, val])
    states = np.zeros((512, 2, 8, 2, 3))
    states[..., 2] = pairs[:, None]  # good diagnostic z
    ids = np.arange(512)
    profiles = {name: {"global_seed_ids": ids, "windows": np.array([[0, 8], [8, 16]]),
        "pair_states": {section: states.copy() for section in SECTIONS}} for name in ("coarse", "fine")}
    cohort = {"global_seed_ids": ids, "calibration": ids < 256, "validation": ids >= 256,
              "joint_population_passed": True}
    result = analyze_case(profiles, ["coarse", "fine"], cohort,
        primary={"section": SECTIONS[0], "axis": 0},
        diagnostics=[{"section": SECTIONS[0], "axis": 2}, {"section": SECTIONS[1], "axis": 2}],
        options=OPTIONS)
    assert not result["joint_primary"]["resolved"] and not result["historical_symbols_verified"]
    assert len(result["projections"]) == 3
    for projection in result["projections"][1:]:
        assert len(projection["audits"]) == 4
        assert all(a["resolved"] for a in projection["audits"].values())
