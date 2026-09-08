import copy
import json

import numpy as np
import pytest

from scripts import run_exp486_return_image_folds as run


def plan():
    return json.loads(run.PLAN.read_bytes())


def synthetic(u, *, derivative=None):
    derivative = 2*u if derivative is None else derivative
    result = dict(status="returned", events=[
        dict(state=[u, 0., 0.], tangent=[1., 0., 0.], time=1.),
        dict(state=[u*u, 0., 0.], tangent=[derivative, 0., 0.], time=2.)])
    return {m: copy.deepcopy(result) for m in ("DOP853", "Radau")}


def test_full_grid_exact_zero_and_two_step_fd():
    seen = []
    def evaluate(u):
        seen.append(u)
        return synthetic(u)
    result = run.family_analysis(dict(grid=[-.1, 0., .1]), evaluate, plan(), scales=(1., 1.))
    assert result["qualified"]
    assert result["candidate_intervals"] == [[0, 2]]
    assert result["roots"][0]["u"] == 0.
    assert all(r["passed"] for r in result["finite_difference"])
    assert len(seen) == len(set(seen)) == 7


def test_invalid_bracket_interior_is_retained_not_bridged():
    def evaluate(u):
        result = synthetic(u)
        if u == 0:
            result["Radau"]["status"] = "unresolved"
        return result
    result = run.family_analysis(dict(grid=[-.1, .1]), evaluate, plan(), scales=(1., 1.))
    assert not result["qualified"]
    assert result["roots"][0]["status"] == "unresolved"
    assert "invalid interior" in result["roots"][0]["reason"]


def test_solver_disagreement_or_wrong_tangent_fails():
    def evaluate(u):
        result = synthetic(u)
        result["Radau"]["events"][-1]["state"][0] += .001
        return result
    result = run.family_analysis(dict(grid=[-.1, 0., .1]), evaluate, plan(), scales=(1., 1.))
    assert not result["qualified"]
    assert not result["numerical_checks_passed"]
    result = run.family_analysis(dict(grid=[-.1, 0., .1]), lambda u: synthetic(u, derivative=1.), plan(), scales=(1., 1.))
    assert not result["numerical_checks_passed"]


def test_excessive_brackets_no_favorite_selection():
    result = run.family_analysis(dict(grid=[-2., -1., 1., 2.]),
        lambda u: synthetic(u, derivative=u*(u*u-2)), plan(), scales=(1., 1.))
    assert len(result["candidate_intervals"]) == 3
    assert result["excessive_brackets"] and not result["roots"]
    assert not result["qualified"]


def test_out_of_region_root_retained_but_not_qualified():
    result = run.family_analysis(dict(grid=[-.1, 0., .1], old_x_interval=[1., 2.]), synthetic, plan(), scales=(1., 1.))
    assert result["roots"][0]["status"] == "qualified"
    assert not result["roots"][0]["in_region"]
    assert not result["qualified"]


def test_saved_anchor_checks_cannot_be_skipped():
    result = run.family_analysis(dict(grid=[-.1, 0., .1], expected_states=[[1., 0., 0.], [0., 0., 0.]], expected_times=[1., 2.]), synthetic, plan(), scales=(1., 1.))
    assert not result["qualified"]
    assert len(result["anchor_checks"]) == 4


def test_all_distinct_root_states_count_in_spread():
    assert run.state_spread([[1., 0., .01], [1., 0., .03]], [15., .01]) == pytest.approx(2.)


def test_declared_matrix_and_worst_case_budget():
    p = plan()
    assert p["cases"] == ["local-a025-c083", "local-a027-c083"]
    assert p["regions"] == [[0, 1], [16, 17]]
    assert p["depths"] == [4, 8]
    assert p["solvers"] == ["DOP853", "Radau"]
    assert p["grid_points"] == 17
    assert np.allclose(p["normalized_directions"], [[1, 0], [2**-.5, 2**-.5]], atol=1e-15)
    maximum = 16*2*(17+4+2*50)
    assert maximum == 3872 < p["limits"]["maximum_target_integrations"]
