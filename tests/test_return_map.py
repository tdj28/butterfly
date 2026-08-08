from __future__ import annotations

import numpy as np

from butterfly import infer_return_map_branches, infer_return_map_branches_robust


def samples(function, count=4000):
    source = np.linspace(0.0, 1.0, count)
    return source, function(source)


def test_monotone_return_map_has_one_branch() -> None:
    source, target = samples(lambda value: 0.1 + 0.8 * value)
    result = infer_return_map_branches(source, target, bootstrap_samples=20)
    assert result.resolved
    assert result.branch_count == 1
    assert result.critical_points == ()


def test_logistic_return_map_has_two_branches() -> None:
    source, target = samples(lambda value: 4.0 * value * (1.0 - value))
    result = infer_return_map_branches(source, target, bootstrap_samples=20)
    assert result.resolved
    assert result.branch_count == 2
    np.testing.assert_allclose(result.critical_points, (0.5,), atol=2e-3)


def test_cubic_return_map_has_three_branches() -> None:
    source, target = samples(
        lambda value: 0.5 + 2.4 * (value - 0.5) ** 3 - 0.42 * (value - 0.5)
    )
    result = infer_return_map_branches(
        source, target, minimum_prominence=0.01, bootstrap_samples=20
    )
    assert result.resolved
    assert result.branch_count == 3
    assert len(result.critical_points) == 2


def test_multivalued_projection_is_unresolved() -> None:
    source = np.tile(np.linspace(0.0, 1.0, 2000), 2)
    base = 4.0 * source[:2000] * (1.0 - source[:2000])
    target = np.r_[base, 1.0 - base]
    result = infer_return_map_branches(source, target, bootstrap_samples=0)
    assert not result.resolved
    assert result.branch_count is None
    assert result.reason == "projection is not graph-like"


def test_robust_oracle_retains_shallow_boundary_extremum() -> None:
    source, target = samples(
        lambda value: value**3 / 3.0 - 0.53 * value**2 / 2.0 + 0.036 * value
    )
    result = infer_return_map_branches_robust(
        source,
        target,
        common_options={
            "minimum_bin_points": 4,
            "grid_size": 4097,
            "minimum_prominence": 0.001,
            "bootstrap_samples": 20,
        },
        variants=tuple(
            {"bin_count": bins, "smoothing": smoothing}
            for bins in (25, 40, 60)
            for smoothing in (1e-6, 1e-5)
        ),
        minimum_variant_consensus=1.0,
        maximum_normalized_critical_point_span=0.03,
    )
    assert result.resolved
    assert result.branch_count == 3
    assert result.variant_consensus == 1.0
    assert len(result.critical_point_intervals) == 2
    np.testing.assert_allclose(
        [sum(interval) / 2.0 for interval in result.critical_point_intervals],
        (0.08, 0.45),
        atol=0.01,
    )


def test_robust_oracle_rejects_variant_disagreement() -> None:
    source, target = samples(
        lambda value: value**3 / 3.0 - 0.53 * value**2 / 2.0 + 0.036 * value
    )
    result = infer_return_map_branches_robust(
        source,
        target,
        common_options={"bin_count": 40, "bootstrap_samples": 0},
        variants=(
            {"minimum_prominence": 0.001},
            {"minimum_prominence": 0.2},
        ),
        minimum_variant_consensus=1.0,
    )
    assert not result.resolved
    assert result.branch_count is None
    assert result.variant_consensus == 0.5
    assert result.reason == "oracle variants disagree"
