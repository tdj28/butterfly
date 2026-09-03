from __future__ import annotations

import numpy as np

from butterfly import infer_local_critical_point_robust


def _variants(prominence: float = 0.005):
    return (
        {
            "bin_count": 30,
            "minimum_bin_points": 4,
            "smoothing": 1e-6,
            "grid_size": 2049,
            "minimum_prominence": prominence,
            "maximum_conditional_spread_ratio": 0.08,
            "minimum_domain_coverage": 0.7,
            "bootstrap_samples": 12,
            "minimum_bootstrap_consensus": 0.75,
            "random_seed": 18,
        },
        {
            "bin_count": 40,
            "minimum_bin_points": 4,
            "smoothing": 1e-5,
            "grid_size": 2049,
            "minimum_prominence": prominence,
            "maximum_conditional_spread_ratio": 0.08,
            "minimum_domain_coverage": 0.7,
            "bootstrap_samples": 12,
            "minimum_bootstrap_consensus": 0.75,
            "random_seed": 19,
        },
    )


def test_local_critical_survives_an_added_distant_extremum() -> None:
    source = np.linspace(0.0, 1.0, 2400)
    derivative_roots = (source - 0.12) * (source - 0.62)
    target = source**3 / 3.0 - 0.37 * source**2 + 0.0744 * source
    assert np.max(np.abs(np.gradient(target, source) - derivative_roots)) < 5e-4
    result = infer_local_critical_point_robust(
        source,
        target,
        expected_normalized_location=0.6,
        variants=_variants(prominence=0.001),
        maximum_normalized_anchor_distance=0.12,
        minimum_runner_up_margin=0.15,
        maximum_normalized_span=0.08,
    )
    assert result.resolved
    assert result.normalized_location is not None
    assert abs(result.normalized_location - 0.62) < 0.04
    assert all(
        variant.nominal_critical_count == 2 for variant in result.variant_results
    )


def test_local_critical_rejects_an_ambiguous_anchor() -> None:
    source = np.linspace(0.0, 1.0, 2400)
    target = source**3 / 3.0 - 0.5 * source**2 + 0.21 * source
    result = infer_local_critical_point_robust(
        source,
        target,
        expected_normalized_location=0.5,
        variants=_variants(prominence=0.001),
        maximum_normalized_anchor_distance=0.3,
        minimum_runner_up_margin=0.15,
        maximum_normalized_span=0.08,
    )
    assert not result.resolved
    assert all(
        variant.reason == "nearest critical lacks the runner-up margin"
        for variant in result.variant_results
    )


def test_local_critical_rejects_a_distant_candidate() -> None:
    source = np.linspace(0.0, 1.0, 2400)
    target = -(source - 0.8) ** 2
    result = infer_local_critical_point_robust(
        source,
        target,
        expected_normalized_location=0.2,
        variants=_variants(prominence=0.01),
        maximum_normalized_anchor_distance=0.12,
        minimum_runner_up_margin=0.05,
        maximum_normalized_span=0.08,
    )
    assert not result.resolved
    assert all(
        variant.reason == "nearest critical exceeds the anchor-distance gate"
        for variant in result.variant_results
    )
