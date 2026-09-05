#!/usr/bin/env python3
"""Preserve a bounded EXP-204-derived nomination pilot; never verify Jones words.

The wall clock is cooperative between GPU calls and fitting stages. A controller
must enforce any hard spending/runtime cap. No automatic retry or resume exists.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import signal
import subprocess
import time

import numpy as np
import scipy

from scripts.gpu_audit_jones_scale_ensemble_residuals import (
    _profile_row, combine_candidate,
)
from scripts.audit_jones_scale_ensemble_residual import signed_residual_bracket_cells
from scripts.gpu_scan_jones_two_critical_residuals import (
    _sections, integrate_gpu, torch, triton,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "butterfly.symbolic-center-pilot-manifest.v1"
PARENT_SCHEMA = "butterfly.jones-scale-ensemble-gpu-residual-manifest.v1"
PARENT_SHA256 = "83a6d8fc986c6a1cec8fab38c90b3c023d98db77cbdc2a86bf433f604faee867"
CANDIDATE_SHA256 = "71aab52016abc8163887b2bdfd4e8124bde0e436be2239751f19d29bed490012"
DEFERRED = {"orbit", "critical_membership", "alphabet_transport", "symbolic_arrows"}


def utc_now():
    return datetime.now(UTC).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite_tree(value):
    if isinstance(value, dict):
        return all(finite_tree(child) for child in value.values())
    if isinstance(value, (tuple, list)):
        return all(finite_tree(child) for child in value)
    return not isinstance(value, (float, np.floating)) or bool(np.isfinite(value))


def encoded_json(value):
    """Preserve diagnostic nonfinites as named nulls, never invalid JSON."""
    invalid = []

    def clean(item, path):
        if isinstance(item, dict):
            return {key: clean(child, f"{path}.{key}") for key, child in item.items()}
        if isinstance(item, (tuple, list)):
            return [clean(child, f"{path}[{index}]") for index, child in enumerate(item)]
        if isinstance(item, (float, np.floating)) and not np.isfinite(item):
            invalid.append(path)
            return None
        if isinstance(item, np.generic):
            return item.item()
        return item

    result = clean(value, "record")
    if invalid:
        result["nonfinite_fields_replaced_by_null"] = invalid
    return (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def write_new_json(path, value):
    with Path(path).open("xb") as stream:
        stream.write(encoded_json(value))
    return {"path": Path(path).name, "sha256": sha256_file(path), "bytes": Path(path).stat().st_size}


def confined_path(root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("input paths must be repository-relative without '..'")
    resolved = (root / path).resolve(strict=True)
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("input escapes source root")
    return resolved


def checked_input(root, declaration):
    expected = declaration["sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("invalid input SHA-256")
    path = confined_path(root, declaration["path"])
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError(f"input hash mismatch: {declaration['path']}")
    return content


def git(root, *args):
    return subprocess.check_output(
        ["git", *args], cwd=root, stderr=subprocess.DEVNULL,
    ).decode().strip()


def source_binding(root, commit, manifest_path, manifest_bytes, *, inventory=None, inventory_sha256=None, required_paths=()):
    """Verify a clean pushed Git snapshot, or an explicitly hash-bound inventory.

    Git mode uses local origin remote-tracking refs, not a network request.
    Inventory mode records the frozen publisher's pushed-commit attestation.
    """
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("a full lowercase source commit is required")
    relative = manifest_path.resolve().relative_to(root.resolve()).as_posix()
    if inventory is not None:
        if inventory_sha256 is None or sha256_file(inventory) != inventory_sha256:
            raise ValueError("source inventory hash mismatch")
        document = json.loads(Path(inventory).read_bytes())
        if document.get("schema") != "butterfly.source-inventory.v1":
            raise ValueError("unsupported source inventory")
        if document.get("source_commit") != commit or document.get("pushed_source_commit") != commit:
            raise ValueError("inventory does not attest the declared pushed source")
        files = document["files"]
        required = {relative, "pyproject.toml", "uv.lock", *required_paths}
        required.update(path.relative_to(root).as_posix() for directory in ("python", "scripts")
                        for path in (root / directory).rglob("*.py"))
        if not required <= set(files):
            raise ValueError("source inventory lacks the complete runtime source closure")
        for name, expected in files.items():
            if sha256_file(confined_path(root, name)) != expected:
                raise ValueError(f"source inventory file mismatch: {name}")
        if files[relative] != hashlib.sha256(manifest_bytes).hexdigest():
            raise ValueError("manifest differs from source inventory")
        return {"mode": "explicit_inventory", "commit": commit,
                "inventory_sha256": inventory_sha256, "pushed_commit_attested": True,
                "file_count": len(files)}
    if inventory_sha256 is not None:
        raise ValueError("source inventory hash requires its file")
    try:
        if git(root, "rev-parse", "HEAD") != commit:
            raise ValueError("source commit mismatch")
        if git(root, "status", "--porcelain", "--untracked-files=all"):
            raise ValueError("clean source required")
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"], cwd=root, stderr=subprocess.DEVNULL,
        )
        if committed != manifest_bytes:
            raise ValueError("manifest differs from committed source")
        refs = git(root, "for-each-ref", "--format=%(objectname) %(refname)", "refs/remotes/origin")
        matching = [line.split(" ", 1)[1] for line in refs.splitlines() if line.startswith(commit + " ")]
        if not matching:
            raise ValueError("HEAD lacks an exact origin remote-tracking ref")
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("source Git checks failed; an explicit verified inventory is required") from error
    return {"mode": "clean_git", "commit": commit, "exact_origin_refs": matching,
            "remote_check": "local remote-tracking refs; no network access", "manifest_matches_HEAD": True}


def prepare(manifest_path, commit, *, root=ROOT, inventory=None, inventory_sha256=None):
    """Outcome-free preflight: inspect declarations/hashes/shape, never fit data."""
    root, manifest_path = Path(root).resolve(), Path(manifest_path).resolve()
    content = manifest_path.read_bytes()
    manifest = json.loads(content)
    if manifest.get("schema") != SCHEMA or not finite_tree(manifest):
        raise ValueError("unsupported or nonfinite pilot manifest")
    interpretation = manifest["interpretation"]
    if interpretation.get("exploratory_nomination_only") is not True or interpretation.get("jones_words_used") is not False:
        raise ValueError("pilot must be word-blind exploratory nomination only")
    if set(interpretation["deferred_verification"]) != DEFERRED:
        raise ValueError("all four verification stages must remain explicitly deferred")
    execution, validity = manifest["execution"], manifest["validity"]
    if type(execution["batch_size"]) is not int or not 1 <= execution["batch_size"] <= 32:
        raise ValueError("batch_size must be an integer in [1,32]")
    for key in ("maximum_wall_seconds", "maximum_analysis_seconds"):
        seconds = execution[key]
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds <= 0:
            raise ValueError(f"{key} must be positive and finite")
    if execution.get("collect_then_local_analyze") is not True:
        raise ValueError("GPU collection must be separated from local analysis")
    if execution.get("stop_on_first_invalid_batch") is not True:
        raise ValueError("first invalid batch must stop the pilot")
    minimum_angle = validity["minimum_normalized_section_transversality"]
    if isinstance(minimum_angle, bool) or not isinstance(minimum_angle, (int, float)) or not 0 < minimum_angle <= 1:
        raise ValueError("normalized transversality threshold must be in (0,1]")
    if validity.get("reject_saturated_survivor_records") is not True:
        raise ValueError("saturated survivor records must be rejected")
    if manifest["parent_design"]["sha256"] != PARENT_SHA256:
        raise ValueError("parent design must retain the original EXP-204 hash")
    parent = json.loads(checked_input(root, manifest["parent_design"]))
    if parent.get("schema") != PARENT_SCHEMA or parent.get("experiment_id") != "EXP-204":
        raise ValueError("parent design must be the frozen EXP-204 study")
    if not finite_tree(parent) or parent["expected_candidate_count"] != 551:
        raise ValueError("invalid EXP-204 numerical design")
    if manifest["candidate_input"]["sha256"] != CANDIDATE_SHA256 or parent["candidate_input_sha256"] != CANDIDATE_SHA256:
        raise ValueError("candidate declaration must retain the EXP-204 input")
    candidate_document = json.loads(checked_input(root, manifest["candidate_input"]))
    candidates = candidate_document["candidates"]
    if len(candidates) != 551 or not all(row.get("passed") is True for row in candidates):
        raise ValueError("the pilot must retain all 551 qualified EXP-204 candidates")
    ids = [row["id"] for row in candidates]
    if len(set(ids)) != len(ids) or not all(isinstance(name, str) and name for name in ids):
        raise ValueError("candidate IDs must be unique nonempty strings")
    for row in candidates:
        states = np.asarray(row["section_states"], dtype=float)
        if states.shape != (parent["cycle_state_count"], 3) or not np.all(np.isfinite(states)):
            raise ValueError("candidate section states are not complete finite cycles")
        if not finite_tree(row["parameters"]):
            raise ValueError("candidate parameters are nonfinite")
    evidence = [*parent["evidence"], *manifest["evidence"]]
    for declaration in evidence:
        checked_input(root, declaration)
    required_paths = [manifest["parent_design"]["path"], *(row["path"] for row in evidence)]
    binding = source_binding(root, commit, manifest_path, content, inventory=inventory,
                             inventory_sha256=inventory_sha256, required_paths=required_paths)
    return {"manifest": manifest, "parent": parent, "candidates": candidates,
            "manifest_sha256": hashlib.sha256(content).hexdigest(), "source": binding,
            "input_hashes": {"candidates": manifest["candidate_input"]["sha256"],
                             "parent_design": manifest["parent_design"]["sha256"]}}


def archive_raw(output_dir, name, candidates, run, profile, parent, validity, *, duration_backend="gpu"):
    """Persist ragged survivor records and their metadata before fitting."""
    sections = _sections(candidates, parent["section"]["kind"])
    candidate_offsets, trajectory_offsets = [0], [0]
    seed_ids, states, times, angles = [], [], [], []
    saturated = []
    expected_shape = (len(candidates), len(parent["ensemble"]["checkpoint_times"]))
    counts, failures = np.asarray(run["survivor_counts"]), np.asarray(run["failed_counts"])
    if counts.shape != expected_shape or failures.shape != (len(candidates),) or len(run["records"]) != len(candidates):
        raise ValueError("GPU result candidate/checkpoint shape mismatch")
    if counts.dtype.kind not in "iu" or failures.dtype.kind not in "iu" or np.any(counts < 0) or np.any(failures < 0):
        raise ValueError("GPU count arrays must contain nonnegative integers without object/pickle data")
    for index, (candidate, record, section) in enumerate(zip(candidates, run["records"], sections, strict=True)):
        if len(record["seed_ids"]) != len(record["states"]) or len(record["times"]) != len(record["states"]):
            raise ValueError("raw survivor record shape mismatch")
        if len(record["seed_ids"]) != counts[index, -1]:
            raise ValueError("raw records do not cover every final survivor")
        for seed_id, state, event_times in zip(record["seed_ids"], record["states"], record["times"], strict=True):
            state, event_times = np.asarray(state, dtype=float), np.asarray(event_times, dtype=float)
            if state.shape != (len(event_times), 3) or event_times.ndim != 1:
                raise ValueError("raw event state/time shape mismatch")
            if (not isinstance(seed_id, (int, np.integer)) or seed_id < 0
                    or seed_id >= parent["ensemble"]["x_count"] * parent["ensemble"]["z_count"]):
                raise ValueError("raw seed ID is not a valid ensemble index")
            if np.any(np.diff(event_times) <= 0):
                raise ValueError("raw event times are not strictly increasing")
            seed_ids.append(int(seed_id))
            states.append(state)
            times.append(event_times)
            trajectory_offsets.append(trajectory_offsets[-1] + len(state))
            if len(state) >= parent["gpu"]["max_recorded_crossings"]:
                saturated.append({"candidate_id": candidate["id"], "seed_id": int(seed_id), "count": len(state)})
            a, b, c = (candidate["parameters"][key] for key in ("a", "b", "c"))
            x, y, z = state.T
            field = np.column_stack((-y-z, x+a*y, b+z*(x-c)))
            normal = np.asarray(section.normal, dtype=float)
            with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
                angle = np.abs(field @ normal) / (np.linalg.norm(field, axis=1) * np.linalg.norm(normal))
            angles.append(angle)
        candidate_offsets.append(len(seed_ids))
    flat_states = np.concatenate(states) if states else np.empty((0, 3))
    flat_times = np.concatenate(times) if times else np.empty(0)
    flat_angles = np.concatenate(angles) if angles else np.empty(0)
    raw_path = Path(output_dir) / f"{name}.npz"
    with raw_path.open("xb") as stream:
        np.savez_compressed(stream, candidate_ids=np.asarray([row["id"] for row in candidates], dtype=str),
                            candidate_record_offsets=np.asarray(candidate_offsets, dtype=np.int64),
                            seed_ids=np.asarray(seed_ids, dtype=np.int64),
                            trajectory_offsets=np.asarray(trajectory_offsets, dtype=np.int64),
                            states=flat_states, times=flat_times,
                            normalized_section_transversality=flat_angles,
                            survivor_counts=counts, failed_counts=failures)
    finite = bool(np.all(np.isfinite(flat_states)) and np.all(np.isfinite(flat_times)) and np.all(np.isfinite(flat_angles)))
    minimum = float(np.min(flat_angles)) if len(flat_angles) else None
    angle_passed = bool(finite and (minimum is None or minimum >= validity["minimum_normalized_section_transversality"]))
    metadata = {
        "schema": "butterfly.symbolic-center-raw-batch.v1", "saved_utc": utc_now(),
        "profile": profile, "candidate_ids": [row["id"] for row in candidates],
        "raw": {"path": raw_path.name, "sha256": sha256_file(raw_path), "bytes": raw_path.stat().st_size},
        "layout": "candidate_record_offsets index seed_ids; trajectory_offsets index states/times/angles; no object arrays or pickle",
        "record_count": len(seed_ids), "event_count": len(flat_angles),
        "saturated_survivor_records": saturated, "finite_recorded_data": finite,
        "minimum_normalized_section_transversality": minimum,
        "transversality_passed": angle_passed, "validity_passed": finite and angle_passed and not saturated,
        "scope": "recorded final-survivor event states only; not captured trajectories, root isolation, between-step extrema, or archive-wide transversality",
        "elapsed_" + duration_backend + "_seconds": run["elapsed_seconds"],
    }
    metadata["metadata_file"] = write_new_json(Path(output_dir) / f"{name}.json", metadata)
    return metadata


def environment():
    if torch is None or triton is None or not torch.cuda.is_available():
        raise RuntimeError("CUDA, PyTorch and Triton are required for target execution")
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "torch": torch.__version__, "triton": triton.__version__,
            "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0),
            "gpu_memory_bytes": torch.cuda.get_device_properties(0).total_memory}


def collect(prepared, output_dir, *, source_recheck=None, integrator=None,
            runtime_environment=None, duration_backend="gpu"):
    """Collect raw GPU evidence only: no spline fitting or nomination analysis."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest, parent, candidates = (prepared[key] for key in ("manifest", "parent", "candidates"))
    started = time.monotonic()
    deadline = started + manifest["execution"]["maximum_wall_seconds"]
    receipt = {"schema": "butterfly.symbolic-center-collection.v1", "experiment_id": manifest["experiment_id"],
               "started_utc": utc_now(), "source": prepared["source"],
               "manifest_sha256": prepared["manifest_sha256"], "input_hashes": prepared["input_hashes"],
               "interpretation": manifest["interpretation"], "batches": [], "completed_candidate_ids": [],
               "status": "running", "collection_passed": False, "nomination_performed": False}
    write_new_json(output_dir / "started.json", receipt)
    active_ids = []

    def check_time(stage):
        if time.monotonic() >= deadline:
            raise TimeoutError(f"cooperative wall-time budget exhausted at {stage}")

    try:
        receipt["environment"] = environment() if runtime_environment is None else runtime_environment
        integrate = integrate_gpu if integrator is None else integrator
        size = manifest["execution"]["batch_size"]
        for start in range(0, len(candidates), size):
            check_time("batch boundary")
            batch = candidates[start:start+size]
            active_ids = [row["id"] for row in batch]
            batch_index = start // size
            batch_row = {"index": batch_index, "candidate_ids": active_ids, "profiles": []}
            receipt["batches"].append(batch_row)
            for profile_index, profile in enumerate(parent["profiles"]):
                check_time("profile boundary")
                name = f"batch-{batch_index:04d}-profile-{profile_index}"
                raw_run = integrate(
                    batch, dt=profile["dt"], horizon=parent["ensemble"]["horizon"],
                    checkpoints=parent["ensemble"]["checkpoint_times"], midpoint=parent["ensemble"]["midpoint_window"],
                    ensemble=parent["ensemble"], capture=parent["capture"], gpu_options=parent["gpu"],
                    section_name=parent["section"]["kind"], section_code=1,
                    target_cycle_state_count=parent["cycle_state_count"],
                )
                metadata = archive_raw(output_dir, name, batch, raw_run, profile, parent, manifest["validity"],
                                       duration_backend=duration_backend)
                batch_row["profiles"].append(metadata)
                write_new_json(output_dir / f"{name}-checkpoint.json", {"candidate_ids": active_ids, "raw_metadata": metadata})
                if not metadata["validity_passed"]:
                    raise ValueError(f"raw survivor validity gate failed in {name}")
                check_time("after raw preservation")
            receipt["completed_candidate_ids"].extend(active_ids)
            active_ids = []
            check_time("completed batch boundary")
        if source_recheck is not None:
            source_recheck()
        check_time("final source check")
        receipt["status"] = "completed"
        receipt["collection_passed"] = True
    except (Exception, KeyboardInterrupt) as error:
        receipt["status"] = "failed"
        receipt["failure"] = {"type": type(error).__name__, "message": str(error), "active_candidate_ids": active_ids}
    finally:
        completed = set(receipt["completed_candidate_ids"])
        receipt["uncompleted_candidate_ids"] = [row["id"] for row in candidates if row["id"] not in completed]
        receipt["finished_utc"] = utc_now()
        receipt["elapsed_seconds"] = time.monotonic() - started
        receipt["automatic_retry_or_resume"] = False
        write_new_json(output_dir / "receipt.json", receipt)
    return receipt


