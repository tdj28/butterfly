import numpy as np
import pytest

from butterfly.transported_tangent import dominant_history, assess_direction, line_angle
from scripts.run_exp485_transported_tangent import extract_history


def test_chronological_left_direction():
    a = np.array([[2., 3.], [0., .01]])
    b = np.array([[0., -.01], [2., 0.]])
    rows = dominant_history([a, b], depths=(1, 2))
    expected = np.linalg.svd(b @ a)[0][:, 0]
    assert line_angle(rows[-1]["direction"], expected) < 1e-14
    assert line_angle(rows[-1]["direction"], np.linalg.svd(a @ b)[0][:, 0]) > 1


@pytest.mark.parametrize("scale", [1., -1., 1e200, 1e-200])
def test_product_rescaling(scale):
    h = dominant_history([scale*np.diag([2., .1])]*8)
    assert line_angle(h[-1]["direction"], [1., 0.]) == 0
    assert h[-1]["singular_ratio"] == pytest.approx(.05**8)


def assess(h, other=None, j=None):
    return assess_direction(dict(a=h, b=h if other is None else other),
                            dict(a=np.eye(2) if j is None else j, b=np.eye(2) if j is None else j))


def test_positive_and_isotropic_negative():
    assert assess(dominant_history([np.diag([2., .1])]*8))["direction_consistent"]
    assert not assess(dominant_history([np.eye(2)]*8))["direction_consistent"]


def test_vertical_no_fake_graph_slope():
    result = assess(dominant_history([np.diag([.1, 2.])]*8))
    assert result["direction_consistent"]
    assert result["projected"]["a"]["x_graph_derivative"] is None


def test_history_and_solver_disagreement():
    h = dominant_history([np.diag([2., .1])]*8)
    other = [dict(row) for row in h]
    other[-1]["direction"] = [0., 1.]
    result = assess(h, other)
    assert not result["checks"]["history_agreement"]
    assert not result["checks"]["solver_agreement"]


def test_curve_derivative_not_partial_and_sign_invariance():
    v = np.array([1., 2.])/np.sqrt(5)
    rotation = np.column_stack([v, [-v[1], v[0]]])
    h = dominant_history([rotation @ np.diag([2., .001]) @ rotation.T]*8)
    result = assess(h, j=np.array([[3., 4.], [0., 1.]]))
    assert result["projected"]["a"]["x_graph_derivative"] == pytest.approx(11.)
    assert result["projected"]["a"]["coordinate_partial"] == 3
    assert line_angle(v, -v) < 1e-15


@pytest.mark.parametrize("matrices", [np.zeros((8, 2, 2)), np.full((8, 2, 2), np.nan), np.zeros((2, 3, 3))])
def test_invalid_derivatives(matrices):
    with pytest.raises(ValueError):
        dominant_history(matrices)


def fixture_events():
    return dict(global_seed_ids=np.array([4, 4, 4, 4, 4, 4]), times=np.arange(6.),
                states=np.column_stack([np.arange(6.), np.zeros(6), np.ones(6)]),
                accepted=np.array([True, False, True, True, True, True]),
                gate_unresolved=np.zeros(6, bool), orientation_unresolved=np.zeros(6, bool))


def test_exact_predecessors_skip_only_rejected_gates():
    e = fixture_events()
    p = dict(global_seed_id=4, saved_pair_times=[4., 5.], initial_state=e["states"][4])
    h = extract_history(e, p, 3)
    assert h["raw_indices"] == [0, 2, 3, 4]


@pytest.mark.parametrize("problem", ["missing", "ambiguous", "state", "time"])
def test_bad_history_is_not_replaced(problem):
    e = fixture_events()
    p = dict(global_seed_id=4, saved_pair_times=[4., 5.], initial_state=e["states"][4].copy())
    depth = 3
    if problem == "missing":
        depth = 4
    elif problem == "ambiguous":
        e["gate_unresolved"][5] = True
    elif problem == "state":
        p["initial_state"][0] += 1
    else:
        e["times"][2] = 0
    with pytest.raises(ValueError):
        extract_history(e, p, depth)


def synthetic_analysis():
    import json
    from scripts.run_exp485_transported_tangent import PLAN
    plan = json.loads(PLAN.read_bytes())
    states = np.column_stack([np.arange(9.), np.zeros(9), np.ones(9)])
    point = dict(history=dict(states=states, times=np.arange(9.)))
    segments = [{m: dict(status="returned", return_state=states[i+1].copy(), return_time=1.,
                         return_jacobian=np.diag([2., .1])) for m in plan["solvers"]} for i in range(8)]
    endpoints = {m: dict(return_jacobian=np.eye(2)) for m in plan["solvers"]}
    return point, segments, endpoints, plan


def test_complete_analysis_and_both_saved_solver_checks():
    from scripts.run_exp485_transported_tangent import analyze
    point, segments, endpoints, plan = synthetic_analysis()
    assert analyze(point, segments, endpoints, plan)["qualified"]
    # A common solver bias must fail even when the two solvers agree.
    for m in plan["solvers"]:
        segments[3][m]["return_state"][0] += .01
    result = analyze(point, segments, endpoints, plan)
    assert not result["qualified"]
    assert not result["geometry"][3]["forward"]["checks"]["saved_pair_state"]
    assert not result["geometry"][3]["reverse"]["checks"]["saved_pair_state"]


def test_missing_return_is_unresolved():
    from scripts.run_exp485_transported_tangent import analyze
    point, segments, endpoints, plan = synthetic_analysis()
    segments[3]["Radau"] = dict(status="no-return")
    result = analyze(point, segments, endpoints, plan)
    assert not result["qualified"] and result["direction"] is None
