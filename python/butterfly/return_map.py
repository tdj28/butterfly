"""Uncertainty-aware branch inference for scalar return-map projections."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Mapping, Sequence

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


@dataclass(frozen=True, slots=True)
class ReturnMapRobustnessResult:
    """Branch decision retained across a declared oracle perturbation family."""

    resolved: bool
    branch_count: int | None
    critical_point_intervals: tuple[tuple[float, float], ...]
    normalized_critical_point_spans: tuple[float, ...]
    maximum_normalized_critical_point_span: float
    variant_consensus: float
    variant_counts: tuple[int | None, ...]
    variant_results: tuple[ReturnMapBranchResult, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class LocalCriticalVariantResult:
    """One oracle variant's independently bootstrapped local critical point."""

    resolved: bool
    normalized_location: float | None
    normalized_interval: tuple[float, float] | None
    nearest_anchor_distance: float | None
    runner_up_margin: float | None
    conditional_spread_ratio: float
    domain_coverage: float
    bootstrap_consensus: float
    valid_bootstrap_samples: int
    bootstrap_samples: int
    nominal_critical_count: int
    reason: str


@dataclass(frozen=True, slots=True)
class LocalCriticalRobustnessResult:
    """A local critical point retained without requiring global branch count."""

    resolved: bool
    normalized_location: float | None
    normalized_interval: tuple[float, float] | None
    maximum_normalized_span: float
    variant_consensus: float
    variant_results: tuple[LocalCriticalVariantResult, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class ReturnMapCoverageCensorResult:
    """Branch decision under a prospectively declared coverage-only censor.

    A variant may be censored only when its sole failed gate is finite occupied
    domain coverage and its nominal critical geometry remains consistent with
    the fully resolved variants.  This result is deliberately separate from
    :class:`ReturnMapRobustnessResult` so the strict oracle is never overwritten
    in an experiment receipt.
    """

    resolved: bool
    branch_count: int | None
    fully_resolved_variant_indices: tuple[int, ...]
    coverage_censored_variant_indices: tuple[int, ...]
    rejected_variant_indices: tuple[int, ...]
    critical_point_intervals: tuple[tuple[float, float], ...]
    normalized_critical_point_spans: tuple[float, ...]
    maximum_normalized_critical_point_span: float
    reason: str


@dataclass(frozen=True, slots=True)
class LowerSupportSlopeRobustnessResult:
    """Signed return-map slope at the occupied lower-support boundary.

    The slope is measured after affine normalization of both scalar
    coordinates.  Each oracle variant is evaluated at its first populated
    binned-source median, so no spline extrapolation is used.  The reported
    interval is a numerical-sensitivity interval across the declared variants,
    not a confidence interval or a coordinate-free topological invariant.
    """

    resolved: bool
    slope_sign: int | None
    slope_interval: tuple[float, float] | None
    median_slope: float | None
    minimum_absolute_slope: float | None
    boundary_source_interval: tuple[float, float] | None
    variant_slopes: tuple[float, ...]
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


def _nearest_local_critical(
    critical_points: Sequence[float],
    expected_normalized_location: float,
) -> tuple[float | None, float | None, float | None]:
    """Return nearest point, anchor distance, and runner-up distance margin."""

    points = tuple(float(point) for point in critical_points)
    if not points:
        return None, None, None
    distances = tuple(abs(point - expected_normalized_location) for point in points)
    order = sorted(range(len(points)), key=lambda index: (distances[index], index))
    best = order[0]
    margin = (
        distances[order[1]] - distances[best] if len(order) > 1 else None
    )
    return points[best], distances[best], margin


def infer_local_critical_point_robust(
    source,
    target,
    *,
    expected_normalized_location: float,
    variants: Sequence[Mapping[str, object]],
    common_options: Mapping[str, object] | None = None,
    maximum_normalized_anchor_distance: float = 0.12,
    minimum_runner_up_margin: float = 0.05,
    minimum_variant_consensus: float = 1.0,
    maximum_normalized_span: float = 0.05,
) -> LocalCriticalRobustnessResult:
    """Track one predeclared critical point independently of total branch count.

    Each variant fits the same normalized return-map spline used by the global
    branch oracle.  It selects the critical point nearest a frozen anchor and
    bootstraps that *local identity*, not the number of extrema in the entire
    map.  A second critical point may therefore appear without erasing a
    stable pre-existing critical point.  The anchor and every acceptance gate
    must be chosen before evaluating held-out trajectories.
    """

    if not 0.0 <= expected_normalized_location <= 1.0:
        raise ValueError("expected normalized location must lie in [0,1]")
    if not variants:
        raise ValueError("at least one oracle variant is required")
    if maximum_normalized_anchor_distance < 0.0:
        raise ValueError("maximum anchor distance must be nonnegative")
    if minimum_runner_up_margin < 0.0:
        raise ValueError("minimum runner-up margin must be nonnegative")
    if not 0.0 < minimum_variant_consensus <= 1.0:
        raise ValueError("minimum variant consensus must lie in (0,1]")
    if maximum_normalized_span < 0.0:
        raise ValueError("maximum normalized span must be nonnegative")

    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    if source.ndim != 1 or target.ndim != 1 or len(source) != len(target):
        raise ValueError("source and target must be equal-length vectors")
    if not np.all(np.isfinite(source)) or not np.all(np.isfinite(target)):
        raise ValueError("return-map samples must be finite")
    source_range = float(np.ptp(source))
    target_range = float(np.ptp(target))
    if source_range == 0.0 or target_range == 0.0:
        return LocalCriticalRobustnessResult(
            False, None, None, float("inf"), 0.0, (), "degenerate coordinate range"
        )
    normalized_source = (source - np.min(source)) / source_range
    normalized_target = (target - np.min(target)) / target_range
    common = dict(common_options or {})
    results = []
    for variant_index, variant in enumerate(variants):
        options = {**common, **dict(variant)}
        bin_count = int(options.get("bin_count", 40))
        minimum_bin_points = int(options.get("minimum_bin_points", 4))
        smoothing = float(options.get("smoothing", 1e-6))
        grid_size = int(options.get("grid_size", 4097))
        minimum_prominence = float(options.get("minimum_prominence", 0.03))
        maximum_spread = float(
            options.get("maximum_conditional_spread_ratio", 0.08)
        )
        minimum_coverage = float(options.get("minimum_domain_coverage", 0.7))
        bootstrap_samples = int(options.get("bootstrap_samples", 100))
        minimum_bootstrap_consensus = float(
            options.get("minimum_bootstrap_consensus", 0.8)
        )
        random_seed = int(options.get("random_seed", 0)) + variant_index
        if len(source) < bin_count * minimum_bin_points:
            raise ValueError("insufficient samples for the requested bin audit")

        count, critical, spread, coverage = _fit_branch_count(
            normalized_source,
            normalized_target,
            bin_count=bin_count,
            minimum_bin_points=minimum_bin_points,
            smoothing=smoothing,
            grid_size=grid_size,
            minimum_prominence=minimum_prominence,
        )
        selected, distance, margin = _nearest_local_critical(
            critical, expected_normalized_location
        )
        nominal_count = max(int(count or 1) - 1, 0)
        if coverage < minimum_coverage:
            nominal_reason = "insufficient invariant-domain coverage"
        elif spread > maximum_spread:
            nominal_reason = "projection is not graph-like"
        elif selected is None:
            nominal_reason = "no prominent local critical candidate"
        elif distance is not None and distance > maximum_normalized_anchor_distance:
            nominal_reason = "nearest critical exceeds the anchor-distance gate"
        elif margin is not None and margin < minimum_runner_up_margin:
            nominal_reason = "nearest critical lacks the runner-up margin"
        else:
            nominal_reason = "nominal local critical resolved"

        bootstrap_locations = []
        if nominal_reason == "nominal local critical resolved" and bootstrap_samples:
            generator = np.random.default_rng(random_seed)
            for _ in range(bootstrap_samples):
                indices = generator.integers(0, len(source), len(source))
                (
                    bootstrap_count,
                    bootstrap_critical,
                    bootstrap_spread,
                    bootstrap_coverage,
                ) = _fit_branch_count(
                    normalized_source[indices],
                    normalized_target[indices],
                    bin_count=bin_count,
                    minimum_bin_points=minimum_bin_points,
                    smoothing=smoothing,
                    grid_size=grid_size,
                    minimum_prominence=minimum_prominence,
                )
                if (
                    bootstrap_count is None
                    or bootstrap_spread > maximum_spread
                    or bootstrap_coverage < minimum_coverage
                ):
                    continue
                bootstrap_selected, bootstrap_distance, bootstrap_margin = (
                    _nearest_local_critical(
                        bootstrap_critical, expected_normalized_location
                    )
                )
                if (
                    bootstrap_selected is not None
                    and bootstrap_distance is not None
                    and bootstrap_distance <= maximum_normalized_anchor_distance
                    and (
                        bootstrap_margin is None
                        or bootstrap_margin >= minimum_runner_up_margin
                    )
                ):
                    bootstrap_locations.append(bootstrap_selected)
        consensus = (
            len(bootstrap_locations) / bootstrap_samples
            if bootstrap_samples
            else (1.0 if nominal_reason == "nominal local critical resolved" else 0.0)
        )
        accepted_locations = (
            [float(selected), *bootstrap_locations] if selected is not None else []
        )
        interval = (
            (min(accepted_locations), max(accepted_locations))
            if accepted_locations
            else None
        )
        variant_span = (
            interval[1] - interval[0] if interval is not None else float("inf")
        )
        if nominal_reason != "nominal local critical resolved":
            resolved = False
            reason = nominal_reason
        elif consensus < minimum_bootstrap_consensus:
            resolved = False
            reason = "bootstrap local-critical identity is unstable"
        elif variant_span > maximum_normalized_span:
            resolved = False
            reason = "bootstrap local-critical location is too wide"
        else:
            resolved = True
            reason = "local critical resolved"
        results.append(
            LocalCriticalVariantResult(
                resolved=resolved,
                normalized_location=float(selected) if selected is not None else None,
                normalized_interval=interval,
                nearest_anchor_distance=distance,
                runner_up_margin=margin,
                conditional_spread_ratio=spread,
                domain_coverage=coverage,
                bootstrap_consensus=consensus,
                valid_bootstrap_samples=len(bootstrap_locations),
                bootstrap_samples=bootstrap_samples,
                nominal_critical_count=nominal_count,
                reason=reason,
            )
        )

    resolved_results = tuple(result for result in results if result.resolved)
    consensus = len(resolved_results) / len(results)
    intervals = tuple(
        result.normalized_interval
        for result in resolved_results
        if result.normalized_interval is not None
    )
    joint_interval = (
        (min(interval[0] for interval in intervals), max(interval[1] for interval in intervals))
        if intervals
        else None
    )
    span = (
        joint_interval[1] - joint_interval[0]
        if joint_interval is not None
        else float("inf")
    )
    location = (
        float(
            np.median(
                [
                    result.normalized_location
                    for result in resolved_results
                    if result.normalized_location is not None
                ]
            )
        )
        if resolved_results
        else None
    )
    if consensus < minimum_variant_consensus:
        resolved = False
        reason = "local critical does not resolve across oracle variants"
    elif span > maximum_normalized_span:
        resolved = False
        reason = "local critical location is variant-unstable"
    else:
        resolved = True
        reason = "local critical resolved across oracle variants"
    return LocalCriticalRobustnessResult(
        resolved=resolved,
        normalized_location=location if resolved else None,
        normalized_interval=joint_interval,
        maximum_normalized_span=span,
        variant_consensus=consensus,
        variant_results=tuple(results),
        reason=reason,
    )


def infer_lower_support_slope_robust(
    source,
    target,
    *,
    variants: Sequence[Mapping[str, object]],
    minimum_bin_points: int = 4,
    minimum_absolute_slope: float = 0.0,
) -> LowerSupportSlopeRobustnessResult:
    """Infer a robust signed derivative at the lower occupied map boundary.

    This is a companion observable to the discrete branch count.  It reuses
    only each variant's bin count and smoothing value, fits the same normalized
    cubic spline used by the branch oracle, and evaluates its derivative at
    the first populated bin median.  Resolution requires every declared
    variant to have the same nonzero sign and to clear ``minimum_absolute_slope``.
    """

    if not variants:
        raise ValueError("at least one oracle variant is required")
    if minimum_bin_points < 1:
        raise ValueError("minimum_bin_points must be positive")
    if minimum_absolute_slope < 0.0:
        raise ValueError("minimum_absolute_slope must be nonnegative")
    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    if source.ndim != 1 or target.ndim != 1 or len(source) != len(target):
        raise ValueError("source and target must be equal-length vectors")
    if not np.all(np.isfinite(source)) or not np.all(np.isfinite(target)):
        raise ValueError("return-map samples must be finite")
    source_range = float(np.ptp(source))
    target_range = float(np.ptp(target))
    if source_range == 0.0 or target_range == 0.0:
        return LowerSupportSlopeRobustnessResult(
            False, None, None, None, None, None, (), "degenerate coordinate range"
        )
    normalized_source = (source - np.min(source)) / source_range
    normalized_target = (target - np.min(target)) / target_range
    slopes = []
    boundaries = []
    for variant in variants:
        if "bin_count" not in variant or "smoothing" not in variant:
            raise ValueError("each slope variant requires bin_count and smoothing")
        x_values, y_values, _spreads = _binned_relation(
            normalized_source,
            normalized_target,
            bin_count=int(variant["bin_count"]),
            minimum_bin_points=minimum_bin_points,
        )
        if len(x_values) < 6:
            return LowerSupportSlopeRobustnessResult(
                False,
                None,
                None,
                None,
                None,
                None,
                tuple(slopes),
                "insufficient populated bins",
            )
        order = np.argsort(x_values)
        x_values = x_values[order]
        y_values = y_values[order]
        spline = UnivariateSpline(
            x_values,
            y_values,
            k=3,
            s=float(variant["smoothing"]) * len(x_values),
            ext=3,
        )
        slope = float(spline.derivative()(x_values[0]))
        if not np.isfinite(slope):
            return LowerSupportSlopeRobustnessResult(
                False,
                None,
                None,
                None,
                None,
                None,
                tuple(slopes),
                "nonfinite boundary slope",
            )
        slopes.append(slope)
        boundaries.append(float(np.min(source) + x_values[0] * source_range))

    slope_interval = (min(slopes), max(slopes))
    median_slope = float(np.median(slopes))
    minimum_magnitude = min(abs(slope) for slope in slopes)
    boundary_interval = (min(boundaries), max(boundaries))
    if all(slope > 0.0 for slope in slopes):
        sign = 1
    elif all(slope < 0.0 for slope in slopes):
        sign = -1
    else:
        return LowerSupportSlopeRobustnessResult(
            False,
            None,
            slope_interval,
            median_slope,
            minimum_magnitude,
            boundary_interval,
            tuple(slopes),
            "oracle variants disagree on slope sign",
        )
    if minimum_magnitude < minimum_absolute_slope:
        return LowerSupportSlopeRobustnessResult(
            False,
            None,
            slope_interval,
            median_slope,
            minimum_magnitude,
            boundary_interval,
            tuple(slopes),
            "boundary slope is too close to zero",
        )
    return LowerSupportSlopeRobustnessResult(
        True,
        sign,
        slope_interval,
        median_slope,
        minimum_magnitude,
        boundary_interval,
        tuple(slopes),
        "resolved across oracle variants",
    )


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


def infer_return_map_branches_robust(
    source,
    target,
    *,
    variants: Sequence[Mapping[str, object]],
    common_options: Mapping[str, object] | None = None,
    minimum_variant_consensus: float = 1.0,
    maximum_normalized_critical_point_span: float = 0.03,
) -> ReturnMapRobustnessResult:
    """Require a branch count and critical locations to survive perturbations.

    ``variants`` contains preregistered binning, smoothing, prominence, and
    bootstrap option dictionaries for :func:`infer_return_map_branches`.
    Critical points are sorted and matched by order. Their reported intervals
    are empirical numerical-sensitivity intervals, not confidence intervals.
    """

    if not variants:
        raise ValueError("at least one oracle variant is required")
    if not 0.0 < minimum_variant_consensus <= 1.0:
        raise ValueError("minimum_variant_consensus must lie in (0,1]")
    if maximum_normalized_critical_point_span < 0.0:
        raise ValueError("maximum critical-point span must be nonnegative")
    common = dict(common_options or {})
    results = tuple(
        infer_return_map_branches(source, target, **{**common, **dict(variant)})
        for variant in variants
    )
    counts = tuple(
        result.branch_count if result.resolved else None for result in results
    )
    resolved_counts = [count for count in counts if count is not None]
    if not resolved_counts:
        return ReturnMapRobustnessResult(
            False,
            None,
            (),
            (),
            float("inf"),
            0.0,
            counts,
            results,
            "no oracle variant resolved",
        )
    frequencies = Counter(resolved_counts)
    branch_count, frequency = min(
        frequencies.items(), key=lambda item: (-item[1], item[0])
    )
    consensus = frequency / len(results)
    agreeing = tuple(
        result
        for result in results
        if result.resolved and result.branch_count == branch_count
    )
    source_range = max(
        float(np.ptp(np.asarray(source, dtype=float))), np.finfo(float).eps
    )
    critical_intervals = tuple(
        (
            min(result.critical_points[index] for result in agreeing),
            max(result.critical_points[index] for result in agreeing),
        )
        for index in range(max(branch_count - 1, 0))
    )
    normalized_spans = tuple(
        (upper - lower) / source_range for lower, upper in critical_intervals
    )
    maximum_span = max(normalized_spans, default=0.0)
    if consensus < minimum_variant_consensus:
        resolved = False
        reason = "oracle variants disagree"
    elif maximum_span > maximum_normalized_critical_point_span:
        resolved = False
        reason = "critical-point location is variant-unstable"
    else:
        resolved = True
        reason = "resolved across oracle variants"
    return ReturnMapRobustnessResult(
        resolved,
        branch_count if resolved else None,
        critical_intervals,
        normalized_spans,
        maximum_span,
        consensus,
        counts,
        results,
        reason,
    )


def infer_return_map_branches_coverage_censored(
    robust: ReturnMapRobustnessResult,
    *,
    source_minimum: float,
    source_maximum: float,
    expected_branch_count: int,
    minimum_fully_resolved_variants: int = 12,
    minimum_censored_domain_coverage: float = 0.65,
    maximum_conditional_spread_ratio: float = 0.08,
    maximum_normalized_critical_point_span: float = 0.03,
) -> ReturnMapCoverageCensorResult:
    """Apply the EXP-121 coverage-only censor without hiding strict failures.

    Fully resolved variants must have ``expected_branch_count``.  Every other
    variant must fail *only* invariant-domain coverage, retain the expected
    number of nominal critical points, clear the declared coverage and
    graph-likeness floors, and preserve the joint critical-location span.
    Resolved contradictory counts and noncoverage failures are never censored.
    """

    if expected_branch_count < 1:
        raise ValueError("expected_branch_count must be positive")
    if minimum_fully_resolved_variants < 1:
        raise ValueError("minimum_fully_resolved_variants must be positive")
    if not 0.0 <= minimum_censored_domain_coverage <= 1.0:
        raise ValueError("minimum_censored_domain_coverage must lie in [0,1]")
    if maximum_conditional_spread_ratio < 0.0:
        raise ValueError("maximum_conditional_spread_ratio must be nonnegative")
    if maximum_normalized_critical_point_span < 0.0:
        raise ValueError("maximum critical-point span must be nonnegative")

    expected_critical_count = expected_branch_count - 1
    resolved_indices = []
    censored_indices = []
    rejected_indices = []
    accepted_critical = []
    for index, variant in enumerate(robust.variant_results):
        critical = tuple(float(value) for value in variant.critical_points)
        if (
            variant.resolved
            and variant.branch_count == expected_branch_count
            and len(critical) == expected_critical_count
        ):
            resolved_indices.append(index)
            accepted_critical.append(critical)
            continue
        coverage_only = bool(
            not variant.resolved
            and variant.reason == "insufficient invariant-domain coverage"
            and variant.domain_coverage >= minimum_censored_domain_coverage
            and variant.conditional_spread_ratio
            <= maximum_conditional_spread_ratio
            and len(critical) == expected_critical_count
        )
        if coverage_only:
            censored_indices.append(index)
            accepted_critical.append(critical)
        else:
            rejected_indices.append(index)

    source_range = max(
        float(source_maximum) - float(source_minimum), np.finfo(float).eps
    )
    intervals = (
        tuple(
            (
                min(points[index] for points in accepted_critical),
                max(points[index] for points in accepted_critical),
            )
            for index in range(expected_critical_count)
        )
        if accepted_critical
        else ()
    )
    normalized_spans = tuple(
        (upper - lower) / source_range for lower, upper in intervals
    )
    maximum_span = max(
        normalized_spans, default=0.0 if accepted_critical else float("inf")
    )
    resolved = bool(
        robust.variant_results
        and len(resolved_indices) >= minimum_fully_resolved_variants
        and len(resolved_indices) + len(censored_indices)
        == len(robust.variant_results)
        and not rejected_indices
        and maximum_span <= maximum_normalized_critical_point_span
    )
    if rejected_indices:
        reason = "one or more variants contradict or fail beyond coverage"
    elif len(resolved_indices) < minimum_fully_resolved_variants:
        reason = "too few fully resolved variants"
    elif maximum_span > maximum_normalized_critical_point_span:
        reason = "critical-point location is variant-unstable"
    elif resolved:
        reason = "resolved with prospectively admissible coverage censoring"
    else:
        reason = "coverage-censor evaluation failed"
    return ReturnMapCoverageCensorResult(
        resolved=resolved,
        branch_count=expected_branch_count if resolved else None,
        fully_resolved_variant_indices=tuple(resolved_indices),
        coverage_censored_variant_indices=tuple(censored_indices),
        rejected_variant_indices=tuple(rejected_indices),
        critical_point_intervals=intervals,
        normalized_critical_point_spans=normalized_spans,
        maximum_normalized_critical_point_span=maximum_span,
        reason=reason,
    )
