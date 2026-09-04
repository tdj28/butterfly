from __future__ import annotations

import numpy as np
from types import SimpleNamespace

import pytest

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.periodic_c import (
    _flow_transition_c_sensitivity,
    correct_arclength_c,
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


@pytest.mark.parametrize("failed_equation", ["phase", "arclength"])
def test_arclength_corrector_requires_all_equations_to_pass(
    monkeypatch: pytest.MonkeyPatch, failed_equation: str
) -> None:
    # Exact periodic circle in the invariant z=0 plane for a=b=0.
    variables = np.asarray((1.0, 0.0, 0.0, 2.0 * np.pi, 1.0))
    predictor = variables.copy()
    reference = variables[:3].copy()
    if failed_equation == "phase":
        reference[1] += 0.01
    else:
        predictor[4] += 0.01
    tangent = np.asarray((0.0, 0.0, 0.0, 0.0, 1.0))
    monkeypatch.setattr(
        "butterfly.periodic_c.least_squares",
        lambda *args, **kwargs: SimpleNamespace(
            x=variables, success=True, nfev=1, message="xtol termination"
        ),
    )
    _, diagnostics = correct_arclength_c(
        predictor,
        tangent,
        reference,
        1.0,
        a=0.0,
        b=0.0,
        solver=SOLVER,
        tolerance=1e-11,
        max_evaluations=40,
    )
    assert diagnostics["closure_error"] < 1e-10
    assert diagnostics[f"{failed_equation}_residual"] > 1e-3
    assert not diagnostics["success"]
