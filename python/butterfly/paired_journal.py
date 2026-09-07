"""Write-once paired-section evidence journals; no target authorization here.

Each fsynced NPZ is followed by a fsynced hash-chained JSON commit. An orphan
NPZ or absent terminal receipt cannot certify completion. No overwrite/resume,
retry, deletion, remote access, fitting, or automatic survivor selection.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
import math
import os
from pathlib import Path
import re
import zipfile

import numpy as np

from .paired_sections import CaptureSection, EVENT_DTYPES, collect_paired_sections, validate_collection
from .poincare import PoincareSection


STATE_KEYS = ("initial_states", "final_states", "failed", "failure_steps", "failure_states",
              "capture_times", "capture_streaks", "ambiguous", "initial_on_plane")


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _safe_path(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("journal paths cannot contain symlinks")
    return path


def _sync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _new_file(path, writer):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        writer(stream)
        stream.flush()
        os.fsync(stream.fileno())
    _sync_directory(path.parent)
    return {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def _json(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    return _new_file(path, lambda stream: stream.write(raw))


def _read_json(path):
    _safe_path(path)
    if path.stat().st_size > 4*1024**2:
        raise ValueError("oversized journal metadata")
    return json.loads(path.read_bytes())


def _checked_file(root, row):
    if not re.fullmatch(r"[a-z0-9-]+\.(npz|json)", row["path"]):
        raise ValueError("invalid journal filename")
    path = _safe_path(root / row["path"])
    if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
        raise ValueError("journal file hash/size mismatch")
    return path


def _arrays(path, maximum_bytes):
    # Bound declared uncompressed arrays before NumPy can allocate from a
    # malicious or corrupt NPY shape. No pickle/object arrays are accepted.
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > 10000 or len({m.filename for m in members}) != len(members):
            raise ValueError("duplicate or excessive NPZ members")
        if sum(m.file_size for m in members) > maximum_bytes:
            raise ValueError("snapshot exceeds uncompressed bound")
        declared_bytes = 0
        for member in members:
            if not re.fullmatch(r"[a-z0-9_]+\.npy", member.filename):
                raise ValueError("unsafe NPZ member")
            with archive.open(member) as stream:
                version = np.lib.format.read_magic(stream)
                if version == (1, 0):
                    shape, _, dtype = np.lib.format.read_array_header_1_0(stream)
                elif version == (2, 0):
                    shape, _, dtype = np.lib.format.read_array_header_2_0(stream)
                else:
                    raise ValueError("unsupported NPY format")
                declared_bytes += math.prod(shape)*dtype.itemsize
                if dtype.hasobject or dtype.fields or declared_bytes > maximum_bytes:
                    raise ValueError("unsafe array dtype/shape")
    with np.load(path, allow_pickle=False) as archive:
        return {k: archive[k] for k in archive.files}


def preflight(initial_states, global_seed_ids, sections, config, *, journal_interval_steps, maximum_snapshot_bytes):
    initial, _, steps, _ = validate_collection(initial_states, sections, **config)
    ids = np.asarray(global_seed_ids)
    if (ids.shape != (len(initial),) or ids.dtype.kind not in "iu" or np.any(ids < 0)
            or np.any(ids > np.iinfo(np.int64).max) or len(np.unique(ids)) != len(ids)):
        raise ValueError("unique nonnegative fixed global seed IDs required")
    if (type(journal_interval_steps) is not int or journal_interval_steps < 1
            or type(maximum_snapshot_bytes) is not int or not 4096 <= maximum_snapshot_bytes <= 512*1024**2):
        raise ValueError("invalid journal interval or byte bound")
    if maximum_snapshot_bytes < len(ids)*160 + 34*512:
        raise ValueError("byte bound cannot fit even the initial state snapshot")
    return initial.copy(), ids.astype(np.int64), steps


def _validate_arrays(arrays, initial, ids, names, start, end, dt, checkpoint_steps):
    count = len(ids)
    if not np.array_equal(arrays["global_seed_ids"], ids) or not np.array_equal(arrays["initial_states"], initial):
        raise ValueError("snapshot changed global seed table")
    for key, shape in {"initial_states": (count, 3), "final_states": (count, 3), "failed": (count,),
            "failure_steps": (count,), "failure_states": (count, 3), "capture_times": (count, 2),
            "capture_streaks": (count, 2), "ambiguous": (count, 2), "initial_on_plane": (count, 2)}.items():
        if arrays[key].shape != shape:
            raise ValueError("invalid snapshot state shape")
    if not np.isfinite(arrays["final_states"]).all():
        raise ValueError("last valid states must be finite")
    for key in ("initial_states", "final_states", "failure_states", "capture_times"):
        if arrays[key].dtype.kind != "f":
            raise ValueError("invalid floating-point state dtype")
    for key in ("failed", "ambiguous", "initial_on_plane"):
        if arrays[key].dtype.kind != "b":
            raise ValueError("invalid Boolean state mask")
    failed, failure_steps = arrays["failed"], arrays["failure_steps"]
    if (failure_steps.dtype.kind not in "iu" or np.any(failure_steps[~failed] != -1)
            or np.any(failure_steps[failed] < 0) or np.any(failure_steps[failed] > end)
            or not np.isnan(arrays["failure_states"][~failed]).all()):
        raise ValueError("failure markers disagree with failure mask")
    capture = arrays["capture_times"]
    if np.isinf(capture).any() or np.any(capture[np.isfinite(capture)] < 0) or np.any(capture[np.isfinite(capture)] > end*dt):
        raise ValueError("invalid capture-time sentinel or range")
    if arrays["capture_streaks"].dtype.kind not in "iu" or np.any(arrays["capture_streaks"] < 0):
        raise ValueError("invalid capture streaks")
    expected_keys = set(STATE_KEYS) | {"global_seed_ids"}
    prior_ambiguity = np.zeros((count, 2), dtype=bool)
    for index, step in enumerate(s for s in checkpoint_steps if s <= end):
        prefix = f"checkpoint_{index}__"
        expected_keys.update(prefix+k for k in ("step", "time", "failed", "captured", "ambiguous"))
        cp_step, cp_time = arrays[prefix+"step"], arrays[prefix+"time"]
        if (cp_step.shape != () or cp_step.dtype.kind not in "iu" or cp_step != step
                or cp_time.shape != () or cp_time.dtype.kind != "f" or cp_time != step*dt):
            raise ValueError("checkpoint step/time differs from declared schedule")
        for key, shape in (("failed", (count,)), ("captured", (count, 2)), ("ambiguous", (count, 2))):
            value = arrays[prefix+key]
            if value.shape != shape or value.dtype.kind != "b":
                raise ValueError("invalid checkpoint mask")
        if (not np.array_equal(arrays[prefix+"failed"], failed & (failure_steps <= step))
                or not np.array_equal(arrays[prefix+"captured"], np.isfinite(capture) & (capture <= step*dt))
                or np.any(prior_ambiguity & ~arrays[prefix+"ambiguous"])
                or np.any(arrays[prefix+"ambiguous"] & ~arrays["ambiguous"])
                or (step == end and not np.array_equal(arrays[prefix+"ambiguous"], arrays["ambiguous"]))):
            raise ValueError("checkpoint masks disagree with state history")
        prior_ambiguity = arrays[prefix+"ambiguous"]
    counts = {}
    for index, name in enumerate(names):
        prefix = f"section_{index}__"
        expected_keys.update(prefix+k for k in (*EVENT_DTYPES, "global_seed_ids"))
        events = {key: arrays[prefix+key] for key in EVENT_DTYPES}
        n = len(events["times"])
        for key, dtype in EVENT_DTYPES.items():
            expected = (n, 3) if key == "states" else (n,)
            if events[key].shape != expected or events[key].dtype.kind != np.dtype(dtype).kind or not np.isfinite(events[key]).all():
                raise ValueError("invalid raw event shape/dtype/finiteness")
        local = events["seed_ids"]
        if np.any(local < 0) or np.any(local >= count):
            raise ValueError("event seed outside fixed seed table")
        if not np.array_equal(arrays[prefix+"global_seed_ids"], ids[local]):
            raise ValueError("global event seed mapping changed")
        if (np.any(events["steps"] <= start) or np.any(events["steps"] > end)
                or np.any(events["times"] <= start*dt) or np.any(events["times"] > end*dt)
                or np.any(events["times"] <= (events["steps"]-1)*dt)
                or np.any(events["times"] > events["steps"]*dt)
                or np.any(~np.isin(events["orientation"], [-1, 1]))):
            raise ValueError("event outside committed delta")
        if np.any(np.diff(events["steps"]) < 0) or np.any(events["capture_distance"] < 0):
            raise ValueError("invalid event order or capture distance")
        if len(set(zip(local.tolist(), events["steps"].tolist()))) != n:
            raise ValueError("duplicate seed/step plane event")
        counts[name] = n
    if set(arrays) != expected_keys:
        raise ValueError("unexpected snapshot arrays")
    return counts


class PairedJournal:
    def __init__(self, directory, initial_states, global_seed_ids, sections, config, *, binding,
                 journal_interval_steps, maximum_snapshot_bytes=64*1024**2):
        initial, ids, steps = preflight(initial_states, global_seed_ids, sections, config,
            journal_interval_steps=journal_interval_steps, maximum_snapshot_bytes=maximum_snapshot_bytes)
        # Validate all metadata before creating files or invoking any field.
        metadata = {"schema": "butterfly.paired-journal.v1", "config": config, "binding": binding,
            "journal_interval_steps": journal_interval_steps, "maximum_snapshot_bytes": maximum_snapshot_bytes,
            "requested_steps": steps, "section_names": list(sections),
            "sections": {n: {**asdict(s), "cycle_states": np.asarray(s.cycle_states).tolist()} for n, s in sections.items()},
            "missing_value_contract": "NaN capture time means not observed; nonfailed failure_states are NaN; failed failure_states retain raw nonfinites. JSON never contains NaN.",
            "automatic_retry": False, "resume_supported": False}
        json.dumps(metadata, allow_nan=False)
        self.root = _safe_path(directory)
        self.root.mkdir(parents=True, exist_ok=False, mode=0o700)
        _sync_directory(self.root.parent)
        self.initial, self.ids, self.names = initial, ids, list(sections)
        self.config, self.steps, self.maximum_bytes = dict(config), steps, maximum_snapshot_bytes
        self.index, self.last_step, self.previous_hash = 0, 0, None
        self.write_failed, self.finished = False, False
        seed_file = _new_file(self.root / "seeds.npz", lambda stream: np.savez_compressed(stream, initial_states=initial, global_seed_ids=ids))
        metadata["seeds"] = seed_file
        _json(self.root / "started.json", metadata)

    def append(self, result):
        if self.write_failed or self.finished:
            raise ValueError("journal is failed/closed; no retry")
        try:
            if result.event_range_start_step != self.last_step or not self.last_step < result.completed_steps <= self.steps:
                raise ValueError("noncontiguous journal snapshot")
            if result.dt != self.config["dt"] or result.requested_steps != self.steps or list(result.events) != self.names:
                raise ValueError("snapshot differs from journal design")
            arrays = {k: np.asarray(getattr(result, k)) for k in STATE_KEYS}
            arrays["global_seed_ids"] = self.ids
            for index, name in enumerate(self.names):
                arrays.update({f"section_{index}__{k}": v for k, v in result.events[name].items()})
                local = result.events[name]["seed_ids"]
                if local.dtype.kind not in "iu" or np.any(local < 0) or np.any(local >= len(self.ids)):
                    raise ValueError("invalid local seed mapping")
                arrays[f"section_{index}__global_seed_ids"] = self.ids[local]
            for index, checkpoint in enumerate(result.checkpoints):
                arrays.update({f"checkpoint_{index}__{k}": np.asarray(v) for k, v in checkpoint.items()})
            checkpoints = np.rint(np.asarray(self.config["checkpoint_times"])/result.dt).astype(int)
            counts = _validate_arrays(arrays, self.initial, self.ids, self.names, self.last_step, result.completed_steps, result.dt, checkpoints)
            if sum(v.nbytes for v in arrays.values())+512*len(arrays) > self.maximum_bytes:
                raise ValueError("snapshot exceeds declared byte bound")
            stem = f"journal-{self.index:06d}"
            raw = _new_file(self.root / (stem+".npz"), lambda stream: np.savez_compressed(stream, **arrays))
            row = {"index": self.index, "start_step": self.last_step, "end_step": result.completed_steps,
                   "raw": raw, "previous_record_sha256": self.previous_hash, "event_counts": counts}
            commit = _json(self.root / (stem+".json"), row)
            self.index, self.last_step, self.previous_hash = self.index+1, result.completed_steps, commit["sha256"]
        except BaseException:
            self.write_failed = True
            raise

    def finish(self, result):
        if self.finished:
            raise ValueError("terminal receipt already written")
        if not self.write_failed and result.completed_steps > self.last_step:
            events = {n: {k: v[e["steps"] > self.last_step] for k, v in e.items()} for n, e in result.events.items()}
            self.append(replace(result, events=events, event_range_start_step=self.last_step))
        # Re-read the on-disk prefix before claiming completion.
        audit = audit_journal(self.root)
        complete = (result.status == "completed" and not self.write_failed and audit["orphan_files"] == []
                    and self.last_step == self.steps == result.completed_steps)
        terminal = {"status": "completed" if complete else "incomplete", "collector_status": result.status,
                    "collector_failure": result.failure, "collector_completed_steps": result.completed_steps,
                    "durable_steps": audit["durable_steps"], "records": audit["records"],
                    "last_record_sha256": audit["last_record_sha256"],
                    "collection_complete": complete, "write_failed": self.write_failed,
                    "scientific_qualification": False}
        _json(self.root / "terminal.json", terminal)
        self.finished = True
        return audit_journal(self.root)


def audit_journal(directory):
    root = _safe_path(directory)
    metadata = _read_json(root / "started.json")
    if metadata["schema"] != "butterfly.paired-journal.v1":
        raise ValueError("wrong journal schema")
    maximum = metadata["maximum_snapshot_bytes"]
    if type(maximum) is not int or not 4096 <= maximum <= 512*1024**2:
        raise ValueError("invalid byte limit")
    seeds = _arrays(_checked_file(root, metadata["seeds"]), maximum)
    ids, initial = seeds["global_seed_ids"], seeds["initial_states"]
    names = metadata["section_names"]
    sections = {name: CaptureSection(section=PoincareSection(**metadata["sections"][name]["section"]),
                    **{k: v for k, v in metadata["sections"][name].items() if k != "section"}) for name in names}
    _, _, steps = preflight(initial, ids, sections, metadata["config"],
        journal_interval_steps=metadata["journal_interval_steps"], maximum_snapshot_bytes=maximum)
    if steps != metadata["requested_steps"] or len(set(names)) != 2:
        raise ValueError("invalid requested horizon/section order")
    previous, end, count = None, 0, 0
    expected = {"started.json", "seeds.npz"}
    totals = {name: 0 for name in names}
    previous_arrays = None
    checkpoints = np.rint(np.asarray(metadata["config"]["checkpoint_times"])/metadata["config"]["dt"]).astype(int)
    for path in sorted(root.glob("journal-*.json")):
        row = _read_json(path)
        if (path.name != f"journal-{count:06d}.json" or row["index"] != count or row["start_step"] != end
                or not end < row["end_step"] <= metadata["requested_steps"] or row["previous_record_sha256"] != previous):
            raise ValueError("broken journal step/hash chain")
        arrays = _arrays(_checked_file(root, row["raw"]), maximum)
        counts = _validate_arrays(arrays, initial, ids, names, end, row["end_step"], metadata["config"]["dt"], checkpoints)
        if counts != row["event_counts"]:
            raise ValueError("journal event count mismatch")
        if previous_arrays is not None:
            if (np.any(previous_arrays["failed"] & ~arrays["failed"])
                    or np.any(previous_arrays["ambiguous"] & ~arrays["ambiguous"])
                    or not np.array_equal(previous_arrays["initial_on_plane"], arrays["initial_on_plane"])):
                raise ValueError("lost prior failure/ambiguity/initial-plane flags")
            captured = np.isfinite(previous_arrays["capture_times"])
            if not np.array_equal(previous_arrays["capture_times"][captured], arrays["capture_times"][captured]):
                raise ValueError("lost or changed first capture time")
            previously_failed = previous_arrays["failed"]
            for key in ("failure_steps", "failure_states", "final_states"):
                if not np.array_equal(previous_arrays[key][previously_failed], arrays[key][previously_failed], equal_nan=True):
                    raise ValueError("changed previously failed trajectory record")
            for key in previous_arrays:
                if key.startswith("checkpoint_") and not np.array_equal(previous_arrays[key], arrays[key]):
                    raise ValueError("changed previously committed checkpoint")
        previous_arrays = arrays
        for name in totals:
            totals[name] += counts[name]
        end, previous, count = row["end_step"], sha256(path), count+1
        expected.update((path.name, row["raw"]["path"]))
    if sum(totals.values()) > metadata["config"]["maximum_events"]:
        raise ValueError("journal exceeds total event bound")
    terminal = None
    if (root / "terminal.json").exists():
        terminal = _read_json(root / "terminal.json")
        expected.add("terminal.json")
        if terminal["durable_steps"] != end or terminal["records"] != count or terminal["last_record_sha256"] != previous:
            raise ValueError("terminal receipt differs from durable prefix")
    orphans = sorted(p.name for p in root.iterdir() if p.name not in expected)
    complete = bool(terminal and terminal["collection_complete"] is True)
    if complete and (orphans or end != metadata["requested_steps"] or terminal["status"] != "completed"
                     or terminal["collector_completed_steps"] != end
                     or terminal["collector_status"] != "completed" or terminal["write_failed"] is not False):
        raise ValueError("invalid completion claim")
    return {"status": "completed" if complete else "incomplete", "durable_steps": end,
            "records": count, "event_counts": totals, "orphan_files": orphans,
            "global_seed_ids": ids.tolist(), "last_record_sha256": previous, "scientific_qualification": False}


def record_collection(rhs, initial_states, global_seed_ids, sections, config, *, directory, binding,
                      journal_interval_steps, maximum_snapshot_bytes=64*1024**2):
    """Explicit numerical primitive; future target CLI must add review/source gates."""
    journal = PairedJournal(directory, initial_states, global_seed_ids, sections, config, binding=binding,
        journal_interval_steps=journal_interval_steps, maximum_snapshot_bytes=maximum_snapshot_bytes)
    result = collect_paired_sections(rhs, initial_states, sections, **config,
        progress=journal.append, journal_interval_steps=journal_interval_steps)
    return result, journal.finish(result)
