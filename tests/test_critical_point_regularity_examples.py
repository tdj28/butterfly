"""Exact algebraic illustrations, not new numerical flow evidence."""
import pytest
from butterfly.return_image_curve import observe_curve,candidate_intervals


def observe(x,y,dx,dy):
    data = dict(status='returned',events=[
        dict(state=[x,0.,0.],tangent=[dx,0.,0.]),
        dict(state=[y,0.,0.],tangent=[dy,0.,0.])])
    return observe_curve(data,scales=(1.,1.),minimum_gain=1e-4,minimum_x_component=.001)


@pytest.mark.parametrize('orientation',[1.,-1.])
def test_regular_quadratic_fold_has_a_connected_sign_change(orientation):
    rows = [observe(orientation*u,u*u,orientation,2*u) for u in (-.1,0.,.1)]
    assert all(r['valid'] for r in rows)
    assert rows[1]['x_graph_slope'] == 0.
    assert candidate_intervals(rows) == [[0,2]]


def test_zero_numerator_and_denominator_can_describe_a_straight_line():
    k = .25
    rows = [observe(u*u,k*u*u,2*u,2*k*u) for u in (-.1,0.,.1)]
    assert not rows[1]['valid'] and rows[1]['x_graph_slope'] is None
    assert rows[0]['x_graph_slope'] == rows[2]['x_graph_slope'] == k
    assert candidate_intervals(rows) == []


def test_tiny_gain_does_not_make_a_nonzero_graph_slope_critical():
    epsilon,k = 1e-12,.25
    # X=epsilon*u+u^3 and Y=k*X: the exact graph slope is k everywhere.
    rows = [observe(epsilon*u+u**3,k*(epsilon*u+u**3),epsilon+3*u*u,k*(epsilon+3*u*u))
        for u in (-.1,0.,.1)]
    assert not rows[1]['valid']
    assert rows[0]['x_graph_slope'] == rows[2]['x_graph_slope'] == k
    assert candidate_intervals(rows) == []


def test_bad_parameterization_can_hide_a_genuine_fold():
    epsilon = 1e-12
    # X=epsilon*u, Y=X^2. A true quadratic graph is numerically ineligible here.
    rows = [observe(epsilon*u,(epsilon*u)**2,epsilon,2*epsilon**2*u) for u in (-.1,0.,.1)]
    assert all(not r['valid'] for r in rows)
    assert candidate_intervals(rows) == []
