import numpy as np
import pytest
from scripts import run_exp484_return_geometry as r


def blocks():
    states = np.zeros((3, 4, 2, 3))
    states[:, :, :, 0] = np.array([[.1, .4, .6, .9], [.2, .3, .7, .8], [.05, .45, .55, .95]])[:, :, None]
    times = np.broadcast_to(np.array([1., 2.]), (3, 4, 2)).copy()
    return states, times


def test_selection_uses_only_calibration_and_preserves_actual_state():
    states, times = blocks()
    chosen = r.select_points(np.array([0, 1, 2]), np.array([False, True, True]), states, times, [0, 1], bins=4)
    assert [x["global_seed_id"] for x in chosen] == [1]*4
    assert [x["stratum"] for x in chosen] == [0, 1, 2, 3]
    assert chosen[0]["initial_state"] == states[1, 0, 0].tolist()


def test_missing_bin_fails_not_interpolates_or_substitutes():
    states, times = blocks()
    with pytest.raises(ValueError, match="no original"):
        r.select_points(np.arange(3), np.ones(3, bool), states, times, [0, 2], bins=4)


def test_duplicate_ids_and_nonfinite_calibration_rejected():
    states, times = blocks()
    with pytest.raises(ValueError, match="invalid"):
        r.select_points(np.array([0, 0, 2]), np.ones(3, bool), states, times, [0, 1], bins=4)
    states[0, 0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="invalid"):
        r.select_points(np.arange(3), np.ones(3, bool), states, times, [0, 1], bins=4)


def test_scaled_jacobian_and_relative_error():
    result = r.scaled_jacobian(np.array([[1., 2.], [3., 4.]]), np.array([10., 2.]))
    np.testing.assert_allclose(result, [[1., .4], [15., 4.]])
    assert r.relative_error(result, result) == 0
    assert r.relative_error(np.ones((2, 2)), np.zeros((2, 2))) == 1


def test_missing_return_never_qualifies():
    plan = dict(thresholds={}, section_coordinate_scales=[15, .01])
    result = r.analyze_point({}, {"DOP853": dict(status="no-return")}, {}, plan)
    assert result["passed"] is False and result["reason"] == "missing base return"


def test_wrong_campaign_anchor_rejected_before_target_call(tmp_path, monkeypatch):
    (tmp_path/"campaign").mkdir()
    (tmp_path/"campaign/receipt.json").write_text("{}")
    monkeypatch.setattr(r, "RUN", tmp_path)
    monkeypatch.setattr(r, "first_return_geometry", lambda *a, **k: pytest.fail("target entered before integrity gate"))
    with pytest.raises(ValueError, match="campaign anchor"):
        r.prepare(dict(campaign_sha256=r.CAMPAIGN_SHA))


def test_analytic_controls_pass_both_solvers():
    plan = dict(solvers=["DOP853", "Radau"], rtol=1e-10, atol=1e-12, max_step=.02)
    assert all(row["passed"] for row in r.controls(plan))


def test_missing_perturbed_return_and_failed_numerical_comparison_are_retained():
    base = dict(status="returned", return_time=1., return_state=np.array([1., 0., 2.]), return_jacobian=np.eye(2))
    plan = dict(solvers=["DOP853", "Radau"], section_coordinate_scales=[15, .01],
        thresholds={key: 1e-6 for key in ("solver_scaled_state_error", "solver_return_time_error",
            "solver_relative_scaled_jacobian_error", "finite_difference_relative_scaled_jacobian_error",
            "saved_pair_scaled_state_error", "saved_pair_return_time_error")})
    point = dict(saved_next_state=[1., 0., 2.], saved_pair_times=[1., 2.])
    row = r.analyze_point(point, {"DOP853": base, "Radau": base}, {1e-5: {(0, -1): dict(status="no-return")}}, plan)
    assert not row["passed"] and not row["checks"]["finite_difference"]
    row = r.analyze_point(point, {"DOP853": base, "Radau": dict(base, return_time=2.)}, {}, plan)
    assert not row["passed"] and not row["checks"]["solver_time"]
