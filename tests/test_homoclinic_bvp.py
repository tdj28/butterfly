"""Analytic controls for the independent endpoint-projection formulation."""

import numpy as np
import pytest

from butterfly.homoclinic_bvp import (
    ParameterBox, ProjectionBoundary, duffing_homoclinic, duffing_model,
    duffing_seed, local_replay_defects, projection_complements,
    rossler_bvp_model, solve_projected_homoclinic,
)


def duffing_trial(radius, tolerance=1e-7):
    mesh, guess, duration = duffing_seed(radius)
    result, summary = solve_projected_homoclinic(
        duffing_model(), mesh, guess, parameter=0.002, flight_time=duration,
        radii=(radius, radius), box=ParameterBox((-0.1, duration * 0.8), (0.1, duration * 1.2)),
        tolerance=tolerance, boundary_tolerance=1e-9, maximum_nodes=5000,
    )
    return result, summary


def test_nonnormal_projection_uses_complements_not_opposite_right_eigenvectors():
    jacobian = np.asarray(((1.0, 4.0), (0.0, -2.0)))
    left, right = projection_complements(jacobian)
    unstable = np.asarray((1.0, 0.0))
    stable = np.asarray((-4.0 / 3.0, 1.0))
    np.testing.assert_allclose(left.T @ unstable, 0.0, atol=1e-14)
    np.testing.assert_allclose(right.T @ stable, 0.0, atol=1e-14)
    assert abs(np.dot(unstable, stable)) > 1.0


def test_parameter_box_keeps_extreme_iterates_inside_physical_domain():
    box = ParameterBox((0.17, 60.0), (0.19, 200.0))
    for transformed in ([0.0, 0.0], [-1000.0, 1000.0], [1000.0, -1000.0]):
        physical, derivative = box.decode(transformed)
        assert np.all(physical >= box.lower) and np.all(physical <= box.upper)
        assert np.all(np.isfinite(derivative))
    np.testing.assert_allclose(box.decode(box.encode((0.18, 100.0)))[0], (0.18, 100.0))


@pytest.mark.parametrize("radius", [0.1, 0.05, 0.025])
def test_projected_bvp_recovers_analytic_duffing_homoclinic(radius):
    result, summary = duffing_trial(radius)
    assert result is not None
    assert summary["passed_numerical_gates"]
    assert abs(summary["parameter"]) < 1e-8
    np.testing.assert_allclose(summary["endpoint_radii"], radius, atol=1e-10)
    assert summary["maximum_excursion"] > 1.4
    points = np.linspace(0.0, 1.0, 501)
    exact = duffing_homoclinic((points - 0.5) * summary["flight_time"])
    error = np.max(np.linalg.norm(result.sol(points) - exact, axis=0))
    # Linear eigenspace endpoints are a finite-radius approximation, not exact
    # points of the nonlinear homoclinic. This budget vanishes with radius.
    assert error < radius**2
    replay = local_replay_defects(duffing_model(), result, summary["parameter"], summary["flight_time"], segments=16)
    assert replay["success"] and replay["maximum_state_defect"] < 1e-6


def test_duffing_endpoint_truncation_error_decreases_under_radius_halving():
    errors = []
    for radius in (0.1, 0.05, 0.025):
        result, summary = duffing_trial(radius)
        assert summary["passed_numerical_gates"]
        points = np.linspace(0.0, 1.0, 1001)
        exact = duffing_homoclinic((points - 0.5) * summary["flight_time"])
        errors.append(float(np.max(np.linalg.norm(result.sol(points) - exact, axis=0))))
    assert errors[1] < 0.4 * errors[0]
    assert errors[2] < 0.4 * errors[1]


def test_equilibrium_collapse_cannot_satisfy_projection_radius_gauges():
    model = duffing_model()
    boundary = ProjectionBoundary(model, 0.0, (0.05, 0.05))
    residual = boundary.residual(np.zeros(2), np.zeros(2), 0.0)
    np.testing.assert_array_equal(residual[-2:], (-0.5, -0.5))


def test_duffing_negative_control_rejects_box_excluding_zero_damping():
    mesh, guess, duration = duffing_seed(0.05)
    _result, summary = solve_projected_homoclinic(
        duffing_model(), mesh, guess, parameter=0.05, flight_time=duration,
        radii=(0.05, 0.05), box=ParameterBox((0.03, duration * 0.8), (0.07, duration * 1.2)),
        tolerance=1e-7, boundary_tolerance=1e-9, maximum_nodes=5000,
    )
    # H'=damping*y^2 excludes nontrivial homoclinics for positive damping.
    assert not summary["passed_numerical_gates"]


def test_domain_violation_produces_failure_receipt():
    mesh, values, duration = duffing_seed(0.05)
    result, summary = solve_projected_homoclinic(
        duffing_model(), mesh, values, parameter=0.0, flight_time=duration,
        radii=(0.05, 0.05), box=ParameterBox((-0.1, 1.0), (0.1, 20.0)),
        maximum_state_norm=0.1,
    )
    assert result is None
    assert not summary["passed_numerical_gates"]
    assert "finite domain" in summary["message"]


def test_independent_rossler_field_and_jacobian_match_finite_difference():
    model = rossler_bvp_model(0.2, 10.3084)
    states = np.asarray(((0.5, -1.0), (0.2, 2.0), (0.4, 0.01)))
    a = 0.1826
    analytic = model.state_jacobian(states, a)
    step = 1e-6
    for index in range(3):
        perturbation = np.zeros_like(states)
        perturbation[index] = step
        observed = (model.field(states + perturbation, a) - model.field(states - perturbation, a)) / (2 * step)
        np.testing.assert_allclose(observed, analytic[:, index], rtol=1e-8, atol=1e-9)
    np.testing.assert_allclose(model.field(model.equilibrium(a)[:, None], a), 0.0, atol=1e-15)
