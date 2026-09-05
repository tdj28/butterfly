"""Tiny synthetic archival controls, without SSH/cloud calls or target fitting."""

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tarfile

import pytest

from scripts import archive_symbolic_collection_to_ssh as archive


COMMIT = "a" * 40
NONCE = "b" * 32


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True))
    return archive.cloud.describe(path)


def write_tar(path, files):
    with tarfile.open(path, "w:") as output:
        for name, raw in files.items():
            member = tarfile.TarInfo(name)
            member.size = len(raw)
            output.addfile(member, io.BytesIO(raw))


@pytest.fixture
def evidence(tmp_path, monkeypatch):
    collection = tmp_path / "original"
    incoming = collection / "prepared-inputs"
    incoming.mkdir(parents=True)
    root = tmp_path / "source"
    runtime = {"post_termination_archive": deepcopy(archive.POLICY), "retrieval": deepcopy(archive.LIMITS),
               "lifecycle": {"maximum_spend_usd": 3.0}}
    plan = {**runtime["lifecycle"], "experiment_id": "EXP-477", "source_commit": COMMIT}
    paths = {archive.cloud.PILOT_MANIFEST: b"{}", "scripts/qualify_symbolic_gpu_records.py": b"# control",
             "scripts/symbolic_ssh_storage.py": b"# storage", "pyproject.toml": b"", "uv.lock": b"",
             archive.cloud.RUNTIME_MANIFEST: json.dumps(runtime, sort_keys=True).encode()}
    for name, raw in paths.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    write_tar(incoming / "source.tar", paths)
    inventory = {"schema": "butterfly.source-inventory.v1", "source_commit": COMMIT, "pushed_source_commit": COMMIT,
                 "source_archive_sha256": archive.pilot.sha256_file(incoming / "source.tar"),
                 "files": {name: hashlib.sha256(raw).hexdigest() for name, raw in paths.items()}}
    write_json(incoming / "source-inventory.json", inventory)
    source = {"mode": "explicit_inventory", "commit": COMMIT,
              "inventory_sha256": archive.pilot.sha256_file(incoming / "source-inventory.json")}
    deployment_parent = {"experiment_id": "synthetic-deployment-control", "ensemble": {"x_count": 128, "z_count": 64},
                         "profiles": [{"dt": .02}, {"dt": .01}], "anchor": {"parameters": {"a": .1, "b": .2, "c": 1.0}}}
    control_config = deepcopy(deployment_parent)
    control_config["ensemble"].update(x_count=8, z_count=8)
    control = {"config": control_config,
               "profiles": [{**profile, "records": [{"synthetic": True}]} for profile in deployment_parent["profiles"]],
               "candidate": {"parameters": deployment_parent["anchor"]["parameters"], "section_states": [[0., -1., 0.]] * 8}}
    monkeypatch.setattr(archive.cloud.qualification, "parent_design", lambda: deepcopy(deployment_parent))
    cpu = {"schema": "butterfly.symbolic-gpu-deployment-control.v1", "mode": "cpu", "passed": True,
           "source": source, "parent_sha256": archive.cloud.qualification.PARENT_HASH,
           "qualification_script_sha256": inventory["files"]["scripts/qualify_symbolic_gpu_records.py"],
           "state_atol": archive.cloud.qualification.STATE_ATOL, "time_atol": archive.cloud.qualification.TIME_ATOL,
           "control": control}
    write_json(incoming / "cpu-control.json", cpu)
    write_json(incoming / "candidates.json", {"candidates": [{"id": "synthetic"}]})
    monkeypatch.setattr(archive.cloud.worker, "CANDIDATE_HASH", archive.pilot.sha256_file(incoming / "candidates.json"))
    monkeypatch.setattr(archive.cloud.worker, "CANDIDATE_BYTES", (incoming / "candidates.json").stat().st_size)
    verified = {"source": source, "manifest_sha256": "c" * 64,
                "input_hashes": {"candidates": archive.pilot.sha256_file(incoming / "candidates.json"), "parent_design": "d" * 64},
                "candidates": [{"id": "synthetic"}], "parent": {"profiles": [{"dt": .01}, {"dt": .005}]},
                "manifest": {"execution": {"batch_size": 8}}}
    monkeypatch.setattr(archive.pilot, "prepare", lambda *args, **kwargs: deepcopy(verified))
    monkeypatch.setattr(archive.pilot, "source_binding", lambda *args, **kwargs: deepcopy(source))
    prepared = {"schema": "butterfly.symbolic-cloud-preparation.v1", "source_commit": COMMIT,
                "plan": plan, "runtime": deepcopy(runtime),
                "ssh_storage_directory": None, "pilot_manifest_sha256": verified["manifest_sha256"],
                "collection_binding": {"input_hashes": verified["input_hashes"], "candidate_ids": ["synthetic"],
                                       "profiles": verified["parent"]["profiles"], "batch_size": 8},
                "cpu_control_sha256": archive.pilot.sha256_file(incoming / "cpu-control.json"),
                "assets": {path.name: archive.cloud.describe(path) for path in incoming.iterdir()}}
    write_json(collection / "preparation.json", prepared)
    retrieved = collection / "retrieved"
    write_json(retrieved / "gpu-control.json", {**cpu, "mode": "gpu", "cpu_control_sha256": prepared["cpu_control_sha256"],
               "benchmark": {"projected_collection_seconds_with_margin": 100}})
    receipt = {"schema": "butterfly.symbolic-center-collection.v1", "experiment_id": "EXP-477", "status": "completed",
               "collection_passed": True, "nomination_performed": False, "source": source,
               "manifest_sha256": verified["manifest_sha256"], "input_hashes": verified["input_hashes"],
               "completed_candidate_ids": ["synthetic"], "uncompleted_candidate_ids": [],
               "batches": [{"index": 0, "candidate_ids": ["synthetic"], "profiles": []}]}
    for index, profile in enumerate(verified["parent"]["profiles"]):
        name = f"batch-0000-profile-{index}"
        raw = retrieved / "collection" / (name + ".npz")
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_bytes(b"synthetic opaque bytes; never fitted")
        metadata = {"schema": "butterfly.symbolic-center-raw-batch.v1", "validity_passed": True,
                    "candidate_ids": ["synthetic"], "profile": profile, "raw": archive.cloud.describe(raw)}
        metadata["metadata_file"] = write_json(raw.with_suffix(".json"), metadata)
        receipt["batches"][0]["profiles"].append(metadata)
        write_json(retrieved / "collection" / (name + "-checkpoint.json"), {"candidate_ids": ["synthetic"], "raw_metadata": metadata})
    write_json(retrieved / "collection/receipt.json", receipt)
    for name in ("collection/started.json", "environment/python.txt", "environment/pip-freeze.txt", "environment/nvidia-smi.txt",
                 "environment/torch.json", "logs/setup.log", "logs/qualification.log", "logs/collection.log"):
        write_json(retrieved / name, {})
    for stage in ("setup", "qualification", "collection"):
        write_json(retrieved / "status" / (stage + ".json"), {"passed": True})
    raw_inventory = {"schema": "butterfly.symbolic-remote-assets.v1",
                     "assets": [{**archive.cloud.describe(path), "path": path.relative_to(retrieved).as_posix()}
                                for path in sorted(retrieved.rglob("*")) if path.is_file()]}
    write_json(retrieved / "retrieval-manifest.json", raw_inventory)
    write_tar(collection / "retrieved.tar", {"retrieval-manifest.json": json.dumps(raw_inventory).encode(),
                                            **{row["path"]: (retrieved / row["path"]).read_bytes() for row in raw_inventory["assets"]}})
    workload = {"schema": "butterfly.symbolic-cloud-workload.v1", "source_commit": COMMIT,
                "remote_directory": "/workspace/butterfly-exp477-" + NONCE, "passed": True,
                "retrieval_verified": True, "complete_raw_closure_verified": True, "owned_writers_quiescent": True,
                "target_collection_started": True, "stages": [{"name": name} for name in ("setup", "qualification", "collection")],
                "retrieval_archive": archive.cloud.describe(collection / "retrieved.tar")}
    write_json(collection / "workload.json", workload)
    ownership = {"schema": "butterfly.runpod-ownership.v1", "pod_id": "owned-synthetic", "nonce": NONCE,
                 "name": "butterfly-exp477-" + NONCE, "preexisting_ids": ["other-one", "other-two"]}
    lifecycle = {**ownership, "schema": "butterfly.runpod-symbolic-worker.v1", "termination_verified": True,
                 "contract_qualified": True, "post_delete_direct_lookup": "HTTP 404", "post_delete_inventory_ids": ["other-one", "other-two"],
                 "persistent_volume_requested": False, "unrelated_resources_mutated": False, "plan": prepared["plan"]}
    args = SimpleNamespace(collection_output_dir=collection, source_commit=COMMIT, source_inventory=None, source_inventory_sha256=None,
                           remote_dir=archive.storage.BASE_DIRECTORY + "/synthetic-archive", output_dir=tmp_path / "archival")
    for name, value in (("ownership", ownership), ("lifecycle", lifecycle)):
        path = tmp_path / (name + ".json")
        descriptor = write_json(path, value)
        setattr(args, name + "_receipt", path)
        setattr(args, name + "_receipt_sha256", descriptor["sha256"])
    return args, root, raw_inventory


