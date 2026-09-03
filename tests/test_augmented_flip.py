from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from butterfly import (
    RosslerParameters,
    SolverConfig,
    augmented_flip_system,
    integrate_flip_segment,
    rossler_hessian_action,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from solve_analytic_augmented_flip import receipt_seed  # noqa: E402


SOLVER = SolverConfig(method="DOP853", rtol=1e-11, atol=1e-13, max_step=0.02)
PARAMETERS = RosslerParameters(a=0.245, b=0.18, c=5.1)


def test_rossler_hessian_action_is_symmetric() -> None:
    left = np.asarray((0.2, -0.3, 0.7))
    right = np.asarray((-0.5, 0.1, 0.4))
    np.testing.assert_allclose(
        rossler_hessian_action(left, right),
        rossler_hessian_action(right, left),
    )
    np.testing.assert_allclose(
        rossler_hessian_action(left, right),
        (0.0, 0.0, -0.27),
    )


def test_segment_second_variations_match_finite_differences() -> None:
    state = np.asarray((0.4, -0.2, 0.3))
    tangent = np.asarray((0.6, 0.1, -0.4))
    duration = 0.17
    endpoint, transition, b_sensitivity, transported, state_action, b_action = (
        integrate_flip_segment(state, tangent, duration, PARAMETERS, SOLVER)
    )
    epsilon = 2e-6
    numerical_state_action = np.empty((3, 3))
    for index in range(3):
        offset = np.eye(3)[index] * epsilon
        plus = integrate_flip_segment(
            state + offset, tangent, duration, PARAMETERS, SOLVER
        )[3]
        minus = integrate_flip_segment(
            state - offset, tangent, duration, PARAMETERS, SOLVER
        )[3]
        numerical_state_action[:, index] = (plus - minus) / (2.0 * epsilon)
    plus_parameters = RosslerParameters(a=PARAMETERS.a, b=PARAMETERS.b + epsilon, c=PARAMETERS.c)
    minus_parameters = RosslerParameters(a=PARAMETERS.a, b=PARAMETERS.b - epsilon, c=PARAMETERS.c)
    numerical_b_action = (
        integrate_flip_segment(state, tangent, duration, plus_parameters, SOLVER)[3]
        - integrate_flip_segment(state, tangent, duration, minus_parameters, SOLVER)[3]
    ) / (2.0 * epsilon)
    np.testing.assert_allclose(state_action, numerical_state_action, rtol=2e-7, atol=2e-9)
    np.testing.assert_allclose(b_action, numerical_b_action, rtol=2e-7, atol=2e-9)
    assert np.all(np.isfinite(endpoint))
    assert np.all(np.isfinite(transition))
    assert np.all(np.isfinite(b_sensitivity))
    assert np.all(np.isfinite(transported))


def test_segment_c_second_variation_matches_finite_difference() -> None:
    state = np.asarray((0.4, -0.2, 0.3))
    tangent = np.asarray((0.6, 0.1, -0.4))
    duration = 0.17
    result = integrate_flip_segment(
        state,
        tangent,
        duration,
        PARAMETERS,
        SOLVER,
        continuation_parameter="c",
    )
    c_sensitivity = result[2]
    c_action = result[5]
    epsilon = 2e-6
    plus_parameters = RosslerParameters(
        a=PARAMETERS.a, b=PARAMETERS.b, c=PARAMETERS.c + epsilon
    )
    minus_parameters = RosslerParameters(
        a=PARAMETERS.a, b=PARAMETERS.b, c=PARAMETERS.c - epsilon
    )
    plus = integrate_flip_segment(
        state,
        tangent,
        duration,
        plus_parameters,
        SOLVER,
        continuation_parameter="c",
    )
    minus = integrate_flip_segment(
        state,
        tangent,
        duration,
        minus_parameters,
        SOLVER,
        continuation_parameter="c",
    )
    numerical_endpoint = (plus[0] - minus[0]) / (2.0 * epsilon)
    numerical_action = (plus[3] - minus[3]) / (2.0 * epsilon)
    np.testing.assert_allclose(c_sensitivity, numerical_endpoint, rtol=2e-7, atol=2e-9)
    np.testing.assert_allclose(c_action, numerical_action, rtol=2e-7, atol=2e-9)


def test_segment_a_second_variation_matches_finite_difference() -> None:
    state = np.asarray((0.4, -0.2, 0.3))
    tangent = np.asarray((0.6, 0.1, -0.4))
    duration = 0.17
    result = integrate_flip_segment(
        state,
        tangent,
        duration,
        PARAMETERS,
        SOLVER,
        continuation_parameter="a",
    )
    a_sensitivity = result[2]
    a_action = result[5]
    epsilon = 2e-6
    plus_parameters = RosslerParameters(
        a=PARAMETERS.a + epsilon, b=PARAMETERS.b, c=PARAMETERS.c
    )
    minus_parameters = RosslerParameters(
        a=PARAMETERS.a - epsilon, b=PARAMETERS.b, c=PARAMETERS.c
    )
    plus = integrate_flip_segment(
        state,
        tangent,
        duration,
        plus_parameters,
        SOLVER,
        continuation_parameter="a",
    )
    minus = integrate_flip_segment(
        state,
        tangent,
        duration,
        minus_parameters,
        SOLVER,
        continuation_parameter="a",
    )
    numerical_endpoint = (plus[0] - minus[0]) / (2.0 * epsilon)
    numerical_action = (plus[3] - minus[3]) / (2.0 * epsilon)
    np.testing.assert_allclose(a_sensitivity, numerical_endpoint, rtol=2e-7, atol=2e-9)
    np.testing.assert_allclose(a_action, numerical_action, rtol=2e-7, atol=2e-9)


def test_augmented_flip_jacobian_matches_finite_differences() -> None:
    segment_count = 2
    nodes = np.asarray(((0.4, -0.2, 0.3), (0.36, -0.12, 0.25)))
    tangents = np.asarray(((0.8, 0.2, -0.3), (0.7, 0.25, -0.2)))
    variables = np.r_[nodes.ravel(), 0.34, PARAMETERS.b, tangents.ravel()]
    phase = np.asarray((0.3, -0.4, 0.5))
    phase /= np.linalg.norm(phase)

    def residual(value):
        return augmented_flip_system(
            value,
            segment_count=segment_count,
            a=PARAMETERS.a,
            c=PARAMETERS.c,
            phase=phase,
            phase_reference=nodes[0],
            solver=SOLVER,
        )[0]

    _, analytic = augmented_flip_system(
        variables,
        segment_count=segment_count,
        a=PARAMETERS.a,
        c=PARAMETERS.c,
        phase=phase,
        phase_reference=nodes[0],
        solver=SOLVER,
    )
    epsilon = 2e-6
    numerical = np.empty_like(analytic)
    for index in range(len(variables)):
        offset = np.eye(len(variables))[index] * epsilon
        numerical[:, index] = (residual(variables + offset) - residual(variables - offset)) / (
            2.0 * epsilon
        )
    np.testing.assert_allclose(analytic, numerical, rtol=3e-7, atol=3e-9)


def test_augmented_c_flip_jacobian_matches_finite_differences() -> None:
    segment_count = 2
    nodes = np.asarray(((0.4, -0.2, 0.3), (0.36, -0.12, 0.25)))
    tangents = np.asarray(((0.8, 0.2, -0.3), (0.7, 0.25, -0.2)))
    variables = np.r_[nodes.ravel(), 0.34, PARAMETERS.c, tangents.ravel()]
    phase = np.asarray((0.3, -0.4, 0.5))
    phase /= np.linalg.norm(phase)

    def residual(value):
        return augmented_flip_system(
            value,
            segment_count=segment_count,
            a=PARAMETERS.a,
            c=None,
            phase=phase,
            phase_reference=nodes[0],
            solver=SOLVER,
            continuation_parameter="c",
            fixed_b=PARAMETERS.b,
        )[0]

    _, analytic = augmented_flip_system(
        variables,
        segment_count=segment_count,
        a=PARAMETERS.a,
        c=None,
        phase=phase,
        phase_reference=nodes[0],
        solver=SOLVER,
        continuation_parameter="c",
        fixed_b=PARAMETERS.b,
    )
    epsilon = 2e-6
    numerical = np.empty_like(analytic)
    for index in range(len(variables)):
        offset = np.eye(len(variables))[index] * epsilon
        numerical[:, index] = (
            residual(variables + offset) - residual(variables - offset)
        ) / (2.0 * epsilon)
    np.testing.assert_allclose(analytic, numerical, rtol=3e-7, atol=3e-9)


def test_augmented_a_flip_jacobian_matches_finite_differences() -> None:
    segment_count = 2
    nodes = np.asarray(((0.4, -0.2, 0.3), (0.36, -0.12, 0.25)))
    tangents = np.asarray(((0.8, 0.2, -0.3), (0.7, 0.25, -0.2)))
    variables = np.r_[nodes.ravel(), 0.34, PARAMETERS.a, tangents.ravel()]
    phase = np.asarray((0.3, -0.4, 0.5))
    phase /= np.linalg.norm(phase)

    def residual(value):
        return augmented_flip_system(
            value,
            segment_count=segment_count,
            a=None,
            c=PARAMETERS.c,
            phase=phase,
            phase_reference=nodes[0],
            solver=SOLVER,
            continuation_parameter="a",
            fixed_b=PARAMETERS.b,
        )[0]

    _, analytic = augmented_flip_system(
        variables,
        segment_count=segment_count,
        a=None,
        c=PARAMETERS.c,
        phase=phase,
        phase_reference=nodes[0],
        solver=SOLVER,
        continuation_parameter="a",
        fixed_b=PARAMETERS.b,
    )
    epsilon = 2e-6
    numerical = np.empty_like(analytic)
    for index in range(len(variables)):
        offset = np.eye(len(variables))[index] * epsilon
        numerical[:, index] = (
            residual(variables + offset) - residual(variables - offset)
        ) / (2.0 * epsilon)
    np.testing.assert_allclose(analytic, numerical, rtol=3e-7, atol=3e-9)


def test_analytic_receipt_seed_preserves_tangent_field() -> None:
    receipt = {
        "schema": "butterfly.analytic-augmented-flip.v1",
        "nodes": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        "period_time": 7.0,
        "corrected_b": 0.18,
        "tangent_nodes": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        "flip_spectrum": {"direct_flip_median": -0.999},
    }
    nodes, duration, b, tangents, multiplier = receipt_seed(
        receipt,
        source_schema="butterfly.analytic-augmented-flip.v1",
        seed_b_offset=1e-6,
        solver=SOLVER,
        a=PARAMETERS.a,
        c=PARAMETERS.c,
    )
    np.testing.assert_allclose(nodes, receipt["nodes"])
    np.testing.assert_allclose(tangents, receipt["tangent_nodes"])
    assert duration == 7.0
    assert b == 0.180001
    assert multiplier == complex(-0.999)


def test_precision_audited_receipt_can_seed_fresh_tangent_field() -> None:
    receipt = {
        "schema": "butterfly.precision-audited-flip-resume.v1",
        "best_evaluation": {
            "nodes": [[0.4, -0.2, 0.3], [0.36, -0.12, 0.25]],
            "period_time": 0.34,
            "b": 0.18,
        },
    }
    nodes, duration, b, tangents, multiplier = receipt_seed(
        receipt,
        source_schema="butterfly.precision-audited-flip-resume.v1",
        seed_b_offset=0.0,
        solver=SOLVER,
        a=PARAMETERS.a,
        c=PARAMETERS.c,
    )
    np.testing.assert_allclose(nodes, receipt["best_evaluation"]["nodes"])
    assert tangents.shape == nodes.shape
    assert duration == 0.34
    assert b == 0.18
    assert np.isfinite(multiplier.real)