def collection_file(directory, descriptor):
    name = descriptor["path"]
    if Path(name).name != name:
        raise ValueError("collection assets must use plain basenames")
    path = confined_path(Path(directory).resolve(), name)
    if sha256_file(path) != descriptor["sha256"] or path.stat().st_size != descriptor["bytes"]:
        raise ValueError(f"collection asset hash/size mismatch: {name}")
    return path


def load_raw(path, expected_ids, parent):
    """Restore the raw ragged layout without pickle or a numerical integration."""
    with np.load(path, allow_pickle=False) as saved:
        arrays = {key: saved[key] for key in saved.files}
    ids = arrays["candidate_ids"].tolist()
    offsets, trajectory = arrays["candidate_record_offsets"], arrays["trajectory_offsets"]
    seeds, states, times = arrays["seed_ids"], arrays["states"], arrays["times"]
    angles = arrays["normalized_section_transversality"]
    if ids != expected_ids or offsets.shape != (len(ids)+1,) or trajectory.shape != (len(seeds)+1,):
        raise ValueError("raw candidate/ragged indexing mismatch")
    for values, final in ((offsets, len(seeds)), (trajectory, len(times))):
        if values.dtype.kind not in "iu" or values[0] != 0 or values[-1] != final or np.any(np.diff(values) < 0):
            raise ValueError("invalid raw ragged offsets")
    if states.shape != (len(times), 3) or times.ndim != 1 or angles.shape != times.shape:
        raise ValueError("raw event array shape mismatch")
    if not all(np.all(np.isfinite(value)) for value in (states, times, angles)):
        raise ValueError("raw collection contains nonfinite event data")
    if seeds.dtype.kind not in "iu" or np.any(seeds < 0) or np.any(seeds >= parent["ensemble"]["x_count"] * parent["ensemble"]["z_count"]):
        raise ValueError("invalid raw seed IDs")
    if np.any(np.diff(trajectory) >= parent["gpu"]["max_recorded_crossings"]):
        raise ValueError("raw survivor records may have saturated")
    records = []
    for index in range(len(ids)):
        start, stop = int(offsets[index]), int(offsets[index+1])
        if len(set(seeds[start:stop].tolist())) != stop-start:
            raise ValueError("duplicate survivor seed ID")
        for j in range(start, stop):
            if np.any(np.diff(times[trajectory[j]:trajectory[j+1]]) <= 0):
                raise ValueError("raw event times are not strictly increasing")
        records.append({"seed_ids": seeds[start:stop],
                        "states": [states[trajectory[j]:trajectory[j+1]] for j in range(start, stop)],
                        "times": [times[trajectory[j]:trajectory[j+1]] for j in range(start, stop)]})
    counts, failures = arrays["survivor_counts"], arrays["failed_counts"]
    if counts.shape != (len(ids), len(parent["ensemble"]["checkpoint_times"])) or failures.shape != (len(ids),):
        raise ValueError("raw count array shape mismatch")
    if (counts.dtype.kind not in "iu" or failures.dtype.kind not in "iu"
            or np.any(counts < 0) or np.any(failures < 0)
            or not np.array_equal(np.diff(offsets), counts[:, -1])):
        raise ValueError("raw survivor count/record mismatch")
    return {"records": records, "survivor_counts": counts, "failed_counts": failures,
            "recorded_angles": angles}


