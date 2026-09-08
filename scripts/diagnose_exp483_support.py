#!/usr/bin/env python3
"""EXP-483: descriptive support diagnosis from authenticated EXP-482 journals.

No integration, alternative model fit, changed verdict, paid service or target resampling.
The CLI has a 600-second wall-time bound and a fresh EXP-483 output directory.
"""
import argparse
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.paired_input_package import load_package
from butterfly.paired_inputs import load_references
from butterfly.paired_phases import from_reference_audit, _expectation
from butterfly.paired_replay import read_batch
from butterfly.paired_sampling import SECTIONS
from scripts import summarize_exp482_maps as original

BINS = (30, 40, 50)
GROUPS = ("failed", "ambiguous_nonfailed", "historical_only", "barrio_only",
          "both", "neither_insufficient", "retained")


def pairs_in_window(events, window, *, first_per_stratum=False, strata=4):
    """True consecutive accepted returns; reject a seed with any ambiguous root.

    Normal rejected roots are not accepted-section returns. Window membership
    is start <= source < end and target <= end; no interpolation or bridging.
    """
    ids = np.asarray(events["global_seed_ids"])
    times = np.asarray(events["times"])
    accepted = np.asarray(events["accepted"])
    ambiguous = np.asarray(events["gate_unresolved"]) | np.asarray(events["orientation_unresolved"])
    values = np.asarray(events["states"])
    start, end = window
    if (ids.ndim != 1 or ids.dtype.kind not in "iu" or np.any(ids < 0)
            or times.shape != ids.shape or accepted.shape != ids.shape
            or ambiguous.shape != ids.shape or values.shape != (len(ids), 3)
            or accepted.dtype.kind != "b" or ambiguous.dtype.kind != "b"
            or not np.isfinite(times).all() or not np.isfinite(values).all()
            or not np.isfinite([start, end]).all() or start >= end
            or type(strata) is not int or strata < 1):
        raise ValueError("invalid raw event/window inputs")
    order = np.argsort(ids, kind="stable")
    unique, offsets, counts = np.unique(ids[order], return_index=True, return_counts=True)
    pieces = []
    edges = np.linspace(start, end, strata+1)
    for seed, offset, count in zip(unique, offsets, counts, strict=True):
        indices = order[offset:offset+count]
        if np.any(np.diff(times[indices]) <= 0):
            raise ValueError("raw event times must increase within each seed")
        if ambiguous[indices].any():
            continue
        good = indices[accepted[indices]]
        left, right = good[:-1], good[1:]
        keep = (times[left] >= start) & (times[left] < end) & (times[right] <= end)
        left, right = left[keep], right[keep]
        if first_per_stratum:
            chosen = []
            for low, high in zip(edges[:-1], edges[1:]):
                match = np.flatnonzero((times[left] >= low) & (times[left] < high))
                if len(match):
                    chosen.append(match[0])
            left, right = left[chosen], right[chosen]
        if len(left):
            pieces.append((np.full(len(left), seed, np.int64),
                           np.column_stack((times[left], times[right])),
                           np.column_stack((values[left, 0], values[right, 0]))))
    if not pieces:
        return dict(ids=np.empty(0, np.int64), times=np.empty((0, 2)), values=np.empty((0, 2)))
    return {key: np.concatenate([p[i] for p in pieces]) for i, key in enumerate(("ids", "times", "values"))}


def occupancy(values, ids, population_ids, bounds, bins):
    """Seed occupancy, not pair weights; never clip new out-of-range data in.

    Counts include zero-pair population members in the pair-count distribution.
    Bounds are always the original common-cohort calibration bounds.
    """
    values, ids, population_ids = np.asarray(values), np.asarray(ids), np.asarray(population_ids)
    lower, upper = bounds
    if (values.shape != (len(ids), 2) or not np.isfinite(values).all()
            or len(np.unique(population_ids)) != len(population_ids)
            or not np.isin(ids, population_ids).all() or upper <= lower or bins < 1):
        raise ValueError("invalid occupancy inputs")
    x = (values[:, 0]-lower)/(upper-lower)
    inside = (x >= 0) & (x <= 1)
    assigned = np.clip(np.floor(x[inside]*bins).astype(int), 0, bins-1)
    in_ids = ids[inside]
    counts = np.array([len(np.unique(in_ids[assigned == b])) for b in range(bins)])
    unique, frequencies = np.unique(ids, return_counts=True)
    lookup = dict(zip(unique.tolist(), frequencies.tolist()))
    per_seed = np.array([lookup.get(int(i), 0) for i in population_ids])
    histogram = {str(int(n)): int((per_seed == n).sum()) for n in np.unique(per_seed)}
    return dict(population_seeds=len(population_ids), observed_seeds=len(unique), pairs=len(ids),
        pairs_per_seed_histogram=histogram, pairs_outside_original_bounds=int((~inside).sum()),
        distinct_seeds_per_bin=counts.tolist(), zero_seed_bins=int((counts == 0).sum()),
        one_to_seven_seed_bins=int(((counts > 0) & (counts < 8)).sum()),
        at_least_eight_seed_bins=int((counts >= 8).sum()), coverage=float(np.mean(counts >= 8)),
        observed_input_range=[float(values[:, 0].min()), float(values[:, 0].max())] if len(ids) else None)


