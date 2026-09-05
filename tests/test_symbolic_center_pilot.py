"""Synthetic, no-GPU controls for the evidence-preserving symbolic pilot."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from scripts import run_symbolic_center_pilot as pilot
from scripts.analyze_symbolic_remote_collection import RemoteCollectionAssets


COMMIT = "a" * 40


@pytest.fixture
def prepared():
    parent = {
        "schema": pilot.PARENT_SCHEMA, "experiment_id": "EXP-204", "expected_candidate_count": 551,
        "candidate_input_sha256": "b" * 64, "evidence": [],
        "section": {"kind": "barrio_positive_x"}, "cycle_state_count": 8,
        "return_coordinate": {"name": "z", "axis": 2},
        "profiles": [{"name": "coarse", "dt": 0.01}, {"name": "fine", "dt": 0.005}],
        "ensemble": {"x_count": 2, "z_count": 2, "horizon": 200.0,
                     "checkpoint_times": [50.0, 100.0, 150.0, 200.0], "midpoint_window": [80.0, 140.0]},
        "capture": {}, "gpu": {"max_recorded_crossings": 32},
        "nested_support": [{"name": "nested", "minimum_return_pairs": 1},
                           {"name": "full", "minimum_return_pairs": 1}],
        "smoothing_values": [4.641588833612782e-6, 1e-5, 2.1544346900318822e-5],
        "acceptance": {"minimum_eligible_candidates": 1, "maximum_normalized_critical_location_span": 0.03,
                       "maximum_survivor_fraction_difference": 0.03, "maximum_direct_absolute_residual": 0.02,
                       "minimum_signed_bracket_cells": 1},
    }
    manifest = {
        "schema": pilot.SCHEMA, "experiment_id": "EXP-477",
        "parent_design": {"path": "parent.json", "sha256": "a" * 64},
        "candidate_input": {"path": "candidates.json", "sha256": "b" * 64}, "evidence": [],
        "execution": {"batch_size": 2, "maximum_wall_seconds": 60.0, "maximum_analysis_seconds": 60.0,
                      "stop_on_first_invalid_batch": True, "collect_then_local_analyze": True},
        "validity": {"reject_saturated_survivor_records": True, "minimum_normalized_section_transversality": 1e-5},
        "interpretation": {"exploratory_nomination_only": True, "jones_words_used": False,
                           "deferred_verification": sorted(pilot.DEFERRED)},
    }
    candidates = [{"id": f"p-{index}", "grid_index": [index, 0], "passed": True,
                   "parameters": {"a": 0.2, "b": 0.2, "c": 7.0},
                   "section_states": [[0.0, -1.0, z] for z in (0.2, 0.8, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9)]}
                  for index in range(3)]
    return {"manifest": manifest, "parent": parent, "candidates": candidates,
            "manifest_sha256": "c" * 64, "source": {"mode": "synthetic", "commit": COMMIT},
            "input_hashes": {"parent_design": "a" * 64, "candidates": "b" * 64}}


def fake_gpu(candidates, **kwargs):
    assert kwargs["section_name"] == "barrio_positive_x" and kwargs["section_code"] == 1
    return {"records": [{"seed_ids": np.asarray([0, 1]),
                          "states": [np.tile([1.0, -1.0, 0.01], (3, 1)) for _ in range(2)],
                          "times": [np.asarray([80.0, 100.0, 120.0]) for _ in range(2)]}
                         for _ in candidates],
            "survivor_counts": np.tile([4, 4, 3, 2], (len(candidates), 1)),
            "failed_counts": np.zeros(len(candidates), dtype=int), "elapsed_seconds": 0.01}


def fake_fit(candidate, record, run, index, parent, profile, axis):
    assert axis == 2 and len(record["seed_ids"]) == 2
    return {"id": candidate["id"], "profile": profile["name"], "dt": profile["dt"],
            "failed_count": int(run["failed_counts"][index]),
            "survivor_counts": run["survivor_counts"][index].tolist(),
            "supports": [{"name": support["name"], "pair_count": 10,
                          "source_domain": [0.0, 1.0], "smoothing_values": parent["smoothing_values"],
                          "results": [{"resolved": True, "branch_count": 3, "critical_points": [0.2, 0.8]}
                                      for _ in parent["smoothing_values"]],
                          "assignments": [{"resolved": True, "orbit_indices": [0, 1],
                                           "normalized_signed_residuals": [0.0, 0.0],
                                           "maximum_absolute_residual": 0.0, "sum_absolute_residual": 0.0}
                                          for _ in parent["smoothing_values"]]}
                         for support in parent["nested_support"]]}


@pytest.fixture
def fake_runtime(monkeypatch):
    monkeypatch.setattr(pilot, "environment", lambda: {"gpu": "synthetic-no-device"})
    monkeypatch.setattr(pilot, "integrate_gpu", fake_gpu)
    monkeypatch.setattr(pilot, "_profile_row", fake_fit)


def collect_fixture(tmp_path, prepared):
    directory = tmp_path / "collection"
    receipt = pilot.collect(prepared, directory)
    assert receipt["collection_passed"]
    return directory, pilot.sha256_file(directory / "receipt.json"), receipt


class FixtureEvidenceStore:
    """Read-only synthetic stand-in for prax: never opens a network connection."""

    def __init__(self, directory):
        self.directory = directory
        self.inventory = {"assets": [{"path": "collection/" + path.name,
                                       "bytes": path.stat().st_size, "sha256": pilot.sha256_file(path)}
                                      for path in sorted(directory.iterdir())]}
        self.audits = 0
        self.fetched = []

    def audit(self):
        for row in self.inventory["assets"]:
            path = self.directory / Path(row["path"]).name
            if not path.is_file() or path.stat().st_size != row["bytes"] or pilot.sha256_file(path) != row["sha256"]:
                raise ValueError("synthetic full inventory hash/size mismatch")
        self.audits += 1
        return deepcopy(self.inventory)

    def fetch_asset(self, row, destination, *, maximum_bytes):
        assert self.audits >= 1
        assert row in self.inventory["assets"] and row["bytes"] <= maximum_bytes
        source = self.directory / Path(row["path"]).name
        with destination.open("xb") as stream:
            stream.write(source.read_bytes())
        self.fetched.append(row["path"])
        return destination


def test_remote_provider_matches_local_output_exactly_and_eviction_preserves_originals(
        tmp_path, prepared, fake_runtime, monkeypatch):
    monkeypatch.setattr(pilot, "utc_now", lambda: "2000-01-01T00:00:00Z")
    monkeypatch.setattr(pilot.time, "monotonic", lambda: 0.0)
    directory, digest, _ = collect_fixture(tmp_path, prepared)
    store = FixtureEvidenceStore(directory)
    originals = {path.name: path.read_bytes() for path in directory.iterdir()}
    monkeypatch.setattr(pilot, "integrate_gpu", lambda *args, **kwargs: pytest.fail("analysis may not call GPU"))
    local = pilot.analyze(prepared, directory, digest, tmp_path / "local-analysis")
    cache_parent = tmp_path / "cache"
    cache_parent.mkdir()
    with RemoteCollectionAssets(store, cache_parent=cache_parent) as provider:
        def fitting(*args):
            assert store.audits == 1  # Entire immutable inventory checked before the first fit.
            raw_copies = list(cache_parent.rglob("*.npz"))
            assert len(raw_copies) == 1
            assert not any(name.endswith(".npz") for name in store.fetched[:5])
            return fake_fit(*args)
        monkeypatch.setattr(pilot, "_profile_row", fitting)
        remote = pilot.analyze(prepared, None, digest, tmp_path / "remote-analysis", asset_provider=provider)
        assert provider.full_audits_completed == 2
        assert provider.peak_cache_bytes <= provider.maximum_asset_bytes
    assert remote["passed"] and remote == local
    local_files = {path.name: path.read_bytes() for path in (tmp_path / "local-analysis").iterdir()}
    remote_files = {path.name: path.read_bytes() for path in (tmp_path / "remote-analysis").iterdir()}
    assert local_files == remote_files
    assert list(cache_parent.iterdir()) == []
    assert originals == {path.name: path.read_bytes() for path in directory.iterdir()}


def test_remote_provider_does_not_relax_collection_source_equality(tmp_path, prepared, fake_runtime, monkeypatch):
    directory, digest, _ = collect_fixture(tmp_path, prepared)
    store = FixtureEvidenceStore(directory)
    changed_source = deepcopy(prepared)
    changed_source["source"]["commit"] = "b" * 40
    monkeypatch.setattr(pilot, "_profile_row", lambda *args: pytest.fail("different source must not fit"))
    with RemoteCollectionAssets(store, cache_parent=tmp_path) as provider:
        result = pilot.analyze(changed_source, None, digest, tmp_path / "analysis", asset_provider=provider)
    assert result["status"] == "failed" and result["nomination_result"] is None
    assert "source binding mismatch" in result["failure"]["message"]
    assert store.fetched == ["collection/receipt.json"]


@pytest.mark.parametrize("asset", ["receipt.json", "batch-0000-profile-0.json", "batch-0000-profile-0.npz"])
@pytest.mark.parametrize("mutation", ["changed", "missing"])
def test_remote_provider_rejects_all_changed_or_missing_originals_before_fit(
        tmp_path, prepared, fake_runtime, monkeypatch, asset, mutation):
    directory, digest, _ = collect_fixture(tmp_path, prepared)
    store = FixtureEvidenceStore(directory)
    path = directory / asset
    if mutation == "changed":
        with path.open("ab") as stream:
            stream.write(b" ")
    else:
        path.unlink()  # Synthetic fixture only; never an original research asset.
    monkeypatch.setattr(pilot, "_profile_row", lambda *args: pytest.fail("bad evidence must not be fitted"))
    with RemoteCollectionAssets(store, cache_parent=tmp_path) as provider:
        result = pilot.analyze(prepared, None, digest, tmp_path / "analysis", asset_provider=provider)
    assert result["status"] == "failed" and result["nomination_result"] is None
    assert "hash/size mismatch" in result["failure"]["message"]
    assert not store.fetched
    assert not list(tmp_path.glob("butterfly-exp477-analysis-*"))


@pytest.mark.parametrize("asset", ["receipt.json", "batch-0000-profile-0.json", "batch-0000-profile-0.npz", "started.json"])
@pytest.mark.parametrize("mutation", ["changed", "missing"])
def test_remote_provider_rehashes_even_undownloaded_originals_after_fit(
        tmp_path, prepared, fake_runtime, asset, mutation):
    directory, digest, _ = collect_fixture(tmp_path, prepared)
    store = FixtureEvidenceStore(directory)
    def mutate():
        if mutation == "changed":
            with (directory / asset).open("ab") as stream:
                stream.write(b" ")
        else:
            (directory / asset).unlink()  # Synthetic fixture only.
    with RemoteCollectionAssets(store, cache_parent=tmp_path) as provider:
        result = pilot.analyze(prepared, None, digest, tmp_path / "analysis",
                               source_recheck=mutate, asset_provider=provider)
    assert result["status"] == "failed" and result["nomination_result"] is None
    assert not result["passed"]
    assert result["completed_candidate_ids"] == ["p-0", "p-1", "p-2"]
    assert "mismatch" in result["failure"]["message"] or result["failure"]["type"] == "FileNotFoundError"
    assert "collection/started.json" not in store.fetched
    assert not list(tmp_path.glob("butterfly-exp477-analysis-*"))


@pytest.mark.parametrize("kind", ["time_order", "fractional_seed", "out_of_range_seed"])
def test_raw_event_identity_gates(tmp_path, prepared, fake_runtime, monkeypatch, kind):
    def malformed(candidates, **kwargs):
        result = fake_gpu(candidates, **kwargs)
        record = result["records"][0]
        if kind == "time_order":
            record["times"][0][1] = record["times"][0][0]
        elif kind == "fractional_seed":
            record["seed_ids"] = np.asarray([0.5, 1.0])
        else:
            record["seed_ids"][0] = 100
        return result
    monkeypatch.setattr(pilot, "integrate_gpu", malformed)
    result = pilot.collect(prepared, tmp_path / "bad")
    assert not result["collection_passed"]


def test_raw_changed_after_fit_invalidates_analysis(tmp_path, prepared, fake_runtime):
    directory, digest, receipt = collect_fixture(tmp_path, prepared)
    def mutate_after_fitting():
        raw = directory / receipt["batches"][0]["profiles"][0]["raw"]["path"]
        with raw.open("ab") as stream:
            stream.write(b"mutation")
    result = pilot.analyze(prepared, directory, digest, tmp_path / "analysis", source_recheck=mutate_after_fitting)
    assert not result["passed"]
    assert result["status"] == "failed"
    assert "hash/size mismatch" in result["failure"]["message"]


def test_collection_never_fits_and_preserves_all_profiles_before_local_analysis(tmp_path, prepared, fake_runtime, monkeypatch):
    calls = []

    def integrate(candidates, **kwargs):
        calls.append(([row["id"] for row in candidates], kwargs["dt"]))
        return fake_gpu(candidates, **kwargs)

    monkeypatch.setattr(pilot, "integrate_gpu", integrate)
    monkeypatch.setattr(pilot, "_profile_row", lambda *args: pytest.fail("collection must not fit"))
    directory, digest, receipt = collect_fixture(tmp_path, prepared)
    assert calls == [(["p-0", "p-1"], 0.01), (["p-0", "p-1"], 0.005), (["p-2"], 0.01), (["p-2"], 0.005)]
    assert receipt["nomination_performed"] is False
    assert not list(directory.glob("*-fits.json"))
    assert receipt["started_utc"] <= receipt["finished_utc"]
    with np.load(directory / "batch-0000-profile-0.npz", allow_pickle=False) as data:
        assert all(data[key].dtype.kind != "O" for key in data.files)
        assert data["candidate_ids"].tolist() == ["p-0", "p-1"]
        assert data["candidate_record_offsets"].tolist() == [0, 2, 4]
        assert data["trajectory_offsets"].tolist() == [0, 3, 6, 9, 12]
        assert np.all(data["normalized_section_transversality"] > 0)
    monkeypatch.setattr(pilot, "_profile_row", fake_fit)
    monkeypatch.setattr(pilot, "integrate_gpu", lambda *args, **kwargs: pytest.fail("local analysis must not use GPU"))
    analyzed = pilot.analyze(prepared, directory, digest, tmp_path / "analysis")
    assert analyzed["status"] == "completed" and analyzed["passed"]
    assert analyzed["nomination_result"]["direct_candidate_ids"] == ["p-0", "p-1", "p-2"]
    assert all(row["reconstruction_count"] == 12 for row in analyzed["combined_candidates"])
    assert analyzed["gpu_calls_performed"] is False


@pytest.mark.parametrize("failure", ["saturated", "tangent", "nonfinite"])
def test_raw_validity_failure_saves_evidence_and_stops_before_later_profiles(tmp_path, prepared, fake_runtime, monkeypatch, failure):
    calls = []

    def integrate(candidates, **kwargs):
        calls.append(kwargs["dt"])
        result = fake_gpu(candidates, **kwargs)
        if failure == "saturated":
            result["records"][0]["states"][0] = np.tile([1.0, -1.0, 0.01], (32, 1))
            result["records"][0]["times"][0] = np.linspace(80.0, 140.0, 32)
        elif failure == "tangent":
            result["records"][0]["states"][0][:] = [1.0, -0.01, 0.01]
        else:
            result["records"][0]["states"][0][0, 0] = np.nan
        return result

    monkeypatch.setattr(pilot, "integrate_gpu", integrate)
    directory = tmp_path / "collection"
    result = pilot.collect(prepared, directory)
    assert result["status"] == "failed" and not result["collection_passed"]
    assert calls == [0.01]
    assert (directory / "batch-0000-profile-0.npz").is_file()
    assert (directory / "batch-0000-profile-0.json").is_file()
    assert not list(directory.glob("*-fits.json"))
    assert len(result["uncompleted_candidate_ids"]) == 3
    json.loads((directory / "receipt.json").read_bytes())


def test_deadline_after_gpu_preserves_raw_and_prevents_next_call(tmp_path, prepared, fake_runtime, monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(pilot.time, "monotonic", lambda: clock[0])

    def integrate(candidates, **kwargs):
        clock[0] = 61.0
        return fake_gpu(candidates, **kwargs)

    monkeypatch.setattr(pilot, "integrate_gpu", integrate)
    result = pilot.collect(prepared, tmp_path / "collection")
    assert result["failure"]["type"] == "TimeoutError"
    assert (tmp_path / "collection/batch-0000-profile-0.npz").is_file()
    assert not (tmp_path / "collection/batch-0000-profile-1.npz").exists()


@pytest.mark.parametrize("error", [OSError("synthetic failure"), KeyboardInterrupt("synthetic termination")])
def test_interrupted_collection_retains_first_profile_and_failure_receipt(tmp_path, prepared, fake_runtime, monkeypatch, error):
    calls = []

    def integrate(candidates, **kwargs):
        calls.append(kwargs["dt"])
        if len(calls) == 2:
            raise error
        return fake_gpu(candidates, **kwargs)

    monkeypatch.setattr(pilot, "integrate_gpu", integrate)
    result = pilot.collect(prepared, tmp_path / "collection")
    assert result["status"] == "failed"
    assert result["failure"]["type"] == type(error).__name__
    assert result["automatic_retry_or_resume"] is False
    assert (tmp_path / "collection/batch-0000-profile-0.npz").is_file()


def test_existing_output_is_never_overwritten_or_resumed(tmp_path, prepared, fake_runtime):
    directory, _, _ = collect_fixture(tmp_path, prepared)
    original = (directory / "receipt.json").read_bytes()
    with pytest.raises(FileExistsError):
        pilot.collect(prepared, directory)
    assert (directory / "receipt.json").read_bytes() == original


@pytest.mark.parametrize("asset", ["receipt.json", "batch-0000-profile-0.json", "batch-0000-profile-0.npz"])
def test_analysis_rejects_changed_collection_before_any_fits(tmp_path, prepared, fake_runtime, monkeypatch, asset):
    directory, digest, _ = collect_fixture(tmp_path, prepared)
    with (directory / asset).open("ab") as stream:
        stream.write(b" ")
    monkeypatch.setattr(pilot, "_profile_row", lambda *args: pytest.fail("tampered inputs must not be fitted"))
    result = pilot.analyze(prepared, directory, digest, tmp_path / "analysis")
    assert result["status"] == "failed" and not result["passed"]
    assert "mismatch" in result["failure"]["message"]


def test_analysis_deadline_preserves_completed_fit_file(tmp_path, prepared, fake_runtime, monkeypatch):
    directory, digest, _ = collect_fixture(tmp_path, prepared)
    clock = [0.0]
    monkeypatch.setattr(pilot.time, "monotonic", lambda: clock[0])

    def fit(*args):
        clock[0] = 61.0
        return fake_fit(*args)

    monkeypatch.setattr(pilot, "_profile_row", fit)
    result = pilot.analyze(prepared, directory, digest, tmp_path / "analysis")
    assert result["status"] == "failed" and result["failure"]["type"] == "TimeoutError"
    assert (tmp_path / "analysis/batch-0000-profile-0-fits.json").is_file()
    assert result["nomination_result"] is None


def test_nonfinite_resolved_fit_cannot_nominate(tmp_path, prepared, fake_runtime, monkeypatch):
    directory, digest, _ = collect_fixture(tmp_path, prepared)

    def fit(*args):
        row = fake_fit(*args)
        row["supports"][0]["assignments"][0]["normalized_signed_residuals"][0] = np.nan
        return row

    monkeypatch.setattr(pilot, "_profile_row", fit)
    result = pilot.analyze(prepared, directory, digest, tmp_path / "analysis")
    assert result["status"] == "failed" and not result["passed"]
    assert "nonfinite" in result["failure"]["message"]


def test_final_source_failure_prevents_collection_qualification(tmp_path, prepared, fake_runtime):
    def changed_source():
        raise ValueError("source changed")

    result = pilot.collect(prepared, tmp_path / "collection", source_recheck=changed_source)
    assert result["status"] == "failed" and not result["collection_passed"]
    assert len(result["completed_candidate_ids"]) == 3


def test_preflight_cli_never_calls_gpu_or_fitter(prepared, monkeypatch, capsys):
    monkeypatch.setattr(pilot, "prepare", lambda *args, **kwargs: prepared)
    monkeypatch.setattr(pilot, "environment", lambda: pytest.fail("preflight must not require CUDA"))
    monkeypatch.setattr(pilot, "integrate_gpu", lambda *args, **kwargs: pytest.fail("preflight must not integrate"))
    monkeypatch.setattr(pilot, "_profile_row", lambda *args: pytest.fail("preflight must not fit"))
    assert pilot.main(["--manifest", "synthetic.json", "--source-commit", COMMIT, "--mode", "preflight"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["preflight_passed"] and not output["target_computation_performed"]


@pytest.fixture
def preflight_files(tmp_path, prepared, monkeypatch):
    manifest = deepcopy(prepared["manifest"])
    parent = deepcopy(prepared["parent"])
    candidates = []
    for index in range(551):
        candidate = deepcopy(prepared["candidates"][0])
        candidate["id"] = f"synthetic-{index}"
        candidates.append(candidate)
    candidate_path = tmp_path / "candidates.json"
    candidate_path.write_text(json.dumps({"candidates": candidates}))
    candidate_hash = pilot.sha256_file(candidate_path)
    parent["candidate_input_sha256"] = candidate_hash
    parent_path = tmp_path / "parent.json"
    parent_path.write_text(json.dumps(parent))
    parent_hash = pilot.sha256_file(parent_path)
    manifest["candidate_input"]["sha256"] = candidate_hash
    manifest["parent_design"]["sha256"] = parent_hash
    manifest_path = tmp_path / "pilot.json"
    manifest_path.write_text(json.dumps(manifest))
    monkeypatch.setattr(pilot, "PARENT_SHA256", parent_hash)
    monkeypatch.setattr(pilot, "CANDIDATE_SHA256", candidate_hash)
    monkeypatch.setattr(pilot, "source_binding", lambda *args, **kwargs: {"commit": COMMIT})
    return manifest_path, manifest


def test_preflight_binds_all_candidates_and_parent_design(preflight_files, tmp_path):
    path, _ = preflight_files
    result = pilot.prepare(path, COMMIT, root=tmp_path)
    assert len(result["candidates"]) == 551
    assert result["parent"]["profiles"][1]["dt"] == 0.005


@pytest.mark.parametrize("change", ["nan", "negative", "batch", "word", "split", "parent_hash", "candidate_hash"])
def test_preflight_invalid_definitions_fail_closed(preflight_files, tmp_path, change):
    path, manifest = preflight_files
    if change == "nan":
        manifest["validity"]["minimum_normalized_section_transversality"] = float("nan")
    elif change == "negative":
        manifest["execution"]["maximum_wall_seconds"] = -1
    elif change == "batch":
        manifest["execution"]["batch_size"] = True
    elif change == "word":
        manifest["interpretation"]["jones_words_used"] = True
    elif change == "split":
        manifest["execution"]["collect_then_local_analyze"] = False
    elif change == "parent_hash":
        manifest["parent_design"]["sha256"] = "d" * 64
    else:
        manifest["candidate_input"]["sha256"] = "e" * 64
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        pilot.prepare(path, COMMIT, root=tmp_path)


@pytest.mark.parametrize("kind", ["dirty", "uncommitted", "unpushed", "failed_status"])
def test_git_source_checks_fail_closed(tmp_path, monkeypatch, kind):
    path = tmp_path / "pilot.json"
    path.write_bytes(b"{}")

    def git(_root, *args):
        if args[0] == "rev-parse":
            return COMMIT
        if args[0] == "status":
            if kind == "failed_status":
                raise subprocess.CalledProcessError(1, ["git", "status"])
            return " M source.py" if kind == "dirty" else ""
        return "" if kind == "unpushed" else COMMIT + " refs/remotes/origin/synthetic"

    monkeypatch.setattr(pilot, "git", git)
    monkeypatch.setattr(pilot.subprocess, "check_output", lambda *args, **kwargs: b"different" if kind == "uncommitted" else b"{}")
    with pytest.raises(ValueError):
        pilot.source_binding(tmp_path, COMMIT, path, b"{}")


def test_inventory_requires_every_runtime_source_and_unchanged_bytes(tmp_path):
    (tmp_path / "scripts").mkdir()
    for name in ("pilot.json", "pyproject.toml", "uv.lock", "scripts/runtime.py"):
        (tmp_path / name).write_text("{}")
    files = {name: pilot.sha256_file(tmp_path / name) for name in ("pilot.json", "pyproject.toml", "uv.lock")}
    document = {"schema": "butterfly.source-inventory.v1", "source_commit": COMMIT,
                "pushed_source_commit": COMMIT, "files": files}
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps(document))
    with pytest.raises(ValueError, match="closure"):
        pilot.source_binding(tmp_path, COMMIT, tmp_path / "pilot.json", b"{}", inventory=inventory,
                             inventory_sha256=pilot.sha256_file(inventory))
    files["scripts/runtime.py"] = pilot.sha256_file(tmp_path / "scripts/runtime.py")
    inventory.write_text(json.dumps(document))
    digest = pilot.sha256_file(inventory)
    assert pilot.source_binding(tmp_path, COMMIT, tmp_path / "pilot.json", b"{}", inventory=inventory,
                                inventory_sha256=digest)["mode"] == "explicit_inventory"
    (tmp_path / "scripts/runtime.py").write_text("changed")
    with pytest.raises(ValueError, match="mismatch"):
        pilot.source_binding(tmp_path, COMMIT, tmp_path / "pilot.json", b"{}", inventory=inventory,
                             inventory_sha256=digest)


def test_raw_loader_rejects_pickle_arrays(tmp_path, prepared):
    path = tmp_path / "bad.npz"
    np.savez(path, candidate_ids=np.asarray([object()], dtype=object))
    with pytest.raises(ValueError, match="Object arrays"):
        pilot.load_raw(path, ["p-0"], prepared["parent"])
