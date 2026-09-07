"""Seed-block, held-out scalar-map audit. No orbit words or target loading.

Operational finite-resolution diagnostics, not a topological conjugacy theorem
or a calibrated statistical test of exact criticality.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import warnings
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.optimize import brentq

from .paired_sampling import block_bootstrap_indices


@dataclass(frozen=True)
class MapOptions:
    minimum_seeds: int = 256
    minimum_bin_seeds: int = 8
    minimum_coverage: float = .7
    maximum_empty_run: int = 2
    maximum_heldout_unsupported_fraction: float = .05
    maximum_heldout_q90_error: float = .08
    minimum_prominence: float = .03
    grid_size: int = 4097
    bootstrap_samples: int = 200
    minimum_bootstrap_consensus: float = .8
    maximum_critical_span: float = .04
    random_seed: int = 481002


VARIANTS = ((40, 1e-5), (30, 1e-5), (50, 1e-5), (40, 1e-6), (40, 1e-4))


def _validate_options(options):
    for name in ("minimum_seeds", "minimum_bin_seeds", "maximum_empty_run", "grid_size", "bootstrap_samples", "random_seed"):
        value = getattr(options, name)
        if type(value) is not int or value < (0 if name in ("maximum_empty_run", "random_seed") else 1):
            raise ValueError("invalid integer map option")
    for name in ("minimum_coverage", "maximum_heldout_unsupported_fraction", "maximum_heldout_q90_error",
                 "minimum_prominence", "minimum_bootstrap_consensus", "maximum_critical_span"):
        value = getattr(options, name)
        if not np.isfinite(value) or not 0 < value <= 1:
            raise ValueError("invalid map fraction")
    if options.grid_size < 33:
        raise ValueError("critical grid too small")


def _empty_run(occupied):
    best = current = 0
    for value in occupied:
        current = 0 if value else current+1
        best = max(best, current)
    return best


def _fit(pairs, seed_ids, bounds, bins, smoothing, options):
    lower, span = bounds
    normalized = (pairs-lower)/span
    x, y = normalized[..., 0].ravel(), normalized[..., 1].ravel()
    ids = np.repeat(seed_ids, pairs.shape[1])
    assignments = np.clip(np.floor(x*bins).astype(int), 0, bins-1)
    xs, ys, occupied = [], [], np.zeros(bins, bool)
    for b in range(bins):
        selected = assignments == b
        # A seed sampled twice in bootstrap has twice its weight but does not
        # become two independently observed seeds for minimum support.
        if len(np.unique(ids[selected])) < options.minimum_bin_seeds:
            continue
        occupied[b] = True
        xs.append(float(np.median(x[selected])))
        ys.append(float(np.median(y[selected])))
    indices = np.flatnonzero(occupied)
    if len(xs) < 6 or occupied.mean() < options.minimum_coverage:
        return {"resolved": False, "reason": "insufficient bin coverage", "coverage": float(occupied.mean())}
    if _empty_run(occupied[indices[0]:indices[-1]+1]) > options.maximum_empty_run:
        return {"resolved": False, "reason": "unsupported interior gap", "coverage": float(occupied.mean())}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        spline = UnivariateSpline(xs, ys, k=3, s=smoothing*len(xs), ext=2)
    if caught:
        return {"resolved": False, "reason": "spline fit warning", "coverage": float(occupied.mean())}
    lo, hi = xs[0], xs[-1]
    grid = np.linspace(lo, hi, options.grid_size)
    grid_spacing = (hi-lo)/(options.grid_size-1)
    derivative = spline.derivative()
    values = derivative(grid)
    roots = []
    for a, b, da, db in zip(grid[:-1], grid[1:], values[:-1], values[1:]):
        if da*db < 0:
            root = float(brentq(derivative, a, b))
        elif da == 0 and a != lo:
            root = float(a)
        else:
            continue
        # A zero slope alone need not be a turning point (e.g. x^3). Also
        # reject sub-grid pairs of numerical roots around a stationary
        # inflection instead of merging them into one false extra branch.
        if derivative(max(lo, root-grid_spacing))*derivative(min(hi, root+grid_spacing)) >= 0:
            continue
        if not roots or root-roots[-1] > 2*(hi-lo)/(options.grid_size-1):
            roots.append(root)
    landmarks = [lo, *roots, hi]
    critical = []
    for i, root in enumerate(roots, 1):
        left_change = float(spline(root)-spline(landmarks[i-1]))
        right_change = float(spline(root)-spline(landmarks[i+1]))
        # Extrema must be above BOTH neighbors or below BOTH, not merely far
        # from each in absolute value. Otherwise a missed/sub-grid root pair
        # near a stationary inflection can create a false prominent branch.
        if left_change*right_change > 0 and min(abs(left_change), abs(right_change)) >= options.minimum_prominence:
            critical.append(root)
    # Do not infer an extremum by interpolating across an unsupported bin.
    for root in critical:
        b = min(int(root*bins), bins-1)
        if b < 1 or b >= bins-1 or not occupied[b-1:b+2].all():
            return {"resolved": False, "reason": "critical point lacks neighboring support", "coverage": float(occupied.mean())}
    return {"resolved": True, "reason": "fit", "coverage": float(occupied.mean()),
            "critical_points": critical, "spline": spline, "domain": (lo, hi), "occupied": occupied}


def audit_map(calibration, validation, *, calibration_ids, validation_ids, options=MapOptions(), variants=VARIANTS,
              retain_models=False):
    """Fit only calibration; freeze its normalization for held-out predictions.

    Input shape is [seed, equal number of selected consecutive pairs, 2].
    Bootstrap replicates retain every pair belonging to a resampled seed.
    No coordinate, hyperparameter or branch count is selected by an orbit word.
    """
    _validate_options(options)
    if type(retain_models) is not bool:
        raise ValueError("retain_models must be Boolean")
    cal, val = np.asarray(calibration, float), np.asarray(validation, float)
    cids, vids = np.asarray(calibration_ids), np.asarray(validation_ids)
    for array, ids in ((cal, cids), (val, vids)):
        if (array.ndim != 3 or array.shape[-1] != 2 or array.shape[1] < 1 or not np.isfinite(array).all()
                or ids.shape != (len(array),) or ids.dtype.kind not in "iu" or np.any(ids < 0)
                or len(np.unique(ids)) != len(ids)):
            raise ValueError("finite equal-pair seed blocks and unique IDs required")
    if cal.shape[1] != val.shape[1] or np.intersect1d(cids, vids).size:
        raise ValueError("equal per-seed weights and disjoint calibration/holdout required")
    if not variants or any(type(b) is not int or b < 6 or not np.isfinite(s) or s <= 0 for b, s in variants):
        raise ValueError("valid frozen spline variants required")
    result = {"resolved": False, "calibration_seeds": len(cal), "validation_seeds": len(val),
              "pairs_per_seed": cal.shape[1], "options": asdict(options), "variants": [],
              "critical_intervals": [], "branch_count": None,
              "interval_semantics": "seed-bootstrap and fixed-variant descriptive envelope; no simultaneous confidence guarantee"}
    if min(len(cal), len(val)) < options.minimum_seeds:
        return {**result, "reason": "insufficient independent seeds"}
    lower, span = float(cal.min()), float(np.ptp(cal))
    if span <= 0 or np.ptp(cal[..., 0]) == 0 or np.ptp(cal[..., 1]) == 0:
        return {**result, "reason": "degenerate calibration range"}
    result["calibration_bounds"] = [lower, lower+span]
    normalized_cal = (cal-lower)/span
    affine = np.polyfit(normalized_cal[..., 0].ravel(), normalized_cal[..., 1].ravel(), 1)
    result["affine_baseline_calibration_coefficients"] = affine.tolist()
    draws = block_bootstrap_indices(len(cal), options.bootstrap_samples, random_seed=options.random_seed)
    nominal_counts, all_points = [], []
    for bins, smoothing in variants:
        fit = _fit(cal, cids, (lower, span), bins, smoothing, options)
        record = {"bins": bins, "smoothing": smoothing, "resolved": False, "coverage": fit["coverage"], "reason": fit["reason"]}
        result["variants"].append(record)
        if not fit["resolved"]:
            continue
        normalized = (val-lower)/span
        x, y = normalized[..., 0].ravel(), normalized[..., 1].ravel()
        lo, hi = fit["domain"]
        assignments = np.clip(np.floor(x*bins).astype(int), 0, bins-1)
        supported = (x >= lo) & (x <= hi) & fit["occupied"][assignments]
        unsupported = float(1-supported.mean())
        errors = np.abs(y[supported]-fit["spline"](x[supported]))
        error = float(np.quantile(errors, .9)) if len(errors) else None
        affine_error = float(np.quantile(np.abs(y[supported]-np.polyval(affine, x[supported])), .9)) if len(errors) else None
        record.update(critical_points=[lower+span*r for r in fit["critical_points"]],
            normalized_critical_points=fit["critical_points"], normalized_domain=[lo, hi],
            heldout_unsupported_fraction=unsupported, heldout_q90_error=error,
            heldout_affine_q90_error=affine_error)
        if retain_models:
            knots = fit["spline"].get_knots()
            record["model"] = {"knots": np.r_[np.repeat(knots[0], 3), knots, np.repeat(knots[-1], 3)].tolist(),
                               "coefficients": fit["spline"].get_coeffs().tolist(), "degree": 3,
                               "occupied_bins": fit["occupied"].tolist()}
        if unsupported > options.maximum_heldout_unsupported_fraction or error is None or error > options.maximum_heldout_q90_error:
            record["reason"] = "held-out graph/support gate failed"
            continue
        points = []
        counts = []
        for indices in draws:
            replica = _fit(cal[indices], cids[indices], (lower, span), bins, smoothing, options)
            count = len(replica["critical_points"]) if replica["resolved"] else None
            counts.append(count)
            if count == len(fit["critical_points"]):
                points.append(replica["critical_points"])
        consensus = len(points)/options.bootstrap_samples
        record.update(bootstrap_critical_counts=counts, bootstrap_consensus=consensus)
        if consensus < options.minimum_bootstrap_consensus:
            record["reason"] = "seed-block branch stability failed"
            continue
        nominal_counts.append(len(fit["critical_points"]))
        if retain_models:
            local_points = np.asarray([fit["critical_points"], *points])
            record["critical_intervals"] = (lower+span*np.column_stack((local_points.min(axis=0),
                local_points.max(axis=0)))).tolist() if len(fit["critical_points"]) else []
        all_points.extend([fit["critical_points"], *points])
        record.update(resolved=True, reason="resolved finite-resolution scalar map")
    if len(nominal_counts) != len(variants) or len(set(nominal_counts)) != 1:
        return {**result, "reason": "not all declared variants resolve with the same branch count"}
    k = nominal_counts[0]
    if k:
        points = np.asarray(all_points)
        intervals = np.column_stack((points.min(axis=0), points.max(axis=0)))
        result["normalized_critical_intervals"] = intervals.tolist()
        result["critical_intervals"] = (lower+span*intervals).tolist()
        if np.any(np.ptp(intervals, axis=1) > options.maximum_critical_span):
            return {**result, "reason": "critical-location envelope too wide"}
    else:
        result["normalized_critical_intervals"] = []
    return {**result, "resolved": True, "branch_count": k+1,
            "reason": "resolved finite-resolution scalar map"}