def unsupported_parts(values, bounds, variant):
    """Disjoint original heldout gate decomposition, only for an existing model."""
    if "model" not in variant:
        return dict(status="not-evaluated", reason=variant["reason"])
    x = (np.asarray(values)[:, 0]-bounds[0])/(bounds[1]-bounds[0])
    lo, hi = variant["normalized_domain"]
    outside = (x < lo) | (x > hi)
    assigned = np.clip(np.floor(x*variant["bins"]).astype(int), 0, variant["bins"]-1)
    sparse_inside = ~outside & ~np.asarray(variant["model"]["occupied_bins"], bool)[assigned]
    supported = ~(outside | sparse_inside)
    fraction = float(1-supported.mean())
    if fraction != variant["heldout_unsupported_fraction"]:
        raise ValueError("heldout decomposition differs from original gate")
    return dict(status="evaluated", pairs=len(x), outside_fitted_interval=int(outside.sum()),
        inside_interval_unsupported_bin=int(sparse_inside.sum()), supported=int(supported.sum()),
        unsupported_fraction=fraction, normalized_fitted_interval=[lo, hi])


def populations(profile):
    state = profile["state"]
    failed = state["failed"]
    ambiguous = np.any(state["ambiguous"], axis=1)
    valid = ~failed & ~ambiguous
    captured = np.isfinite(state["capture_times"])
    hist, barrio = captured.T
    result = dict(failed=failed, ambiguous_nonfailed=~failed & ambiguous,
        historical_only=valid & hist & ~barrio, barrio_only=valid & ~hist & barrio,
        both=valid & hist & barrio, neither_insufficient=valid & ~captured.any(axis=1) & ~profile["retained"],
        retained=profile["retained"])
    if not np.all(sum(mask.astype(int) for mask in result.values()) == 1):
        raise ValueError("capture groups are not a disjoint partition")
    if any(int(result[key].sum()) != profile["counts"][key] for key in GROUPS):
        raise ValueError("capture groups do not reproduce original counts")
    return result, valid


def capture_phase(times, capture_times):
    first = np.min(np.where(np.isfinite(capture_times), capture_times, np.inf), axis=1)
    return dict(before_detection=times[:, 1] < first,
                straddling_detection=(times[:, 0] < first) & (times[:, 1] >= first),
                at_or_after_detection=times[:, 0] >= first)


