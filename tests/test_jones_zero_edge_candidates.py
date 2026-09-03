import numpy as np

from scripts.prepare_jones_zero_edge_candidates import interpolate_zero, zero_edges


def test_zero_edges_returns_both_orientations_deterministically() -> None:
    values = np.asarray([[1.0, -1.0], [-2.0, 3.0]])
    assert zero_edges(values) == [
        ("c", 0, 0, 0, 1),
        ("c", 1, 0, 1, 1),
        ("a", 0, 0, 1, 0),
        ("a", 0, 1, 1, 1),
    ]


def test_zero_edges_ignores_missing_and_same_sign_values() -> None:
    values = np.asarray([[1.0, np.nan, 2.0], [3.0, -1.0, 4.0]])
    assert zero_edges(values) == [("c", 1, 0, 1, 1), ("c", 1, 1, 1, 2)]


def test_interpolate_zero_uses_signed_linear_fraction() -> None:
    left = {"a": 0.2, "b": 0.2, "c": 6.0}
    right = {"a": 0.3, "b": 0.2, "c": 8.0}
    parameters, fraction = interpolate_zero(left, right, 1.0, -3.0)
    assert fraction == 0.25
    assert parameters == {"a": 0.225, "b": 0.2, "c": 6.5}