def cli(args, *, execute=False):
    options = ["--collection-output-dir", str(args.collection_output_dir), "--source-commit", args.source_commit,
               "--remote-dir", args.remote_dir, "--output-dir", str(args.output_dir)]
    for name in ("lifecycle", "ownership"):
        options.extend(["--" + name + "-receipt", str(getattr(args, name + "_receipt")),
                        "--" + name + "-receipt-sha256", getattr(args, name + "_receipt_sha256")])
    return options + (["--execute"] if execute else [])


def test_preflight_checks_complete_evidence_without_extracting_or_fitting(evidence):
    args, root, _ = evidence
    before = {path.relative_to(args.collection_output_dir): path.read_bytes() for path in args.collection_output_dir.rglob("*") if path.is_file()}
    checked = archive.preflight(args, root=root)
    assert checked["raw_closure"] == {"complete": True, "candidate_count": 1, "profile_batch_count": 2}
    assert before == {path.relative_to(args.collection_output_dir): path.read_bytes() for path in args.collection_output_dir.rglob("*") if path.is_file()}


@pytest.mark.parametrize("target,change", [
    ("workload.json", "nonce"), ("workload.json", "closure"), ("preparation.json", "policy"),
    ("preparation.json", "plan"), ("preparation.json", "assets"), ("prepared-inputs/cpu-control.json", "bytes"),
    ("prepared-inputs/source.tar", "bytes"), ("retrieved.tar", "bytes"),
    ("retrieved/collection/batch-0000-profile-0.npz", "bytes"), ("retrieved/gpu-control.json", "missing"),
])
def test_preflight_rejects_changed_or_incomplete_local_evidence(evidence, target, change):
    args, root, _ = evidence
    path = args.collection_output_dir / target
    if change == "missing":
        path.unlink()
    elif change == "bytes":
        with path.open("ab") as stream:
            stream.write(b"mutated")
    else:
        value = json.loads(path.read_bytes())
        if change == "nonce": value["remote_directory"] = "/workspace/butterfly-exp477-" + "c" * 32
        elif change == "closure": value["complete_raw_closure_verified"] = False
        elif change == "policy": value["runtime"]["post_termination_archive"]["maximum_transfer_seconds"] = 900
        elif change == "plan": value["plan"]["source_commit"] = "c" * 40
        elif change == "assets": value["assets"]["unexpected.env"] = {}
        write_json(path, value)
    with pytest.raises((ValueError, RuntimeError, OSError)):
        archive.preflight(args, root=root)


