import numpy as np

from scripts.solve_jones_homoclinic_collocation import (
    physical_secant_plane,
    scaled_rossler_flow,
    scaled_rossler_jacobian,
    validate_solver_blocks,
)


def test_physical_secant_plane_places_predictor_at_requested_c_increment():
    previous = np.array([0.1800, 10.0])
    current = np.array([0.1799, 10.001])
    scales = np.array([0.002, 0.004])
    tangent, predictor = physical_secant_plane(previous, current, scales, 0.0002)
    assert np.isclose(np.linalg.norm(tangent), 1.0)
    assert np.isclose(predictor[1], current[1] + 0.0002)
    assert np.isclose(np.dot(tangent, (predictor - predictor) / scales), 0.0)


def test_scaled_rossler_state_jacobian_matches_central_difference():
    states = np.array([[1.0, 2.0], [-0.5, 0.25], [0.1, 0.2]])
    total_time = 3.0
    a_value = 0.18
    b_value = 0.2
    c_value = 10.3
    analytic = scaled_rossler_jacobian(states, total_time, a_value, c_value)
    step = 1e-7
    for component in range(3):
        plus = states.copy()
        minus = states.copy()
        plus[component] += step
        minus[component] -= step
        numeric = (
            scaled_rossler_flow(plus, total_time, a_value, b_value, c_value)
            - scaled_rossler_flow(minus, total_time, a_value, b_value, c_value)
        ) / (2.0 * step)
        assert np.allclose(analytic[:, component], numeric, rtol=1e-8, atol=1e-8)


def test_collocation_manifest_requires_shared_manifold_replay_solver():
    solver = {"method": "Radau", "rtol": 1e-10, "atol": 1e-12, "max_step": 0.05}
    validate_solver_blocks({"solver": solver, "replay": {"solver": solver.copy()}})
