"""Outcome-free seed construction and paired-section sample selection.

This module does not integrate a field, infer a partition or authorize targets.
All IDs are fixed before capture; rows from a seed are one sampling unit.
"""
from __future__ import annotations

import hashlib
import numpy as np

SECTIONS = ("historical-negative", "barrio-positive")


def seed_table(count=8192, *, random_seed=481001):
    """IID uniform x,z coordinates in the prior sampling rectangle, new draw.

    Half the fixed IDs are calibration and half holdout, independently of state.
    y is supplied later from each candidate's historical section, not sampled.
    """
    if type(count) is not int or count < 2 or count % 2 or type(random_seed) is not int or random_seed < 0:
        raise ValueError("positive even count and nonnegative integer seed required")
    coordinates = np.random.Generator(np.random.PCG64(random_seed)).random((count, 2))
    coordinates = [-14., .008] + coordinates * np.array([13.8, .542])
    return {"global_seed_ids": np.arange(count, dtype=np.int64), "xz": coordinates,
            "holdout": np.arange(count) >= count//2}


def seed_commitment(table):
    """Portable ordered commitment, independent of NPZ timestamp/container."""
    digest = hashlib.sha256(b"butterfly.paired-seeds.v1\0")
    for key, dtype in (("global_seed_ids", "<i8"), ("xz", "<f8"), ("holdout", "u1")):
        array = np.asarray(table[key], dtype=dtype, order="C")
        digest.update(key.encode()+b"\0")
        digest.update(np.asarray(array.shape, dtype="<i8").tobytes())
        digest.update(array.tobytes())
    return digest.hexdigest()


def _ids(values):
    ids = np.asarray(values)
    if (ids.ndim != 1 or ids.dtype.kind not in "iu" or np.any(ids < 0)
            or np.any(ids > np.iinfo(np.int64).max) or len(np.unique(ids)) != len(ids)):
        raise ValueError("unique nonnegative global seed IDs required")
    return ids.astype(np.int64)


def section_pairs(events, global_seed_ids, windows, *, strata_per_window=4):
    """One true consecutive accepted pair per physical-time source stratum.

    Select the first eligible pair in each stratum. Both endpoints must be
    inside its observation window; strata partition the SOURCE time only.
    Opposite-direction/gate-rejected roots are not returns to this section.
    An unresolved root invalidates the entire seed here (no bridging). Event
    indices point into the original unfiltered raw arrays for exact replay.
    """
    ids = _ids(global_seed_ids)
    windows = np.asarray(windows, dtype=float)
    if (windows.ndim != 2 or windows.shape[1] != 2 or not len(windows)
            or not np.isfinite(windows).all() or np.any(windows[:, 0] < 0)
            or np.any(windows[:, 0] >= windows[:, 1])
            or np.any(windows[1:, 0] < windows[:-1, 1])
            or type(strata_per_window) is not int or strata_per_window < 1):
        raise ValueError("ordered nonoverlapping windows and positive strata required")
    required = ("global_seed_ids", "times", "states", "accepted", "gate_unresolved", "orientation_unresolved")
    if not set(required) <= set(events):
        raise ValueError("missing raw event fields")
    rows = {k: np.asarray(events[k]) for k in required}
    n = len(rows["times"])
    for key in required:
        if rows[key].shape != ((n, 3) if key == "states" else (n,)):
            raise ValueError("invalid event shape")
    if (rows["global_seed_ids"].dtype.kind not in "iu"
            or not np.isin(rows["global_seed_ids"], ids).all()
            or not np.isfinite(rows["times"]).all() or np.any(rows["times"] < 0)
            or not np.isfinite(rows["states"]).all()):
        raise ValueError("invalid event identities/finiteness")
    for key in ("accepted", "gate_unresolved", "orientation_unresolved"):
        if rows[key].dtype.kind != "b":
            raise ValueError("Boolean event flags required")
    selected = np.full((len(ids), len(windows), strata_per_window, 2), -1, dtype=np.int64)
    eligible = np.zeros((len(ids), len(windows), strata_per_window), dtype=np.int64)
    unresolved = rows["gate_unresolved"] | rows["orientation_unresolved"]
    order = np.argsort(rows["global_seed_ids"], kind="stable")
    ordered_ids = rows["global_seed_ids"][order]
    for i, seed_id in enumerate(ids):
        low, high = np.searchsorted(ordered_ids, seed_id, side="left"), np.searchsorted(ordered_ids, seed_id, side="right")
        raw = order[low:high]
        if np.any(np.diff(rows["times"][raw]) <= 0):
            raise ValueError("seed event times must be strictly increasing in raw order")
        if unresolved[raw].any():
            continue
        accepted = raw[rows["accepted"][raw]]
        left, right = accepted[:-1], accepted[1:]
        for w, (start, end) in enumerate(windows):
            for s in range(strata_per_window):
                low, high = start+(end-start)*s/strata_per_window, start+(end-start)*(s+1)/strata_per_window
                good = ((rows["times"][left] >= low) & (rows["times"][left] < high)
                        & (rows["times"][right] <= end))
                matches = np.flatnonzero(good)
                eligible[i, w, s] = len(matches)
                if len(matches):
                    first = matches[0]
                    selected[i, w, s] = left[first], right[first]
    return {"pair_indices": selected, "eligible_counts": eligible,
            "sufficient": np.all(selected >= 0, axis=(1, 2, 3))}


def common_sample(global_seed_ids, state, events, windows, *, horizon, strata_per_window=4):
    """Same finite-horizon cohort for both sections and both time windows.

    Primary population: numerically valid, unambiguous, neither section captured
    by horizon, and all declared pair strata present on both sections. This is
    conditional finite-time sampling, not a proof of a chaotic invariant set.
    """
    ids = _ids(global_seed_ids)
    if (list(events) != list(SECTIONS) or not np.isfinite(horizon) or horizon <= 0
            or np.asarray(windows).max() > horizon):
        raise ValueError("both ordered sections and a covering finite horizon required")
    values = {k: np.asarray(state[k]) for k in ("failed", "ambiguous", "capture_times")}
    for k, shape in (("failed", (len(ids),)), ("ambiguous", (len(ids), 2)), ("capture_times", (len(ids), 2))):
        if values[k].shape != shape:
            raise ValueError("state/global seed table mismatch")
    if values["failed"].dtype.kind != "b" or values["ambiguous"].dtype.kind != "b":
        raise ValueError("Boolean state masks required")
    times = values["capture_times"]
    if np.isinf(times).any() or np.any(times[np.isfinite(times)] < 0) or np.any(times[np.isfinite(times)] > horizon):
        raise ValueError("capture times outside committed horizon")
    pairs = {name: section_pairs(events[name], ids, windows, strata_per_window=strata_per_window) for name in SECTIONS}
    if any(np.any(np.asarray(e["times"]) > horizon) for e in events.values()):
        raise ValueError("raw event lies beyond the committed horizon")
    failed = values["failed"]
    raw_ambiguous_ids = np.concatenate([np.asarray(e["global_seed_ids"])[np.asarray(e["gate_unresolved"]) |
        np.asarray(e["orientation_unresolved"])] for e in events.values()])
    ambiguous = values["ambiguous"].any(axis=1) | np.isin(ids, raw_ambiguous_ids)
    captured = np.isfinite(times)
    valid = ~failed & ~ambiguous
    neither = valid & ~captured.any(axis=1)
    sufficient = np.logical_and.reduce([p["sufficient"] for p in pairs.values()])
    retained = neither & sufficient
    counts = {"total": len(ids), "failed": int(failed.sum()),
        "ambiguous_nonfailed": int((ambiguous & ~failed).sum()),
        "historical_only": int((valid & captured[:, 0] & ~captured[:, 1]).sum()),
        "barrio_only": int((valid & ~captured[:, 0] & captured[:, 1]).sum()),
        "both": int((valid & captured.all(axis=1)).sum()),
        "neither_insufficient": int((neither & ~sufficient).sum()), "retained": int(retained.sum())}
    assert sum(v for k, v in counts.items() if k != "total") == len(ids)
    return {"global_seed_ids": ids, "retained": retained, "counts": counts,
            "section_pair_indices": {n: p["pair_indices"] for n, p in pairs.items()},
            "section_eligible_counts": {n: p["eligible_counts"] for n, p in pairs.items()}}


def block_bootstrap_indices(seed_count, replicates, *, random_seed):
    """Resample whole seed blocks, never individual correlated return pairs."""
    if any(type(x) is not int or x < 1 for x in (seed_count, replicates)):
        raise ValueError("positive seed/replicate counts required")
    return np.random.Generator(np.random.PCG64(random_seed)).integers(0, seed_count, (replicates, seed_count))
