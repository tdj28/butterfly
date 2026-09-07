"""Write-once, audited full-prefix adaptive snapshots; no target authority.

Reuses bounded NPZ and fsynced exclusive IO, not the RK4-specific step schema.
Full-prefix storage is intentional for the short qualification trajectories.
No resume, retry, repair, overwrite, deletion or remote connection.
"""
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np

from . import paired_journal as io
from .paired_adaptive import collect_adaptive_sections, validate_adaptive
from .paired_sampling import SECTIONS
from .paired_sections import CaptureSection, EVENT_DTYPES
from .poincare import PoincareSection

ARRAY_KEYS = ("global_seed_ids", "initial_states", "final_states", "initial_on_plane",
              "capture_times", "capture_streaks", "ambiguous", "integration_times", "integration_states")
META_KEYS = ("status", "completed", "method", "horizon", "completed_steps", "field_evaluations", "observed_until", "failure")


def unpack(arrays, meta):
    return {**meta, **{k: arrays[k] for k in ARRAY_KEYS}, "events": {
        name: {k: arrays[f"section_{i}__{k}"] for k in (*EVENT_DTYPES, "global_seed_ids")}
        for i, name in enumerate(SECTIONS)}}


def pack(record):
    if set(record) != set(ARRAY_KEYS) | set(META_KEYS) | {"events"} or list(record["events"]) != list(SECTIONS):
        raise ValueError("unexpected adaptive snapshot fields")
    arrays = {k: np.asarray(record[k]) for k in ARRAY_KEYS}
    arrays.update({f"section_{i}__{k}": np.asarray(v) for i, name in enumerate(SECTIONS)
                   for k, v in record["events"][name].items()})
    return arrays, {k: record[k] for k in META_KEYS}


def validate_snapshot(record, initial, seed, sections, config, previous=None):
    arrays, meta = pack(record)
    steps = record["completed_steps"]
    if (type(steps) is not int or not 0 <= steps <= config["maximum_steps"]
            or record["method"] != config["method"] or record["horizon"] != config["horizon"]
            or record["status"] not in ("running", "completed", "failed", "interrupted")
            or type(record["completed"]) is not bool or record["completed"] != (record["status"] == "completed")
            or type(record["field_evaluations"]) is not int
            or not 0 <= record["field_evaluations"] <= config["maximum_field_evaluations"]
            or (record["completed"] and (record["observed_until"] != config["horizon"] or record["failure"] is not None))):
        raise ValueError("adaptive snapshot differs from numerical design/status")
    shapes = {"global_seed_ids": ((1,), "i"), "initial_states": ((1, 3), "f"), "final_states": ((1, 3), "f"),
        "initial_on_plane": ((1, 2), "b"), "capture_times": ((1, 2), "f"), "capture_streaks": ((1, 2), "i"),
        "ambiguous": ((1, 2), "b"), "integration_times": ((steps+1,), "f"), "integration_states": ((steps+1, 3), "f")}
    for key, (shape, kind) in shapes.items():
        value = arrays[key]
        if value.shape != shape or value.dtype.kind != kind or (key != "capture_times" and not np.isfinite(value).all()):
            raise ValueError("invalid adaptive state array")
    times, states = arrays["integration_times"], arrays["integration_states"]
    if (not np.array_equal(arrays["global_seed_ids"], [seed]) or not np.array_equal(arrays["initial_states"], initial[None, :])
            or not np.array_equal(states[0], initial) or not np.array_equal(states[-1], arrays["final_states"][0])
            or times[0] != 0 or np.any(np.diff(times) <= 0) or times[-1] != record["observed_until"]
            or times[-1] > config["horizon"] or np.any(arrays["capture_streaks"] < 0)
            or np.any(np.linalg.norm(states[1:], axis=1) > config["escape_radius"])):
        raise ValueError("adaptive state/trace/seed identity mismatch")
    on_plane = [[initial @ spec.section.normal == spec.section.offset for spec in sections.values()]]
    if not np.array_equal(arrays["initial_on_plane"], on_plane):
        raise ValueError("initial-plane flags changed")
    capture = arrays["capture_times"]
    if np.isinf(capture).any() or np.any(capture[np.isfinite(capture)] <= 0) or np.any(capture[np.isfinite(capture)] > times[-1]):
        raise ValueError("invalid adaptive capture time")
    expected = set(ARRAY_KEYS)
    count = 0
    for i, name in enumerate(SECTIONS):
        event = record["events"][name]
        n = len(event["times"])
        count += n
        expected.update(f"section_{i}__{k}" for k in (*EVENT_DTYPES, "global_seed_ids"))
        for key, dtype in {**EVENT_DTYPES, "global_seed_ids": np.int64}.items():
            value = event[key]
            if (value.shape != ((n, 3) if key == "states" else (n,)) or value.dtype.kind != np.dtype(dtype).kind
                    or not np.isfinite(value).all()):
                raise ValueError("invalid adaptive event array")
        s = event["steps"]
        if (np.any(event["seed_ids"] != 0) or np.any(event["global_seed_ids"] != seed)
                or np.any(s < 1) or np.any(s > steps) or np.any(np.diff(s) <= 0)
                or not np.isin(event["orientation"], [-1, 1]).all()
                or np.any(np.diff(event["times"]) <= 0) or np.any(event["capture_distance"] < 0)):
            raise ValueError("adaptive event identity/order mismatch")
        if np.any(event["times"] <= times[s-1]) or np.any(event["times"] > times[s]):
            raise ValueError("adaptive event lies outside its committed step")
        if np.isfinite(capture[0, i]):
            selected = event["times"] == capture[0, i]
            if (selected.sum() != 1 or not event["accepted"][selected].all()
                    or (event["gate_unresolved"][selected] | event["orientation_unresolved"][selected]).any()
                    or np.any(event["capture_distance"][selected] > sections[name].radius)):
                raise ValueError("capture time lacks matching accepted near-cycle raw event")
    if set(arrays) != expected or count > config["maximum_events"]:
        raise ValueError("unexpected adaptive arrays or excess events")
    if previous is not None:
        if (previous["status"] != "running" or steps < previous["completed_steps"]
                or record["field_evaluations"] < previous["field_evaluations"]
                or (steps == previous["completed_steps"] and record["status"] == "running")):
            raise ValueError("nonmonotone adaptive snapshot progression")
        for key in ("integration_times", "integration_states"):
            if not np.array_equal(record[key][:len(previous[key])], previous[key]):
                raise ValueError("changed committed adaptive trace")
        for name in SECTIONS:
            for key, old in previous["events"][name].items():
                if not np.array_equal(record["events"][name][key][:len(old)], old):
                    raise ValueError("changed committed adaptive events")
        known = np.isfinite(previous["capture_times"])
        if (not np.array_equal(capture[known], previous["capture_times"][known])
                or np.any(previous["ambiguous"] & ~record["ambiguous"])):
            raise ValueError("lost prior capture or ambiguity")
    json.dumps(meta, allow_nan=False)
    return arrays, meta