def diagnose():
    audited, profiles, analysis = original.audit()
    pre = json.loads((original.RUN/"preflight/receipt.json").read_bytes())
    plan = load_package(original.RUN/"preflight/inputs", pre["inputs"]["sha256"])
    design, _ = from_reference_audit(plan, load_references(plan, original.RUN/"preflight/inputs"),
        source_commit=original.SOURCE, plan_sha256=pre["plan_sha256"])
    grid = design.validate()
    rows, decompositions, timing = [], [], []
    for case, case_profiles in profiles.items():
        cohort = analysis["cases"][case]["cohort"]
        common = np.asarray(cohort["retained"], bool)
        split = np.asarray(cohort["holdout"], bool)
        for name, profile in case_profiles.items():
            all_ids = profile["global_seed_ids"]
            positions = {int(seed): i for i, seed in enumerate(all_ids)}
            groups, valid = populations(profile)
            pieces = {(w, selector): [] for w in range(2) for selector in ("selected", "all")}
            for trial in grid:
                if trial.stage != "collection" or trial.candidate_id != case or trial.profile != name:
                    continue
                source = original.RUN/"campaign/collection/phase"
                recorded = json.loads((source/"receipts"/(trial.trial_id+".json")).read_bytes())
                raw = read_batch(source/"trials"/trial.trial_id, _expectation(design, trial, recorded))
                for (w, selector), chunks in pieces.items():
                    chunks.append(pairs_in_window(raw["events"][SECTIONS[0]], profile["windows"][w],
                        first_per_stratum=selector == "selected"))
            for (w, selector), chunks in pieces.items():
                data = {key: np.concatenate([c[key] for c in chunks]) for key in ("ids", "times", "values")}
                # Batch order is frozen, but assert/reorder by the original global IDs explicitly.
                index = np.array([positions[int(seed)] for seed in data["ids"]], dtype=int)
                order = np.argsort(index, kind="stable")
                index = index[order]
                data = {key: value[order] for key, value in data.items()}
                aud = analysis["cases"][case]["analysis"]["primary_audits"][f"{name}/window-{w}"]
                bounds = aud["calibration_bounds"]
                if selector == "selected":
                    keep = common[index]
                    if (not np.array_equal(data["ids"][keep], np.repeat(all_ids[common], 4))
                            or not np.array_equal(data["values"][keep], profile["pair_states"][SECTIONS[0]][common, w, ..., 0].reshape(-1, 2))
                            or not np.array_equal(data["times"][keep], profile["pair_times"][SECTIONS[0]][common, w].reshape(-1, 2))):
                        raise ValueError("independent selector differs from original common-cohort pairs")
                    val = data["values"][keep & split[index]]
                    for variant in aud["variants"]:
                        decompositions.append(dict(case=case, profile=name, window=w, bins=variant["bins"],
                            smoothing=variant["smoothing"], **unsupported_parts(val, bounds, variant)))
                phases = capture_phase(data["times"], profile["state"]["capture_times"][index])
                for group, mask in groups.items():
                    timing.append(dict(case=case, profile=name, window=w, selector=selector, group=group,
                        population_seeds=int(mask.sum()), eligible_valid_pairs=int((mask[index] & valid[index]).sum()),
                        **{phase: int((mask[index] & valid[index] & keep).sum()) for phase, keep in phases.items()}))
                comparators = {**groups, "joint_original_cohort": common, "valid_before_detection": valid}
                for group, mask in comparators.items():
                    for label, split_mask in (("calibration", ~split), ("heldout", split)):
                        population_ids = all_ids[mask & split_mask]
                        keep = mask[index] & split_mask[index] & valid[index]
                        if group == "valid_before_detection":
                            keep &= phases["before_detection"]
                        for bins in BINS:
                            stats = occupancy(data["values"][keep], data["ids"][keep], population_ids, bounds, bins)
                            if group == "joint_original_cohort" and selector == "selected" and label == "calibration":
                                variant = next(v for v in aud["variants"] if v["bins"] == bins)
                                if stats["coverage"] != variant["coverage"]:
                                    raise ValueError("original calibration coverage not reproduced")
                            rows.append(dict(case=case, profile=name, window=w, selector=selector,
                                population=group, split=label, bins=bins, original_calibration_bounds=bounds, **stats))
            print(f"support and conditioning complete: {case} {name}", flush=True)
    receipt = json.loads((original.RUN/"campaign/receipt.json").read_bytes())
    if (sha256(original.RUN/"campaign/receipt.json") != original.CAMPAIGN_SHA
            or inventory(original.RUN/"campaign", omit=("receipt.json",)) != receipt["files"]):
        raise ValueError("preserved campaign changed during diagnostic")
    return dict(experiment_id="EXP-483", status="descriptive-diagnostic-completed",
        campaign_sha256=original.CAMPAIGN_SHA, original_analysis_sha256=original.ANALYSIS_SHA,
        raw_replay_and_original_analysis_exact=audited["all_raw_collection_and_analysis_replay_exact"],
        independent_common_pair_selector_exact=True, full_inventory_verified_before_and_after=True,
        projection=dict(section=SECTIONS[0], axis="x"), rows=rows,
        heldout_decomposition=decompositions, capture_timing=timing,
        group_semantics="Seven named groups partition each profile. Joint cohort and valid_before_detection are overlapping comparators, not additive groups.",
        capture_semantics="Detection time is the fifth qualifying reference crossing, not a proven onset of attraction. Before-detection pairs may already approach a reference; uncaptured finite paths are not invariant chaotic orbits.",
        scope="Descriptive, outcome-informed sampling diagnosis; unequal all-pair weights, no alternative refit or new qualification. Original fits replayed for integrity only. EXP-482 unresolved; flow chains and homoclinicity remain unverified.",
        paid_review="not_run", new_integrations=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-483" not in output.parents:
        parser.error("fresh output must be beneath artifacts/EXP-483")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        parser.error("commit diagnostic implementation before execution")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    def timeout(*_):
        raise TimeoutError("600-second diagnostic wall-time limit")
    previous = signal.signal(signal.SIGALRM, timeout)
    signal.alarm(600)
    try:
        result = diagnose()
        result.update(diagnostic_source_commit=commit, diagnostic_script_sha256=sha256(Path(__file__)),
            elapsed_seconds=time.monotonic()-started, wall_limit_seconds=600,
            batch_raw_event_limit="Inherited authenticated 262144 events per batch; batches streamed individually")
        write_json(output/"summary.json", result)
        print(json.dumps(dict(status=result["status"], rows=len(result["rows"]),
            summary_sha256=sha256(output/"summary.json"), elapsed_seconds=result["elapsed_seconds"])))
    except (Exception, KeyboardInterrupt) as error:
        write_json(output/"failure.json", dict(status="diagnostic-failed", source_commit=commit,
            error_type=type(error).__name__, message=str(error), elapsed_seconds=time.monotonic()-started))
        raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    main()
