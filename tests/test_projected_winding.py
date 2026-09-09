"""Analytic geometric controls for a prospective saved-trajectory diagnostic."""
import numpy as np
import pytest

from butterfly.projected_winding import hermite,polygon_measure,window_nodes,compare_polygons


@pytest.mark.parametrize("turns",[-2,-1,0,1,2])
def test_known_circle_winding(turns):
    t = np.linspace(.3,.3+2*np.pi*turns,101)
    r = polygon_measure(np.column_stack([np.cos(t),np.sin(t)]))
    assert r["qualified"] and r["cut_index"] == turns
    assert r["angle_change"] == pytest.approx(2*np.pi*turns,abs=1e-13)


def test_origin_and_near_origin_are_not_assigned_valid_winding():
    assert not polygon_measure([[1,0],[-1,0]])["qualified"]
    assert polygon_measure([[1,0],[-1,0]])["cut_index"] is None
    assert not polygon_measure([[1,1e-12],[-1,1e-12]])["qualified"]
    assert not polygon_measure([[0,0],[1,1]])["qualified"]


def test_antipodal_undersampling_rejected():
    assert not polygon_measure([[1,0],[-1,.01]])["qualified"]


def test_hermite_reproduces_known_cubic_and_rejects_extrapolation():
    q = lambda t:np.array([t**3,2*t*t,3*t])
    f = lambda t:np.array([3*t*t,4*t,3.])
    np.testing.assert_allclose(hermite(0.,1.,q(0),q(1),f(0),f(1),.3),q(.3),atol=1e-15)
    with pytest.raises(ValueError):
        hermite(0.,1.,q(0),q(1),f(0),f(1),1.1)


@pytest.mark.parametrize("height",[-1e-5,1e-5])
def test_open_parabolic_arc_and_extremum_recovery(height):
    # Ordinary two-endpoint mesh misses the small upper detour for height>0.
    q = lambda t:np.array([-t,height-.5*t*t,7.])
    field = lambda t,state:np.array([-1.,-t,0.])
    t = np.array([-.1,.1])
    nodes = window_nodes(t,np.array([q(v) for v in t]),[dict(time=0.,state=q(0).tolist())],field,-.05,.05)
    r = compare_polygons(nodes,[0.,0.])
    assert r["qualified"]
    assert r["measures"]["extrema_augmented"]["cut_index"] == (1 if height > 0 else 0)
    assert r["measures"]["raw"]["cut_index"] == 0
    assert r["refinement_angle_error"] < 1e-13
    assert abs(r["measures"]["extrema_augmented"]["angle_change"]/(2*np.pi)) < .6
    expected = (np.pi if height > 0 else -np.pi)+2*np.arctan((.00125-height)/.05)
    assert r["measures"]["midpoint_enriched"]["angle_change"] == pytest.approx(expected,abs=1e-13)


def test_same_3d_height_does_not_mean_equilibrium_contact():
    q = [[1.,-1.,13.],[0.,1e-5,13.],[-1.,-1.,13.]]
    assert polygon_measure(np.array(q)[:,:2])["qualified"]
    assert min(np.linalg.norm(v) for v in q) >= 13.


@pytest.mark.parametrize("bad",[[[1.,0.]],[[float("nan"),0.],[1.,1.]],[[1.,0.,0.],[0.,1.,0.]]])
def test_malformed_polygon_rejected(bad):
    with pytest.raises(ValueError):
        polygon_measure(bad)
