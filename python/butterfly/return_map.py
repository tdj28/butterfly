"""Uncertainty-aware branch inference for scalar return-map projections."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.optimize import brentq


@dataclass(frozen=True, slots=True)
class ReturnMapBranchResult:
    """Result of a graph-likeness and critical-point branch audit."""

    resolved: bool
    branch_count: int | None
    critical_points: tuple[float, ...]
    conditional_spread_ratio: float
    domain_coverage: float
    bootstrap_consensus: float
    bootstrap_counts: tuple[int, ...]
    reason: str


def _binned_relation(source, target, *, bin_count, minimum_bin_points):
    edges = np.linspace(0.0, 1.0, bin_count + 1)
    indices = np.clip(np.digitize(source, edges) - 1, 0, bin_count - 1)
    x_values = []
    y_values = []
    spreads = []
    for index in range(bin_count):
        selected = indices == index
        if np.count_nonzero(selected) < minimum_bin_points:
            continue
        x_bin = source[selected]
        y_bin = target[selected]
        x_values.append(float(np.median(x_bin)))
        y_values.append(float(np.median(y_bin)))
        spreads.append(float(1.4826 * np.median(np.abs(y_bin - np.median(y_bin)))))
    return np.asarray(x_values), np.asarray(y_values), np.asarray(spreads)


def _critical_points(spline, *, grid_size, minimum_prominence):
    derivative = spline.derivative()
    grid = np.linspace(0.0, 1.0, grid_size)
    values = derivative(grid)
    roots = []
    for left, right, left_value, right_value in zip(
        grid[:-1], grid[1:], values[:-1], values[1:], strict=True
    ):
        if left_value == 0.0:
            roots.append(float(left))
        elif left_value * right_value < 0.0:
            roots.append(float(brentq(derivative, left, right)))
    unique = []
    for root in roots:
        if 1e-6 < root < 1.0 - 1e-6 and (
            not unique or abs(root - unique[-1]) > 2.0 / grid_size
        ):
            unique.append(root)
    retained = []
    landmarks = [0.0, *unique, 1.0]
    for index, root in enumerate(unique, start=1):
        value = float(spline(root))
        left_change = abs(value - float(spline(landmarks[index - 1])))
        right_change = abs(value - float(spline(landmarks[index + 1])))
        if min(left_change, right_change) >= minimum_prominence:
            retained.append(root)
    return tuple(retained)


def _fit_branch_count(
    source,
    target,
    *,
    bin_count,
    minimum_bin_points,
    smoothing,
    grid_size,
    minimum_prominence,
):
    x_values, y_values, spreads = _binned_relation(
        source,
        target,
        bin_count=bin_count,
        minimum_bin_points=minimum_bin_points,
    )
    coverage = len(x_values) / bin_count
    if len(x_values) < 6:
        return None, (), float("inf"), coverage
    order = np.argsort(x_values)
    x_values = x_values[order]
    y_values = y_values[order]
    spreads = spreads[order]
    target_range = max(float(np.ptp(target)), np.finfo(float).eps)
    spread_ratio = float(np.median(spreads) / target_range)
    spline = UnivariateSpline(
        x_values,
        y_values,
        k=3,
        s=float(smoothing) * len(x_values),
        ext=3,
    )
    critical = _critical_points(
        spline,
        grid_size=grid_size,
        minimum_prominence=minimum_prominence,
    )
    return len(critical) + 1, critical, spread_ratio, coverage


def infer_return_map_branches(
    source,
    target,
    *,
    bin_count: int = 40,
    minimum_bin_points: int = 4,
    smoothing: float = 1e-6,
    grid_size: int = 4097,
    minimum_prominence: float = 0.03,
    maximum_conditional_spread_ratio: float = 0.08,
    minimum_domain_coverage: float = 0.7,
    bootstrap_samples: int = 100,
    minimum_bootstrap_consensus: float = 0.8,
    random_seed: int = 0,
) -> ReturnMapBranchResult:
    """Infer a scalar return-map branch count or return an unresolved label.

    Both coordinates are affinely normalized. The oracle first checks whether
    the projection is sufficiently graph-like and covers the declared domain;
    it then counts prominent spline critical points and requires bootstrap
    agreement. A failed precondition is reported as unresolved rather than
    being coerced into a branch count.
    """

    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    if source.ndim != 1 or target.ndim != 1 or len(source) != len(target):
        raise ValueError("source and target must be equal-length vectors")
    if len(source) < bin_count * minimum_bin_points:
        raise ValueError("insufficient samples for the requested bin audit")
    if not np.all(np.isfinite(source)) or not np.all(np.isfinite(target)):
        raise ValueError("return-map samples must be finite")
    source_range = float(np.ptp(source))
    target_range = float(np.ptp(target))
    if source_range == 0.0 or target_range == 0.0:
        return ReturnMapBranchResult(
            False, None, (), float("inf"), 0.0, 0.0, (), "degenerate coordinate range"
        )
    normalized_source = (source - np.min(source)) / source_range
    normalized_target = (target - np.min(target)) / target_range
    count, critical, spread, coverage = _fit_branch_count(
        normalized_source,
        normalized_target,
        bin_count=bin_count,
        minimum_bin_points=minimum_bin_points,
        smoothing=smoothing,
        grid_size=grid_size,
        minimum_prominence=minimum_prominence,
    )
    if coverage < minimum_domain_coverage:
        reason = "insufficient invariant-domain coverage"
        resolved = False
    elif spread > maximum_conditional_spread_ratio:
        reason = "projection is not graph-like"
        resolved = False
    elif count is None:
        reason = "insufficient populated bins"
        resolved = False
    else:
        reason = "resolved"
        resolved = True

    bootstrap_counts = []
    if resolved and bootstrap_samples:
        generator = np.random.default_rng(random_seed)
        for _ in range(bootstrap_samples):
            indices = generator.integers(0, len(source), len(source))
            bootstrap_count, _, bootstrap_spread, bootstrap_coverage = _fit_branch_count(
                normalized_source[indices],
                normalized_target[indices],
                bin_count=bin_count,
                minimum_bin_points=minimum_bin_points,
                smoothing=smoothing,
                grid_size=grid_size,
                minimum_prominence=minimum_prominence,
            )
            if (
                bootstrap_count is not None
                and bootstrap_spread <= maximum_conditional_spread_ratio
                and bootstrap_coverage >= minimum_domain_coverage
            ):
                bootstrap_counts.append(bootstrap_count)
        consensus = (
            bootstrap_counts.count(count) / bootstrap_samples if count is not None else 0.0
        )
        if consensus < minimum_bootstrap_consensus:
            resolved = False
            reason = "bootstrap branch count is unstable"
    else:
        consensus = 1.0 if resolved else 0.0
    return ReturnMapBranchResult(
        resolved=resolved,
        branch_count=count if resolved else None,
        critical_points=tuple(
            float(np.min(source) + point * source_range) for point in critical
        ),
        conditional_spread_ratio=spread,
        domain_coverage=coverage,
        bootstrap_consensus=consensus,
        bootstrap_counts=tuple(bootstrap_counts),
        reason=reason,
    )