def test_source_tar_cannot_replace_original_members_even_with_rewritten_container_hash(evidence):
    args, _, _ = evidence
    inventory = archive.document(args.collection_output_dir / "prepared-inputs/source-inventory.json")
    path = args.collection_output_dir / "prepared-inputs/source.tar"
    write_tar(path, {"scripts/unbound.py": b"# not the source"})
    inventory["source_archive_sha256"] = archive.pilot.sha256_file(path)
    with pytest.raises(ValueError, match="file hashes"):
        archive.verify_source_archive(path, inventory)


def test_staged_candidate_cannot_change_with_rewritten_preparation_descriptor(evidence):
    args, root, _ = evidence
    staged = args.collection_output_dir / "prepared-inputs/candidates.json"
    staged.write_bytes(b'{"candidates":[]}')
    path = args.collection_output_dir / "preparation.json"
    prepared = archive.document(path)
    prepared["assets"]["candidates.json"] = archive.cloud.describe(staged)
    write_json(path, prepared)
    with pytest.raises(ValueError, match="staged candidates"):
        archive.preflight(args, root=root)


def test_cpu_uses_distinct_deployment_parent_not_scientific_scout_parent(evidence):
    args, root, _ = evidence
    checked = archive.preflight(args, root=root)  # Real validate_control, no integration.
    cpu = json.loads(checked["cpu_bytes"])
    assert [row["dt"] for row in cpu["control"]["profiles"]] == [.02, .01]
    assert [row["dt"] for row in checked["prepared"]["collection_binding"]["profiles"]] == [.01, .005]


def test_runtime_and_plan_cannot_change_even_with_self_consistent_lifecycle(evidence):
    args, root, _ = evidence
    path = args.collection_output_dir / "preparation.json"
    prepared = archive.document(path)
    prepared["runtime"]["lifecycle"]["maximum_spend_usd"] = 30.0
    prepared["plan"]["maximum_spend_usd"] = 30.0
    write_json(path, prepared)
    lifecycle = archive.document(args.lifecycle_receipt)
    lifecycle["plan"] = prepared["plan"]
    args.lifecycle_receipt_sha256 = write_json(args.lifecycle_receipt, lifecycle)["sha256"]
    with pytest.raises(ValueError, match="frozen source contract"):
        archive.preflight(args, root=root)


