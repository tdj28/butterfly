"""Joint finite-resolution decisions and all-point critical-proximity matrices.

No field integration, historical alphabet, reference loading or target authority.
Inputs are the already-audited fixed-cohort map results, not chosen best fits.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import BSpline

from .paired_replay import coordinate_blocks
from .seed_return_map import MapOptions, VARIANTS, audit_map


def primary_keys(profiles, window_count):
    return [f"{p}/window-{w}" for p in profiles for w in range(window_count)]


def joint_primary(audits, expected_keys, cohort, *, variants=VARIANTS, maximum_span=.04):
    """Require the whole declared grid; no best-window/profile selection."""
    keys = list(expected_keys)
    if not keys or len(set(keys)) != len(keys) or set(audits) != set(keys):
        raise ValueError("exact complete primary audit grid required")
    if not np.isfinite(maximum_span) or not 0 < maximum_span <= 1:
        raise ValueError("invalid joint critical-span threshold")
    variants = tuple(tuple(v) for v in variants)
    if not variants or len(set(variants)) != len(variants):
        raise ValueError("nonempty distinct variant family required")
    result = {"resolved": False, "primary_keys": keys, "branch_count": None, "critical_intervals": [],
              "variants": [list(v) for v in variants],
              "maximum_span_threshold": maximum_span, "reason": "joint population gate failed"}
    if cohort["joint_population_passed"] is not True:
        return result
    results = [audits[k] for k in keys]
    if not all(a["resolved"] is True for a in results):
        return {**result, "reason": "one or more primary maps unresolved"}
    for a in results:
        if ([(r["bins"], r["smoothing"]) for r in a["variants"]] != list(variants)
                or not all(r["resolved"] is True for r in a["variants"])
                or type(a["branch_count"]) is not int or a["branch_count"] < 1):
            raise ValueError("primary map lacks the exact resolved variant family")
    counts = [a["branch_count"] for a in results]
    if len(set(counts)) != 1:
        return {**result, "reason": "primary branch counts disagree", "branch_counts": counts}
    k = counts[0]-1
    bounds = np.asarray([a["calibration_bounds"] for a in results], float)
    if bounds.shape != (len(results), 2) or not np.isfinite(bounds).all() or np.any(bounds[:, 0] >= bounds[:, 1]):
        raise ValueError("invalid calibration bounds")
    domain = [float(bounds[:, 0].min()), float(bounds[:, 1].max())]
    intervals = []
    for a in results:
        values = np.asarray(a["critical_intervals"], float).reshape(-1, 2)
        if values.shape != (k, 2) or not np.isfinite(values).all() or np.any(values[:, 0] > values[:, 1]):
            raise ValueError("critical intervals differ from resolved branch count")
        if k > 1 and np.any(values[1:, 0] <= values[:-1, 1]):
            return {**result, "reason": "ordered critical regions overlap"}
        intervals.append(values)
    combined = np.column_stack((np.min(intervals, axis=0)[:, 0], np.max(intervals, axis=0)[:, 1])) if k else np.empty((0, 2))
    spans = (combined[:, 1]-combined[:, 0])/(domain[1]-domain[0])
    result.update(calibration_domain=domain, critical_intervals=combined.tolist(), normalized_spans=spans.tolist())
    if np.any(spans > maximum_span):
        return {**result, "reason": "critical regions unstable across windows/profiles"}
    if k > 1 and np.any(combined[1:, 0] <= combined[:-1, 1]):
        return {**result, "reason": "joint ordered critical regions overlap"}
    return {**result, "resolved": True, "branch_count": k+1, "reason": "joint finite-resolution primary map resolved"}


def _model(record):
    payload = record["model"]
    knots, coefficients = np.asarray(payload["knots"], float), np.asarray(payload["coefficients"], float)
    occupied = np.asarray(payload["occupied_bins"])
    if (payload["degree"] != 3 or knots.ndim != 1 or coefficients.ndim != 1 or len(coefficients) < 4
            or len(knots) != len(coefficients)+4 or not np.isfinite(knots).all() or not np.isfinite(coefficients).all()
            or np.any(np.diff(knots) < 0) or occupied.shape != (record["bins"],) or occupied.dtype.kind != "b"
            or not np.array_equal([knots[3], knots[-4]], record["normalized_domain"])):
        raise ValueError("invalid retained calibration spline")
    return BSpline(knots, coefficients, 3, extrapolate=False), occupied


def critical_matrix(joint, audits, orbit_values, *, interval_padding=.01, maximum_slope=.02):
    """All orbit points by all ordered regions, requiring every primary model.

    No refitting or nearest-point selection occurs. Out-of-support points keep
    distances but have null slopes and cannot pass. Empty turning sets are not
    failures of a monotone scalar map and cannot become a criticality claim.
    """
    if joint["resolved"] is not True:
        return {"status": "not-evaluated", "reason": "joint primary map did not qualify"}
    keys = joint["primary_keys"]
    if set(audits) != set(keys):
        raise ValueError("critical matrix requires the complete primary map grid")
    # Recompute structural gates, so removed variants or changed region
    # envelopes cannot silently weaken an earlier complete-grid decision.
    checked = joint_primary(audits, keys, {"joint_population_passed": True},
                            variants=joint["variants"], maximum_span=joint["maximum_span_threshold"])
    if checked != joint:
        raise ValueError("primary maps changed after joint decision")
    points = np.asarray(orbit_values, float)
    if points.ndim != 1 or not len(points) or not np.isfinite(points).all():
        raise ValueError("all finite ordered reference-orbit coordinates required")
    if (not np.isfinite([interval_padding, maximum_slope]).all() or interval_padding < 0 or maximum_slope < 0):
        raise ValueError("invalid critical-proximity thresholds")
    k = joint["branch_count"]-1
    matched = np.ones((len(points), k), bool)
    details = []
    for key in keys:
        audit = audits[key]
        if audit["resolved"] is not True or audit["branch_count"] != k+1:
            raise ValueError("primary map changed after joint decision")
        lower, upper = audit["calibration_bounds"]
        span = upper-lower
        normalized = (points-lower)/span
        if not np.isfinite(normalized).all():
            raise ValueError("nonfinite normalized orbit coordinates")
        for index, record in enumerate(audit["variants"]):
            spline, occupied = _model(record)
            intervals = np.asarray(record["critical_intervals"], float).reshape(-1, 2)
            if intervals.shape != (k, 2) or not np.isfinite(intervals).all() or np.any(intervals[:, 0] > intervals[:, 1]):
                raise ValueError("missing per-variant bootstrap regions")
            lo, hi = record["normalized_domain"]
            # Bound before integer conversion to avoid overflow for remote points.
            bins = np.floor(np.clip(normalized, 0, 1)*record["bins"]).astype(int).clip(0, record["bins"]-1)
            supported = (normalized >= lo) & (normalized <= hi) & occupied[bins]
            slopes = np.full(len(points), np.nan)
            slopes[supported] = spline.derivative()(normalized[supported])
            if not np.isfinite(slopes[supported]).all():
                raise ValueError("nonfinite in-support spline derivative")
            distances = np.maximum(np.maximum(intervals[:, 0][None, :]-points[:, None],
                                              points[:, None]-intervals[:, 1][None, :]), 0)/span
            near = ((distances <= interval_padding) & supported[:, None]
                    & (np.abs(slopes[:, None]) <= maximum_slope))
            matched &= near
            details.append({"primary_key": key, "variant_index": index, "bins": record["bins"],
                "smoothing": record["smoothing"], "calibration_bounds": [lower, upper],
                "critical_intervals": intervals.tolist(), "normalized_distances": distances.tolist(),
                "supported": supported.tolist(), "slopes": [float(x) if np.isfinite(x) else None for x in slopes],
                "near": near.tolist()})
    return {"status": "evaluated" if k else "no-turning-regions", "orbit_values": points.tolist(),
            "critical_region_count": k, "near_every_primary_model": matched.tolist(), "models": details,
            "interval_padding": interval_padding, "maximum_absolute_slope": maximum_slope,
            "claim_scope": "finite-resolution proximity only; no exact criticality, alphabet or symbolic-arrow verification"}


def analyze_case(profiles, profile_names, cohort, *, primary, diagnostics, options=MapOptions(), variants=VARIANTS,
                 maximum_joint_span=.04):
    """All predeclared projections/windows; diagnostics never rescue primary."""
    names = list(profile_names)
    if set(profiles) != set(names) or len(names) != 2:
        raise ValueError("exact two-profile set required")
    windows = profiles[names[0]]["windows"]
    projections = [primary, *diagnostics]
    identities = [(p["section"], p["axis"]) for p in projections]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate primary/diagnostic projection")
    results = []
    primary_audits = {}
    for projection_index, projection in enumerate(projections):
        audits = {}
        for name in names:
            for window in range(len(windows)):
                blocks = coordinate_blocks(profiles[name], cohort, projection["section"], projection["axis"], window)
                audits[f"{name}/window-{window}"] = audit_map(**blocks, options=options, variants=variants,
                    retain_models=projection_index == 0)
        if projection_index == 0:
            primary_audits = audits
        results.append({"projection": projection, "role": "primary" if projection_index == 0 else "diagnostic",
                        "audits": audits})
    joint = joint_primary(primary_audits, primary_keys(names, len(windows)), cohort,
                          variants=variants, maximum_span=maximum_joint_span)
    return {"projections": results, "primary_audits": primary_audits, "joint_primary": joint,
            "historical_symbols_verified": False}
