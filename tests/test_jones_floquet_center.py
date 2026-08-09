import numpy as np

from scripts.search_jones_floquet_center import (
    quadratic_saddle_candidates,
    ring_sign_alternations,
    signed_dominant_nontrivial,
)


def test_signed_dominant_nontrivial_removes_neutral_multiplier() -> None:
    dominant, neutral, index = signed_dominant_nontrivial([0.23, 1.0 + 2e-10, -1e-18])
    assert index == 1
    assert abs(neutral - 1.0) < 1e-9
    assert dominant == complex(0.23)


def test_ring_sign_alternations_identifies_transverse_crossing() -> None:
    assert ring_sign_alternations([1, 1, -1, -1, 1, 1, -1, -1]) == 4
    assert ring_sign_alternations([1, 1, 1, -1, -1, -1, -1, 1]) == 2
    assert ring_sign_alternations([1, 0, -1, -1, 1, 1, -1, -1]) == 0


def test_quadratic_saddle_candidate_recovers_shifted_product_zero() -> None:
    a_values = np.linspace(-1.0, 1.0, 5)
    c_values = np.linspace(-1.0, 1.0, 5)
    aa, cc = np.meshgrid(a_values, c_values, indexing="ij")
    values = (aa - 0.12) * (cc + 0.08)
    candidates = quadratic_saddle_candidates(
        a_values,
        c_values,
        values,
        maximum_stationary_cell_offset=0.8,
        minimum_ring_sign_alternations=4,
        zero_tolerance=1e-12,
    )
    assert candidates
    best = candidates[0]
    assert abs(best["parameters"]["a"] - 0.12) < 1e-12
    assert abs(best["parameters"]["c"] + 0.08) < 1e-12
    assert abs(best["stationary_multiplier"]) < 1e-12
    assert best["hessian_eigenvalues"][0] < 0 < best["hessian_eigenvalues"][1]


def test_quadratic_valley_is_not_a_saddle_candidate() -> None:
    axis = np.linspace(-1.0, 1.0, 5)
    aa, cc = np.meshgrid(axis, axis, indexing="ij")
    values = aa * aa + cc * cc
    assert not quadratic_saddle_candidates(
        axis,
        axis,
        values,
        maximum_stationary_cell_offset=0.8,
        minimum_ring_sign_alternations=4,
        zero_tolerance=1e-12,
    )
