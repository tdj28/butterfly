"""Analytic controls, not target-system outcomes or symbolic labels."""
import numpy as np
import pytest
from butterfly.poincare import PoincareSection
from butterfly.return_geometry import event_corrected_tangent, first_return_geometry


SECTION = PoincareSection((0., 1., 0.), 0., direction=-1)


def rhs(_t, q):
    return np.array([-q[1], q[0], -.3*q[2]])


def jac(_t, _q):
    return np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., -.3]])


@pytest.mark.parametrize("method", ["DOP853", "Radau"])
def test_analytic_rotation_contraction_return_and_derivative(method):
    result = first_return_geometry(rhs, jac, [-1., 0., .2], SECTION, method=method, horizon=7., max_step=.04)
    decay = np.exp(-.3*2*np.pi)
    assert result["status"] == "returned"
    assert result["selected_event"] == 1  # initial root retained, not misread as a return
    assert abs(result["return_time"]-2*np.pi) < 1e-9
    np.testing.assert_allclose(result["return_state"], [-1., 0., .2*decay], atol=1e-10)
    np.testing.assert_allclose(result["return_jacobian"], np.diag([1., decay]), atol=1e-9)
    np.testing.assert_allclose(result["return_time_gradient"], 0, atol=1e-9)


def test_time_correction_removes_normal_sensitivity():
    tangent = np.array([[2., 3.], [4., 6.], [5., 7.]])
    field = np.array([1., -2., 3.])
    normal = np.array([0., 1., 0.])
    corrected, time_gradient = event_corrected_tangent(tangent, field, normal)
    np.testing.assert_allclose(normal @ corrected, 0, atol=1e-15)
    np.testing.assert_allclose(time_gradient, [2., 3.])
    np.testing.assert_allclose(corrected, tangent+np.outer(field, [2., 3.]))


def test_normal_rescaling_does_not_change_event_correction():
    tangent = np.arange(6.).reshape(3, 2)
    a = event_corrected_tangent(tangent, [1, 2, 3], [0, 1, 0])
    b = event_corrected_tangent(tangent, [1, 2, 3], [0, -20, 0])
    for left, right in zip(a, b):
        np.testing.assert_allclose(left, right)


@pytest.mark.parametrize("field", [[0, 0, 0], [1, 1e-12, 2]])
def test_zero_velocity_and_near_grazing_are_rejected(field):
    with pytest.raises(ValueError, match="transverse"):
        event_corrected_tangent(np.eye(3)[:, [0, 2]], field, [0, 1, 0])


def test_no_return_remains_missing_not_identity():
    result = first_return_geometry(rhs, jac, [-1., 0., .2], SECTION, horizon=1.)
    assert result["status"] == "no-return" and "return_jacobian" not in result


def test_off_section_or_wrong_orientation_rejected():
    with pytest.raises(ValueError, match="section"):
        first_return_geometry(rhs, jac, [-1., .01, .2], SECTION)
    with pytest.raises(ValueError, match="orientation"):
        first_return_geometry(rhs, jac, [1., 0., .2], SECTION)


def test_gate_rejects_invalid_initial_state():
    section = PoincareSection((0., 1., 0.), 0., direction=-1, gate_axis=0, gate_upper=-2.)
    with pytest.raises(ValueError, match="initial"):
        first_return_geometry(rhs, jac, [-1., 0., .2], section)


def test_nonfinite_jacobian_stops_collection():
    with pytest.raises(ValueError, match="Jacobian"):
        first_return_geometry(rhs, lambda t, q: np.full((3, 3), np.nan), [-1., 0., .2], SECTION)
