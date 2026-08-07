from __future__ import annotations

import numpy as np

from butterfly import infer_return_map_branches


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
