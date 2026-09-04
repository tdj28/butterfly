import numpy as np

from butterfly.classify import (
    DynamicsClassification,
    OrbitLabel,
    classify_fundamental_period,
    classify_with_lyapunov,
    closest_recurrence_candidate,
    combine_initial_conditions,
)


def test_closest_recurrence_candidate_finds_exact_fundamental_pattern() -> None:
    pattern = np.array([[0.0, 0.0], [1.0, 0.5], [-0.5, 0.25]])
    crossings = np.tile(pattern, (6, 1))
    candidate = closest_recurrence_candidate(
        crossings, max_period=8, required_repeats=4
    )
    assert candidate is not None
    assert candidate.period == 3
    assert candidate.normalized_error == 0.0


def test_exact_fundamental_period_three() -> None:
    motif = np.asarray(((1.0, 0.0), (0.0, 2.0), (-1.0, 0.5)))
    result = classify_fundamental_period(np.tile(motif, (8, 1)), max_period=8)
    assert result.label == OrbitLabel.PERIODIC
    assert result.fundamental_period == 3
    assert result.recurrence_error == 0.0


def test_minimal_period_is_selected_over_a_multiple() -> None:
    motif = np.asarray(((1.0,), (-1.0,)))
    result = classify_fundamental_period(np.tile(motif, (12, 1)), max_period=10)
    assert result.fundamental_period == 2


def test_small_numerical_noise_is_accepted() -> None:
    rng = np.random.default_rng(20260806)
    motif = np.asarray(((1.0, 2.0), (-3.0, 0.5)))
    values = np.tile(motif, (10, 1)) + rng.normal(scale=1e-9, size=(20, 2))
    result = classify_fundamental_period(values, max_period=5, atol=1e-7, rtol=0.0)
    assert result.label == OrbitLabel.PERIODIC
    assert result.fundamental_period == 2


def test_nonperiodic_sequence_stays_unresolved() -> None:
    rng = np.random.default_rng(7)
    result = classify_fundamental_period(rng.normal(size=(100, 2)), max_period=12)
    assert result.label == OrbitLabel.UNRESOLVED
    assert result.fundamental_period is None
    assert "not inferred" in result.reason


def test_nonfinite_and_escape_labels_are_distinct() -> None:
    failed = classify_fundamental_period(((0.0,), (np.nan,)))
    escaped = classify_fundamental_period(((0.0,), (2e6,)))
    assert failed.label == OrbitLabel.NUMERICAL_FAILURE
    assert escaped.label == OrbitLabel.ESCAPING


def test_insufficient_crossings_are_unresolved() -> None:
    result = classify_fundamental_period(((1.0,), (1.0,), (1.0,)))
    assert result.label == OrbitLabel.UNRESOLVED
    assert "insufficient" in result.reason


def test_uncertainty_aware_chaos_signature() -> None:
    recurrence = classify_fundamental_period(np.arange(100.0), max_period=8)
    result = classify_with_lyapunov(
        recurrence,
        (0.104, 0.0014, -10.09),
        (0.0075, 0.0018, 0.0154),
    )
    assert result.label == OrbitLabel.CHAOTIC
    assert "three-exponent-chaos-signature" in result.evidence


def test_quasiperiodic_signature_requires_two_decisive_zeros() -> None:
    recurrence = classify_fundamental_period(np.arange(100.0), max_period=8)
    resolved = classify_with_lyapunov(
        recurrence,
        (5e-4, -4e-4, -2.0),
        (5e-4, 5e-4, 0.01),
    )
    uncertain = classify_with_lyapunov(
        recurrence,
        (0.002, 0.0, -2.0),
        (0.002, 0.001, 0.01),
    )
    assert resolved.label == OrbitLabel.QUASIPERIODIC
    assert uncertain.label == OrbitLabel.UNRESOLVED


def test_conflicting_period_and_positive_exponent_stays_unresolved() -> None:
    motif = np.tile(((1.0,), (-1.0,)), (10, 1))
    recurrence = classify_fundamental_period(motif, max_period=4)
    result = classify_with_lyapunov(
        recurrence,
        (0.1, 0.0, -2.0),
        (0.001, 0.001, 0.01),
    )
    assert recurrence.label == OrbitLabel.PERIODIC
    assert result.label == OrbitLabel.UNRESOLVED
    assert "conflicts" in result.reason


def test_distinct_initial_condition_periods_are_multistable() -> None:
    period_two = DynamicsClassification(
        OrbitLabel.PERIODIC, 2, 0.9, "period two", ("test",)
    )
    period_three = DynamicsClassification(
        OrbitLabel.PERIODIC, 3, 0.8, "period three", ("test",)
    )
    result = combine_initial_conditions([period_two, period_three])
    assert result.label == OrbitLabel.MULTISTABLE
    assert set(result.evidence) == {"periodic:p2", "periodic:p3"}


def test_escape_and_periodic_capture_do_not_imply_multistability() -> None:
    periodic = DynamicsClassification(
        OrbitLabel.PERIODIC, 2, 0.9, "period two", ("test",)
    )
    escaping = DynamicsClassification(
        OrbitLabel.ESCAPING, None, 1.0, "escape radius exceeded", ("test",)
    )
    result = combine_initial_conditions([periodic, escaping])
    assert result.label == OrbitLabel.UNRESOLVED
    assert result.fundamental_period is None
    assert "escape is not a bounded attractor" in result.reason


def test_agreeing_escaping_initial_conditions_remain_escaping() -> None:
    escaping = DynamicsClassification(
        OrbitLabel.ESCAPING, None, 1.0, "escape radius exceeded", ("test",)
    )
    result = combine_initial_conditions([escaping, escaping])
    assert result.label == OrbitLabel.ESCAPING


def test_escape_with_unresolved_initial_condition_remains_unresolved() -> None:
    escaping = DynamicsClassification(
        OrbitLabel.ESCAPING, None, 1.0, "escape radius exceeded", ("test",)
    )
    unresolved = DynamicsClassification(
        OrbitLabel.UNRESOLVED, None, 0.0, "insufficient returns", ("test",)
    )
    assert combine_initial_conditions([escaping, unresolved]).label == OrbitLabel.UNRESOLVED
