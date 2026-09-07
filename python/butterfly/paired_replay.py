"""Bounded journal replay and global-ID cohort joins; no target entry point.

Expected bindings must come from the future authorized run manifest, not from
copying the journal under inspection. Completion alone is not source authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from . import paired_journal as journal
from .paired_sampling import SECTIONS, _ids, common_sample
from .paired_sections import EVENT_DTYPES


@dataclass(frozen=True)
class BatchExpectation:
    started_sha256: str
    terminal_sha256: str
    global_seed_ids: np.ndarray
    initial_states: np.ndarray
    config: dict
    sections: dict
    binding: dict
    recording: dict


def _canonical(value):
    return json.loads(json.dumps(value, sort_keys=True, allow_nan=False))


def replay_batch(directory, expected: BatchExpectation, windows, *, strata_per_window=4):
    """Read one externally bound, complete batch and retain all pair selections.

    No mutable survivor reindexing: raw pair indices refer to concatenated
    per-section journal deltas in commit order. NaN/-1 denote missing pairs.
    All initial seeds and their capture/failure masks remain in the result.
    """
    root = journal._safe_path(Path(directory))
    ids = _ids(expected.global_seed_ids)
    if not len(ids) or np.asarray(expected.initial_states).shape != (len(ids), 3):
        raise ValueError("nonempty expected seed/state table required")
    for name, digest in (("started.json", expected.started_sha256), ("terminal.json", expected.terminal_sha256)):
        if journal.sha256(journal._safe_path(root/name)) != digest:
            raise ValueError("journal differs from externally bound receipt")
    metadata = journal._read_json(root/"started.json")
    if (metadata["config"] != _canonical(expected.config)
            or metadata["sections"] != _canonical(expected.sections)
            or metadata["binding"] != _canonical(expected.binding)
            or {k: metadata[k] for k in ("journal_interval_steps", "maximum_snapshot_bytes")} != expected.recording
            or metadata["section_names"] != list(SECTIONS)):
        raise ValueError("journal differs from expected numerical design/source binding")
    audit = journal.audit_journal(root)
    if audit["status"] != "completed" or audit["orphan_files"] or audit["records"] < 1:
        raise ValueError("only complete audited batches may enter analysis")
    if audit["global_seed_ids"] != ids.tolist():
        raise ValueError("global seed identity/order differs from planned batch")
    seed_data = journal._arrays(journal._checked_file(root, metadata["seeds"]), metadata["maximum_snapshot_bytes"])
    if not np.array_equal(seed_data["initial_states"], expected.initial_states):
        raise ValueError("initial conditions differ from the planned seed table")
    chunks = {name: [] for name in SECTIONS}
    previous_hash, rows, final = None, [], None
    total_bytes = 0
    # A batch's total raw event cap bounds concatenation, even when each
    # snapshot fits individually. States/checkpoints are read one block at a time.
    maximum_event_bytes = metadata["config"]["maximum_events"] * 160
    for index in range(audit["records"]):
        path = root/f"journal-{index:06d}.json"
        row = journal._read_json(path)
        if row["index"] != index or row["previous_record_sha256"] != previous_hash:
            raise ValueError("journal commit chain changed during replay")
        raw_path = journal._checked_file(root, row["raw"])
        data = journal._arrays(raw_path, metadata["maximum_snapshot_bytes"])
        if journal.sha256(raw_path) != row["raw"]["sha256"]:
            raise ValueError("raw snapshot changed during replay")
        for section_index, name in enumerate(SECTIONS):
            prefix = f"section_{section_index}__"
            event = {k: data[prefix+k] for k in (*EVENT_DTYPES, "global_seed_ids")}
            total_bytes += sum(v.nbytes for v in event.values())
            if total_bytes > maximum_event_bytes:
                raise ValueError("batch replay exceeds declared raw event bound")
            chunks[name].append(event)
        final = {key: data[key] for key in journal.STATE_KEYS}
        previous_hash = journal.sha256(path)
        rows.append({"record": path.name, "record_sha256": previous_hash, "raw": row["raw"]})
    if previous_hash != audit["last_record_sha256"]:
        raise ValueError("journal terminal chain changed during replay")
    events = {name: {k: np.concatenate([chunk[k] for chunk in chunks[name]])
                    for k in (*EVENT_DTYPES, "global_seed_ids")} for name in SECTIONS}
    if any(len(events[n]["times"]) != audit["event_counts"][n] for n in SECTIONS):
        raise ValueError("replayed event counts differ from journal audit")
    sample = common_sample(ids, final, events, windows, horizon=metadata["config"]["horizon"],
                           strata_per_window=strata_per_window)
    pair_states, pair_times = {}, {}
    for name in SECTIONS:
        indices = sample["section_pair_indices"][name]
        valid = indices >= 0
        states = np.full((*indices.shape, 3), np.nan)
        times = np.full(indices.shape, np.nan)
        states[valid] = events[name]["states"][indices[valid]]
        times[valid] = events[name]["times"][indices[valid]]
        pair_states[name], pair_times[name] = states, times
    # Recheck committed metadata and audit after all reads. This is a read-only
    # offline integrity check, not a filesystem lock against a hostile writer.
    if (journal.sha256(root/"started.json") != expected.started_sha256
            or journal.sha256(root/"terminal.json") != expected.terminal_sha256
            or journal.audit_journal(root) != audit):
        raise ValueError("journal changed while replaying")
    return {**sample, "initial_states": seed_data["initial_states"], "state": final,
            "pair_states": pair_states, "pair_times": pair_times,
            "windows": np.asarray(windows, float), "horizon": metadata["config"]["horizon"],
            "binding": metadata["binding"], "source": {"started_sha256": expected.started_sha256,
            "terminal_sha256": expected.terminal_sha256, "records": rows}}


def assemble_profile(batches, expected_batch_ids, global_seed_ids, initial_states):
    """Join a complete planned batch set into original global seed order."""
    ids = _ids(global_seed_ids)
    planned = list(expected_batch_ids)
    initial = np.asarray(initial_states)
    if (not len(ids) or initial.shape != (len(ids), 3) or not planned or len(set(planned)) != len(planned)
            or set(batches) != set(planned)):
        raise ValueError("exact planned batch set and global seed table required")
    ordered = [batches[name] for name in planned]
    keys = ("candidate_id", "profile", "source_commit", "plan_sha256")
    binding = {k: ordered[0]["binding"][k] for k in keys}
    for name, batch in zip(planned, ordered, strict=True):
        if batch["binding"].get("trial_id") != name or {k: batch["binding"][k] for k in keys} != binding:
            raise ValueError("batch identity/candidate/profile/source binding mismatch")
    joined_ids = np.concatenate([b["global_seed_ids"] for b in ordered])
    _ids(joined_ids)
    if set(joined_ids.tolist()) != set(ids.tolist()):
        raise ValueError("missing or substituted global seeds across batches")
    positions = {int(seed): i for i, seed in enumerate(joined_ids)}
    order = np.array([positions[int(seed)] for seed in ids])
    def join(values):
        return np.concatenate(values)[order]
    if not np.array_equal(join([b["initial_states"] for b in ordered]), initial):
        raise ValueError("joined states differ from fixed global seed table")
    windows, horizon = ordered[0]["windows"], ordered[0]["horizon"]
    for b in ordered:
        if not np.array_equal(b["windows"], windows) or b["horizon"] != horizon:
            raise ValueError("batches do not share physical windows/horizon")
    counts = {key: sum(b["counts"][key] for b in ordered) for key in ordered[0]["counts"]}
    batch_index = join([np.full(len(b["global_seed_ids"]), i, np.int64) for i, b in enumerate(ordered)])
    return {"global_seed_ids": ids, "initial_states": initial.copy(), "windows": windows.copy(), "horizon": horizon,
            "retained": join([b["retained"] for b in ordered]), "counts": counts,
            "pair_states": {n: join([b["pair_states"][n] for b in ordered]) for n in SECTIONS},
            "pair_times": {n: join([b["pair_times"][n] for b in ordered]) for n in SECTIONS},
            "section_pair_indices": {n: join([b["section_pair_indices"][n] for b in ordered]) for n in SECTIONS},
            "section_eligible_counts": {n: join([b["section_eligible_counts"][n] for b in ordered]) for n in SECTIONS},
            "state": {key: join([b["state"][key] for b in ordered]) for key in journal.STATE_KEYS},
            "seed_batch_index": batch_index, "batch_ids": planned,
            "sources": [b["source"] for b in ordered], "binding": binding}


def intersect_profiles(profiles, expected_profiles, global_seed_ids, holdout, *, minimum_seeds=256, maximum_disagreement=.03):
    """Same fixed seed cohort in both profiles; failures remain explicit."""
    ids, split = _ids(global_seed_ids), np.asarray(holdout)
    names = list(expected_profiles)
    if (len(names) != 2 or len(set(names)) != 2 or set(profiles) != set(names)
            or split.shape != (len(ids),) or split.dtype.kind != "b" or not len(ids)
            or type(minimum_seeds) is not int or minimum_seeds < 1
            or not np.isfinite(maximum_disagreement) or not 0 <= maximum_disagreement <= 1):
        raise ValueError("two exact profiles, fixed split and valid cohort thresholds required")
    reference = profiles[names[0]]
    for name, p in profiles.items():
        if (not np.array_equal(p["global_seed_ids"], ids)
                or p["binding"]["profile"] != name
                or any(p["binding"][k] != reference["binding"][k] for k in ("candidate_id", "source_commit", "plan_sha256"))
                or not np.array_equal(p["initial_states"], reference["initial_states"])
                or not np.array_equal(p["windows"], reference["windows"])
                or p["horizon"] != reference["horizon"] or p["retained"].shape != (len(ids),)
                or p["retained"].dtype.kind != "b"):
            raise ValueError("profile populations or physical windows differ")
        counts = p["counts"]
        categories = {"failed", "ambiguous_nonfailed", "historical_only", "barrio_only",
                      "both", "neither_insufficient", "retained"}
        if (set(counts) != categories | {"total"}
                or any(type(v) is not int or v < 0 for v in counts.values())
                or counts["total"] != len(ids) or counts["retained"] != int(p["retained"].sum())
                or sum(counts[k] for k in categories) != len(ids)):
            raise ValueError("profile population counts differ from retained mask or input size")
    a, b = (profiles[n]["retained"] for n in names)
    retained, disagreement = a & b, float(np.mean(a != b))
    calibration, validation = retained & ~split, retained & split
    supported = min(int(calibration.sum()), int(validation.sum())) >= minimum_seeds
    return {"global_seed_ids": ids, "holdout": split.copy(), "retained": retained,
            "calibration": calibration, "validation": validation,
            "profile_counts": {n: profiles[n]["counts"] for n in names},
            "intersection_loss": {n: int((profiles[n]["retained"] & ~retained).sum()) for n in names},
            "disagreement_fraction": disagreement, "retention_compatible": disagreement <= maximum_disagreement,
            "calibration_seeds": int(calibration.sum()), "validation_seeds": int(validation.sum()),
            "sufficient_seeds": supported, "joint_population_passed": supported and disagreement <= maximum_disagreement}


def coordinate_blocks(profile, cohort, section, axis, window):
    """Extract only original selected pairs; verify finite complete blocks."""
    if section not in SECTIONS or type(axis) is not int or axis not in (0, 1, 2):
        raise ValueError("known section and scalar axis required")
    if not np.array_equal(profile["global_seed_ids"], cohort["global_seed_ids"]):
        raise ValueError("cohort/global seed order differs")
    points = profile["pair_states"][section]
    if type(window) is not int or not 0 <= window < points.shape[1]:
        raise ValueError("unknown observation window")
    blocks = points[:, window, :, :, axis]
    cal, val = blocks[cohort["calibration"]], blocks[cohort["validation"]]
    if not np.isfinite(cal).all() or not np.isfinite(val).all():
        raise ValueError("retained cohort contains missing/nonfinite pairs")
    return {"calibration": cal, "validation": val,
            "calibration_ids": profile["global_seed_ids"][cohort["calibration"]],
            "validation_ids": profile["global_seed_ids"][cohort["validation"]]}
