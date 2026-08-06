import numpy as np

from butterfly.classify import OrbitLabel, classify_fundamental_period


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