class AdaptiveJournal:
    def __init__(self, directory, initial_state, global_seed_id, sections, config, *, binding, maximum_snapshot_bytes=8*1024**2):
        initial, _ = validate_adaptive(initial_state, global_seed_id, sections, **config)
        if type(maximum_snapshot_bytes) is not int or not 32768 <= maximum_snapshot_bytes <= 64*1024**2:
            raise ValueError("invalid adaptive snapshot byte limit")
        metadata = {"schema": "butterfly.adaptive-journal.v1", "initial_state": initial.tolist(),
            "global_seed_id": global_seed_id, "config": config, "binding": binding,
            "sections": {n: {**asdict(s), "cycle_states": np.asarray(s.cycle_states).tolist()} for n, s in sections.items()},
            "maximum_snapshot_bytes": maximum_snapshot_bytes, "automatic_retry": False, "resume_supported": False}
        json.dumps(metadata, allow_nan=False)
        self.root = io._safe_path(directory)
        self.root.mkdir(parents=True, exist_ok=False, mode=0o700)
        io._sync_directory(self.root.parent)
        io._json(self.root/"started.json", metadata)
        self.initial, self.seed, self.sections, self.config = initial.copy(), global_seed_id, sections, dict(config)
        self.maximum_bytes = maximum_snapshot_bytes
        self.previous, self.previous_hash, self.index = None, None, 0
        self.write_failed = self.finished = False

    def append(self, record):
        if self.write_failed or self.finished:
            raise ValueError("adaptive journal failed/closed; no retry")
        try:
            arrays, meta = validate_snapshot(record, self.initial, self.seed, self.sections, self.config, self.previous)
            if sum(v.nbytes for v in arrays.values())+512*len(arrays) > self.maximum_bytes:
                raise ValueError("adaptive snapshot exceeds byte bound")
            stem = f"journal-{self.index:06d}"
            raw = io._new_file(self.root/(stem+".npz"), lambda stream: np.savez_compressed(stream, **arrays))
            commit = io._json(self.root/(stem+".json"), {"index": self.index, "previous_record_sha256": self.previous_hash,
                "snapshot": meta, "raw": raw})
            self.previous = unpack({k: v.copy() for k, v in arrays.items()}, dict(meta))
            self.previous_hash, self.index = commit["sha256"], self.index+1
        except BaseException:
            self.write_failed = True
            raise

    def finish(self, result):
        if self.finished:
            raise ValueError("adaptive terminal already written")
        audit = audit_adaptive_journal(self.root)
        if not self.write_failed:
            arrays, meta = validate_snapshot(result, self.initial, self.seed, self.sections, self.config)
            if audit["snapshot"] is None:
                raise ValueError("adaptive terminal lacks recorded collector result")
            saved, saved_meta = pack(audit["snapshot"])
            if meta != saved_meta or any(not np.array_equal(arrays[k], saved[k], equal_nan=True) for k in arrays):
                raise ValueError("collector result differs from final durable snapshot")
        complete = (result["status"] == "completed" and not self.write_failed and not audit["orphan_files"]
                    and audit["last_snapshot_status"] == "completed" and audit["durable_time"] == self.config["horizon"])
        io._json(self.root/"terminal.json", {"collection_complete": bool(complete), "collector_status": result["status"],
            "collector_failure": result["failure"], "write_failed": self.write_failed,
            "records": audit["records"], "last_record_sha256": audit["last_record_sha256"],
            "durable_time": audit["durable_time"], "scientific_qualification": False})
        self.finished = True
        return audit_adaptive_journal(self.root)


