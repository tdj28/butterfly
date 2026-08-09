from __future__ import annotations

import numpy as np

from scripts.qualify_jones_landmark_word import (
    _historical_partition,
    _phase_aligned_error,
    _spline_residuals,
)


def test_historical_partition_mapping_for_two_and_three_branches() -> None:
    two = _historical_partition("x", (0.0, 1.0), ((0.4, 0.6),), 2)
    assert two.branch_symbols == ("1", "0")
    assert two.critical_symbols == ("C",)
    three = _historical_partition(
        "x", (0.0, 1.0), ((0.2, 0.3), (0.7, 0.8)), 3
    )
    assert three.branch_symbols == ("2", "1", "0")
    assert three.critical_symbols == ("D", "C")


def test_phase_aligned_error_recovers_cyclic_shift() -> None:
    left = np.asarray([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [3.0, 0.0, 4.0]])
    right = np.roll(left, 1, axis=0)
    result = _phase_aligned_error(left, right, (1.0, 1.0))
    assert result["resolved"]
    assert result["maximum_scaled_error"] == 0.0


def test_spline_residual_is_small_at_quadratic_critical() -> None:
    source = np.linspace(0.0, 1.0, 2000)
    target = 1.0 - (source - 0.5) ** 2
    variants = (
        {"bin_count": 30, "minimum_bin_points": 4, "smoothing": 1e-8},
        {"bin_count": 40, "minimum_bin_points": 4, "smoothing": 1e-7},
    )
    residual = _spline_residuals(source, target, [0.5], variants)[0]
    assert residual < 0.02
