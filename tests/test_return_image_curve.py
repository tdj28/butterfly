import numpy as np
import pytest

from butterfly.poincare import PoincareSection
from butterfly.return_image_curve import image_returns, observe_curve, candidate_intervals


def control_field(k=1., decay=.03):
    def rhs(t, q):
        x, y, z = q
        return np.array([-y-2*k*decay*z*z, x-k*z*z, -decay*z])
    def jac(t, q):
        z = q[2]
        return np.array([[0., -1., -4*k*decay*z], [1., 0., -2*k*z], [0., 0., -decay]])
    return rhs, jac


@pytest.mark.parametrize("method", ["DOP853", "Radau"])
@pytest.mark.parametrize("depth", [4, 8])
def test_known_continuous_image_fold(method, depth):
    decay = .03
    u = 1/(2*(1-np.exp(-2*decay*2*np.pi*(depth+1))))-.5
    q = np.array([-4.+u, 0., .5+u])
    result = image_returns(*control_field(decay=decay), q, [1., 0., 1.],
                           PoincareSection((0., 1., 0.), 0., -1), count=depth+1, method=method)
    assert result["status"] == "returned"
    assert len(result["events"]) == depth+1
    for n, row in enumerate(result["events"], 1):
        rho = np.exp(-decay*2*np.pi*n)
        expected = [q[0]-q[2]**2*(1-rho*rho), 0., q[2]*rho]
        tangent = [1-2*q[2]*(1-rho*rho), 0., rho]
        assert np.max(np.abs(np.array(row["state"])-expected)) < 1e-8
        assert np.max(np.abs(np.array(row["tangent"])-tangent)) < 1e-8
        assert abs(row["time"]-n*2*np.pi) < 1e-8
    observation = observe_curve(result, scales=(1., 1.))
    assert observation["valid"]
    assert abs(observation["x_graph_slope"]) < 1e-7


def test_no_fold_and_projection_degenerate_controls():
    section = PoincareSection((0., 1., 0.), 0., -1)
    no_fold = image_returns(*control_field(k=0.), [-4., 0., .5], [1., 0., 1.], section, count=5)
    assert observe_curve(no_fold, scales=(1., 1.))["x_graph_slope"] == pytest.approx(1., abs=1e-9)
    degenerate = image_returns(*control_field(), [-4., 0., 0.], [0., 0., 1.], section, count=5)
    assert not observe_curve(degenerate, scales=(1., 1.))["valid"]


def test_missing_returns_do_not_become_success():
    result = image_returns(*control_field(), [-4., 0., .5], [1., 0., 1.],
                           PoincareSection((0., 1., 0.), 0., -1), count=5, time_per_return=.2)
    assert result["status"] == "unresolved"
    assert result["events"] == []


def test_rejected_gate_is_not_silently_skipped():
    # For k=-1 the return x rises past the gate after the accepted initial point.
    section = PoincareSection((0., 1., 0.), 0., -1, gate_axis=0, gate_upper=-4.1)
    result = image_returns(*control_field(k=-1.), [-4.2, 0., 1.], [1., 0., 0.], section, count=5)
    assert result["status"] == "unresolved"
    assert any(not r["accepted"] for r in result["events"])


@pytest.mark.parametrize("change", ["orientation", "tangent", "count"])
def test_initial_contract_rejects_invalid_inputs(change):
    q, tangent, count = [-4., 0., .5], [1., 0., 1.], 5
    if change == "orientation":
        q[0] = 4.
    elif change == "tangent":
        tangent[1] = 1.
    else:
        count = 0
    with pytest.raises(ValueError):
        image_returns(*control_field(), q, tangent, PoincareSection((0., 1., 0.), 0., -1), count=count)


def obs(slope, tangent=1., valid=True):
    return dict(x_graph_slope=slope, input_x_tangent=tangent, valid=valid)


def test_all_sign_changes_and_exact_zero():
    assert candidate_intervals([obs(1), obs(-1), obs(-2), obs(1)]) == [[0, 1], [2, 3]]
    assert candidate_intervals([obs(1), obs(0), obs(-1)]) == [[0, 2]]
    assert candidate_intervals([obs(1), obs(0), obs(1)]) == []


def test_input_projection_turn_and_missing_gap_are_not_folds():
    assert candidate_intervals([obs(1, 1), obs(-1, -1)]) == []
    assert candidate_intervals([obs(1), obs(None, valid=False), obs(-1)]) == []