def audit_adaptive_journal(directory, *, expected_binding=None, expected_started_sha256=None, expected_terminal_sha256=None):
    root = io._safe_path(directory)
    for name, digest in (("started.json", expected_started_sha256), ("terminal.json", expected_terminal_sha256)):
        if digest is not None and io.sha256(io._safe_path(root/name)) != digest:
            raise ValueError("adaptive journal differs from externally bound receipt")
    meta = io._read_json(root/"started.json")
    if meta["schema"] != "butterfly.adaptive-journal.v1" or (expected_binding is not None and meta["binding"] != expected_binding):
        raise ValueError("adaptive journal schema/binding mismatch")
    names = list(SECTIONS)
    if set(meta["sections"]) != set(names):
        raise ValueError("both adaptive sections required")
    sections = {n: CaptureSection(section=PoincareSection(**meta["sections"][n]["section"]),
        **{k: v for k, v in meta["sections"][n].items() if k != "section"}) for n in names}
    initial, _ = validate_adaptive(meta["initial_state"], meta["global_seed_id"], sections, **meta["config"])
    maximum = meta["maximum_snapshot_bytes"]
    if type(maximum) is not int or not 32768 <= maximum <= 64*1024**2:
        raise ValueError("invalid adaptive byte bound")
    previous = previous_hash = None
    count = 0
    expected = {"started.json"}
    for path in sorted(root.glob("journal-*.json")):
        row = io._read_json(path)
        if path.name != f"journal-{count:06d}.json" or row["index"] != count or row["previous_record_sha256"] != previous_hash:
            raise ValueError("broken adaptive journal hash chain")
        arrays = io._arrays(io._checked_file(root, row["raw"]), maximum)
        record = unpack(arrays, row["snapshot"])
        validated, _ = validate_snapshot(record, initial, meta["global_seed_id"], sections, meta["config"], previous)
        if set(validated) != set(arrays):
            raise ValueError("extra adaptive raw arrays")
        previous, previous_hash, count = record, io.sha256(path), count+1
        expected.update((path.name, row["raw"]["path"]))
    time = 0. if previous is None else previous["observed_until"]
    terminal = None
    if (root/"terminal.json").exists():
        terminal = io._read_json(root/"terminal.json")
        expected.add("terminal.json")
        if terminal["records"] != count or terminal["last_record_sha256"] != previous_hash or terminal["durable_time"] != time:
            raise ValueError("adaptive terminal differs from durable prefix")
    orphans = sorted(p.name for p in root.iterdir() if p.name not in expected)
    complete = bool(terminal and terminal["collection_complete"] is True)
    if complete and (orphans or previous is None or previous["status"] != "completed" or time != meta["config"]["horizon"]
                     or terminal["write_failed"] is not False or terminal["collector_status"] != "completed"):
        raise ValueError("invalid adaptive completion claim")
    return {"status": "completed" if complete else "incomplete", "records": count, "durable_time": time,
        "last_record_sha256": previous_hash, "last_snapshot_status": None if previous is None else previous["status"],
        "orphan_files": orphans, "snapshot": previous, "binding": meta["binding"]}


def record_adaptive(rhs, initial_state, global_seed_id, sections, config, *, directory, binding, maximum_snapshot_bytes=8*1024**2):
    sink = AdaptiveJournal(directory, initial_state, global_seed_id, sections, config,
                           binding=binding, maximum_snapshot_bytes=maximum_snapshot_bytes)
    result = collect_adaptive_sections(rhs, initial_state, global_seed_id, sections, **config, progress=sink.append)
    return result, sink.finish(result)