@pytest.mark.parametrize("kind", ["member_hash", "missing", "unsafe"])
def test_raw_archive_content_gate_does_not_trust_container_hash(evidence, kind):
    args, _, inventory = evidence
    files = {"retrieval-manifest.json": json.dumps(inventory).encode(),
             **{row["path"]: (args.collection_output_dir / "retrieved" / row["path"]).read_bytes() for row in inventory["assets"]}}
    target = "collection/batch-0000-profile-0.npz"
    if kind == "member_hash": files[target] = b"x" * len(files[target])
    elif kind == "missing": files.pop(target)
    else: files["../escape"] = b"escape"
    path = args.collection_output_dir / "retrieved.tar"
    write_tar(path, files)
    with pytest.raises(ValueError):
        archive.verify_archive(path, inventory)


def patch_preflight(monkeypatch, root):
    original = archive.preflight
    monkeypatch.setattr(archive, "preflight", lambda args: original(args, root=root))


def test_default_is_local_only_and_no_overwrite(evidence, monkeypatch):
    args, root, _ = evidence
    patch_preflight(monkeypatch, root)
    monkeypatch.setattr(archive.storage, "SshEvidenceStore", lambda *args, **kwargs: pytest.fail("unexpected SSH"))
    assert archive.main(cli(args)) == 0
    receipt = archive.document(args.output_dir / "receipt.json")
    assert receipt["mode"] == "preflight" and not receipt["ssh_upload_started"] and receipt["passed"]
    with pytest.raises(FileExistsError):
        archive.main(cli(args))


@pytest.mark.parametrize("failure", [None, "timeout", "remote_closure", "changed_during_upload", "bad_ack"])
def test_execute_runs_only_after_termination_retains_originals_and_binds_remote_identity(evidence, monkeypatch, failure):
    args, root, inventory = evidence
    patch_preflight(monkeypatch, root)
    events = []
    class FakeStore:
        def __init__(self, remote_dir, *, local_control_directory):
            assert remote_dir == args.remote_dir
            self.binding = {}
            events.append("new-remote-folder")
        def prepare(self, prepared, cpu, *, helper_sha256):
            assert self.binding["task_worker_id"] == "owned-synthetic"
            assert self.binding["task_worker_nonce"] == NONCE and self.binding["source_commit"] == COMMIT
            events.append("prepare")
        def receive(self, command, *, seconds, progress):
            assert command == ["/bin/cat", str(args.collection_output_dir / "retrieved.tar")]
            assert 0 < seconds <= 7200
            events.append("receive")
            if failure == "timeout": raise TimeoutError("synthetic transfer deadline")
            if failure == "changed_during_upload":
                with (args.collection_output_dir / "workload.json").open("ab") as stream: stream.write(b" ")
            descriptor = archive.cloud.describe(args.collection_output_dir / "retrieved.tar")
            if failure == "bad_ack": descriptor["sha256"] = "0" * 64
            return descriptor
        def finalize(self, *, seconds):
            assert 0 < seconds <= 7200
            events.append("finalize")
            self.binding["retrieval_manifest_sha256"] = "d" * 64
            write_json(args.output_dir / "remote-storage.json", self.binding)
            return {"retrieval_verified": True, "complete_raw_closure_verified": failure != "remote_closure"}
        def retain_compact_receipts(self, *, seconds):
            events.append("compact")
            return inventory
    monkeypatch.setattr(archive.storage, "SshEvidenceStore", FakeStore)
    original_tar = (args.collection_output_dir / "retrieved.tar").read_bytes()
    assert archive.main(cli(args, execute=True)) == (0 if failure is None else 2)
    receipt = archive.document(args.output_dir / "receipt.json")
    assert receipt["worker_termination_verified_before_upload"] and receipt["runpod_calls_performed"] is False
    assert receipt["local_originals_removed"] is False
    assert (args.collection_output_dir / "retrieved.tar").read_bytes() == original_tar
    if failure is None: assert events == ["new-remote-folder", "prepare", "receive", "finalize", "compact"]
    elif failure != "remote_closure": assert "finalize" not in events


def test_unterminated_worker_cannot_trigger_even_ssh_preparation(evidence, monkeypatch):
    args, root, _ = evidence
    patch_preflight(monkeypatch, root)
    lifecycle = archive.document(args.lifecycle_receipt)
    lifecycle["termination_verified"] = False
    args.lifecycle_receipt_sha256 = write_json(args.lifecycle_receipt, lifecycle)["sha256"]
    monkeypatch.setattr(archive.storage, "SshEvidenceStore", lambda *args, **kwargs: pytest.fail("unexpected SSH"))
    assert archive.main(cli(args, execute=True)) == 2
    assert not archive.document(args.output_dir / "receipt.json")["ssh_upload_started"]


def test_output_cannot_be_written_inside_original_evidence(evidence):
    args, _, _ = evidence
    args.output_dir = args.collection_output_dir / "forbidden"
    with pytest.raises(SystemExit):
        archive.main(cli(args))
    assert not args.output_dir.exists()