class LocalCollectionAssets:
    """Original local-file I/O behind the same bounded-provider interface."""

    def __init__(self, directory):
        self.directory = Path(directory)

    def receipt_bytes(self, expected_sha256):
        path = self.directory / "receipt.json"
        if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) or sha256_file(path) != expected_sha256:
            raise ValueError("collection receipt hash mismatch")
        return path.read_bytes()

    def verify_assets(self, descriptors):
        for descriptor in descriptors:
            collection_file(self.directory, descriptor)

    def metadata_bytes(self, descriptor):
        return collection_file(self.directory, descriptor).read_bytes()

    @contextmanager
    def materialize(self, descriptor):
        yield collection_file(self.directory, descriptor)


def analyze(prepared, collection_dir, collection_sha256, output_dir, *, source_recheck=None,
            asset_provider=None):
    """Fit hash-bound evidence locally; optional provider changes only input I/O.

    Providers must verify all immutable assets before fitting, return verified
    metadata bytes, and materialize only one raw profile per context. The full
    original receipt/asset set is checked again before any nomination result.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest, parent, candidates = (prepared[key] for key in ("manifest", "parent", "candidates"))
    started = time.monotonic()
    deadline = started + manifest["execution"]["maximum_analysis_seconds"]
    receipt = {"schema": "butterfly.symbolic-center-analysis.v1", "experiment_id": manifest["experiment_id"],
               "started_utc": utc_now(), "source": prepared["source"],
               "manifest_sha256": prepared["manifest_sha256"], "input_hashes": prepared["input_hashes"],
               "collection_receipt_sha256": collection_sha256, "interpretation": manifest["interpretation"],
               "status": "running", "passed": False, "gpu_calls_performed": False,
               "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "fit_batches": [], "completed_candidate_ids": [], "nomination_result": None}
    write_new_json(output_dir / "started.json", receipt)
    combined = []
    active_ids = []
    metadata_assets = []
    assets = LocalCollectionAssets(collection_dir) if asset_provider is None else asset_provider

    def check_time(stage):
        if time.monotonic() >= deadline:
            raise TimeoutError(f"cooperative analysis budget exhausted at {stage}")

    try:
        collection = json.loads(assets.receipt_bytes(collection_sha256))
        if (collection.get("schema") != "butterfly.symbolic-center-collection.v1"
                or collection.get("status") != "completed" or collection.get("collection_passed") is not True
                or collection.get("nomination_performed") is not False):
            raise ValueError("analysis requires a completed validity-qualified raw collection")
        if (collection["manifest_sha256"] != prepared["manifest_sha256"]
                or collection["input_hashes"] != prepared["input_hashes"]
                or collection["source"]["commit"] != prepared["source"]["commit"]):
            raise ValueError("collection manifest/input/source binding mismatch")
        expected_ids = [row["id"] for row in candidates]
        observed_ids = [name for batch in collection["batches"] for name in batch["candidate_ids"]]
        if observed_ids != expected_ids or collection["completed_candidate_ids"] != expected_ids:
            raise ValueError("collection must contain each frozen candidate exactly once in order")
        # Validate every immutable asset before the first fit, not after finding a candidate.
        metadata_assets = [metadata[key] for batch in collection["batches"]
                           for metadata in batch["profiles"] for key in ("metadata_file", "raw")]
        assets.verify_assets(metadata_assets)
        for batch in collection["batches"]:
            if len(batch["profiles"]) != len(parent["profiles"]):
                raise ValueError("collection lacks the complete profile set")
            for metadata, profile in zip(batch["profiles"], parent["profiles"], strict=True):
                expected_metadata = {key: value for key, value in metadata.items() if key != "metadata_file"}
                if json.loads(assets.metadata_bytes(metadata["metadata_file"])) != expected_metadata:
                    raise ValueError("raw metadata content mismatch")
                if metadata["validity_passed"] is not True or metadata["profile"] != profile or metadata["candidate_ids"] != batch["candidate_ids"]:
                    raise ValueError("raw metadata validity/profile binding mismatch")
        lookup = {row["id"]: row for row in candidates}
        for batch in collection["batches"]:
            check_time("batch boundary")
            active_ids = batch["candidate_ids"]
            candidate_batch = [lookup[name] for name in active_ids]
            profile_rows = []
            files = []
            for index, (metadata, profile) in enumerate(zip(batch["profiles"], parent["profiles"], strict=True)):
                check_time("profile boundary")
                with assets.materialize(metadata["raw"]) as raw_path:
                    raw = load_raw(raw_path, active_ids, parent)
                    if len(raw["recorded_angles"]) and float(np.min(raw["recorded_angles"])) < manifest["validity"]["minimum_normalized_section_transversality"]:
                        raise ValueError("preserved transversality gate failed")
                    rows = [_profile_row(candidate, raw["records"][j], raw, j, parent, profile,
                                         parent["return_coordinate"]["axis"])
                            for j, candidate in enumerate(candidate_batch)]
                    del raw  # Release the previous profile before loading the next.
                # An unresolved fit may legitimately contain infinite failure diagnostics.
                for row in rows:
                    for support in row["supports"]:
                        for item in [*support["results"], *support["assignments"]]:
                            if item.get("resolved") and not finite_tree(item):
                                raise ValueError("resolved fit contains nonfinite numerical data")
                profile_rows.append(rows)
                files.append(write_new_json(output_dir / f"batch-{batch['index']:04d}-profile-{index}-fits.json", {"rows": rows}))
                check_time("after fitting")
            batch_combined = [combine_candidate(candidate, profile_rows, parent) for candidate in candidate_batch]
            combined.extend(batch_combined)
            receipt["completed_candidate_ids"].extend(active_ids)
            files.append(write_new_json(output_dir / f"batch-{batch['index']:04d}-combined.json", {"rows": batch_combined}))
            receipt["fit_batches"].append({"index": batch["index"], "candidate_ids": active_ids, "files": files})
            active_ids = []
        if source_recheck is not None:
            source_recheck()
        assets.receipt_bytes(collection_sha256)
        assets.verify_assets(metadata_assets)
        check_time("final source check")
        eligible = [row for row in combined if row["eligible"]]
        direct = [row["id"] for row in eligible if row["direct_gate_passed"]]
        cells = signed_residual_bracket_cells(combined)
        coverage = len(eligible) >= parent["acceptance"]["minimum_eligible_candidates"]
        nominated = bool(coverage and (direct or len(cells) >= parent["acceptance"]["minimum_signed_bracket_cells"]))
        receipt["nomination_result"] = {"eligible_count": len(eligible), "coverage_passed": coverage,
                                        "direct_candidate_ids": direct, "corner_range_nomination_cells": cells,
                                        "nomination_passed": nominated,
                                        "warning": "separate corner sign ranges do not establish a simultaneous root; no center or symbolic chain is verified"}
        receipt["status"] = "completed"
        receipt["passed"] = nominated
    except (Exception, KeyboardInterrupt) as error:
        receipt["status"] = "failed"
        receipt["failure"] = {"type": type(error).__name__, "message": str(error), "active_candidate_ids": active_ids}
    finally:
        completed = set(receipt["completed_candidate_ids"])
        receipt["uncompleted_candidate_ids"] = [row["id"] for row in candidates if row["id"] not in completed]
        receipt["combined_candidates"] = combined
        receipt["finished_utc"] = utc_now()
        receipt["elapsed_seconds"] = time.monotonic() - started
        receipt["automatic_retry_or_resume"] = False
        write_new_json(output_dir / "receipt.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-inventory", type=Path)
    parser.add_argument("--source-inventory-sha256")
    parser.add_argument("--mode", choices=("preflight", "collect", "analyze"), default="preflight")
    parser.add_argument("--collection-dir", type=Path)
    parser.add_argument("--collection-receipt-sha256")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    try:
        prepared = prepare(args.manifest, args.source_commit, inventory=args.source_inventory,
                           inventory_sha256=args.source_inventory_sha256)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.error(f"preflight failed: {error}")
    if args.preflight or args.mode == "preflight":
        print(encoded_json({"preflight_passed": True, "target_computation_performed": False,
                            "candidate_count": len(prepared["candidates"]), "source": prepared["source"],
                            "manifest_sha256": prepared["manifest_sha256"], "input_hashes": prepared["input_hashes"]}).decode(), end="")
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for execution")
    def interrupted(_signal, _frame):
        raise KeyboardInterrupt("termination signal received; no automatic retry")

    previous = signal.signal(signal.SIGTERM, interrupted)
    recheck = lambda: prepare(args.manifest, args.source_commit, inventory=args.source_inventory,
                              inventory_sha256=args.source_inventory_sha256)
    try:
        if args.mode == "collect":
            receipt = collect(prepared, args.output_dir, source_recheck=recheck)
            passed = receipt["collection_passed"]
        else:
            if args.collection_dir is None or args.collection_receipt_sha256 is None:
                parser.error("analyze requires --collection-dir and --collection-receipt-sha256")
            receipt = analyze(prepared, args.collection_dir, args.collection_receipt_sha256,
                              args.output_dir, source_recheck=recheck)
            passed = receipt["passed"]
    finally:
        signal.signal(signal.SIGTERM, previous)
    print(encoded_json({"output_dir": str(args.output_dir), "status": receipt["status"],
                        "phase_passed": passed}).decode(), end="")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
