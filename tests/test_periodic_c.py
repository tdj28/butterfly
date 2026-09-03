from __future__ import annotations

import numpy as np

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.periodic_c import (
    _flow_transition_c_sensitivity,
    extended_shooting_jacobian_c,
)


SOLVER = SolverConfig(method="DOP853", rtol=1e-11, atol=1e-13, max_step=0.02)
PARAMETERS = RosslerParameters(a=0.1798, b=0.2, c=3.18)


def test_flow_c_sensitivity_matches_centered_difference() -> None:
    state = np.asarray((-4.5, -0.44, 0.026))
    duration = 0.31
    endpoint, transition, sensitivity = _flow_transition_c_sensitivity(
        state, duration, PARAMETERS, SOLVER
    )
    epsilon = 2e-6
    plus = RosslerParameters(a=PARAMETERS.a, b=PARAMETERS.b, c=PARAMETERS.c + epsilon)
    minus = RosslerParameters(a=PARAMETERS.a, b=PARAMETERS.b, c=PARAMETERS.c - epsilon)
    plus_endpoint = _flow_transition_c_sensitivity(state, duration, plus, SOLVER)[0]
    minus_endpoint = _flow_transition_c_sensitivity(state, duration, minus, SOLVER)[0]
    numerical = (plus_endpoint - minus_endpoint) / (2.0 * epsilon)
    np.testing.assert_allclose(sensitivity, numerical, rtol=2e-7, atol=2e-9)
    assert np.all(np.isfinite(endpoint))
    assert np.all(np.isfinite(transition))


def test_extended_shooting_c_jacobian_matches_centered_difference() -> None:
    variables = np.asarray((-4.5, -0.44, 0.026, 0.31, PARAMETERS.c))
    phase = rossler_rhs(0.0, variables[:3], PARAMETERS)
    phase /= np.linalg.norm(phase)

    def residual(value: np.ndarray) -> np.ndarray:
        parameters = RosslerParameters(a=PARAMETERS.a, b=PARAMETERS.b, c=value[4])
        endpoint = _flow_transition_c_sensitivity(
            value[:3], value[3], parameters, SOLVER
        )[0]
        return np.r_[endpoint - value[:3], np.dot(phase, value[:3] - variables[:3])]

    analytic = extended_shooting_jacobian_c(
        variables,
        a=PARAMETERS.a,
        b=PARAMETERS.b,
        phase_direction=phase,
        solver=SOLVER,
    )
    epsilon = 2e-6
    numerical = np.empty_like(analytic)
    for index in range(len(variables)):
        offset = np.eye(len(variables))[index] * epsilon
        numerical[:, index] = (
            residual(variables + offset) - residual(variables - offset)
        ) / (2.0 * epsilon)
    np.testing.assert_allclose(analytic, numerical, rtol=3e-7, atol=3e-9)
