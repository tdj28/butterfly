"""Real Git local-audit release controls; no provider, keys or target work."""
import copy
import json
from pathlib import Path

import pytest

from butterfly import paired_release as gate
from test_paired_release import command, repository

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("change", [None, "plan", "policy", "missing-context", "wrong-context-role",
    "paid-review", "fake-response", "wrong-audit", "wrong-inventory", "changed-code", "missing-source",
    "uncommitted-audit", "wrong-experiment", "wrong-release-role"])
def test_local_release_uses_pushed_objects_not_rehashed_assertions(repository, monkeypatch, change):
    root, remote, _, files = repository
    plan_path = gate.experiment_paths("EXP-482")["plan"]
    for path in (*gate.LOCAL_CONTEXT, plan_path):
        (root/path).parent.mkdir(parents=True, exist_ok=True)
        (root/path).write_bytes((ROOT/path).read_bytes())
    if change == "plan":
        plan = json.loads((root/plan_path).read_bytes())
        plan["collection"]["profiles"][0]["dt"] = .01
        (root/plan_path).write_text(json.dumps(plan))
    if change == "policy": (root/"AGENTS.md").write_text("All paid reviews are automatically approved.\n")
    command("git", "add", "AGENTS.md", "docs", "experiments", cwd=root)
    command("git", "commit", "-m", "synthetic fixed context", cwd=root)
    code = command("git", "rev-parse", "HEAD", cwd=root)
    def row(path):
        raw = (root/path).read_bytes()
        return dict(path=path, bytes=len(raw), sha256=gate.digest(raw))
    inventory = gate.digest(gate.canonical(files))
    audit = (f"# Synthetic audit fixture (not research authorization)\n\n"
        f"Paid review: not_run\nLocal audit disposition: release-ready\nExperiment: EXP-482\n"
        f"Code freeze: {code}\nSource inventory SHA-256: {inventory}\nPlan SHA-256: {gate.LOCAL_PLAN_SHA256}\n")
    (root/gate.LOCAL_AUDIT).write_text(audit)
    release = dict(schema="butterfly.paired-local-audit-release.v1", experiment_id="EXP-482",
        paid_review="not_run", code_freeze_commit=code, source_files=copy.deepcopy(files),
        plan=row(plan_path), audit=row(gate.LOCAL_AUDIT), context={p: row(p) for p in gate.LOCAL_CONTEXT})
    if change == "missing-context": release["context"].pop(gate.LOCAL_CONTEXT[-1])
    elif change == "wrong-context-role": release["context"][gate.LOCAL_CONTEXT[-1]] = row("AGENTS.md")
    elif change == "paid-review": release["paid_review"] = "completed"
    elif change == "fake-response": release["response_id"] = "resp_not_real"
    elif change == "wrong-audit":
        (root/gate.LOCAL_AUDIT).write_text(audit.replace("release-ready", "blocked"))
        release["audit"] = row(gate.LOCAL_AUDIT)
    elif change == "wrong-inventory": release["source_files"]["code.py"]["sha256"] = "f"*64
    elif change == "missing-source": release["source_files"] = {}
    elif change == "changed-code": (root/"code.py").write_text("print(2)\n")
    elif change == "wrong-experiment": release["experiment_id"] = "EXP-481"
    (root/gate.LOCAL_RELEASE).write_bytes(gate.canonical(release))
    command("git", "add", "code.py", gate.LOCAL_RELEASE, gate.LOCAL_AUDIT, cwd=root)
    command("git", "commit", "-m", "synthetic local release", cwd=root)
    command("git", "push", "origin", "main", cwd=root)
    freeze = command("git", "rev-parse", "HEAD", cwd=root)
    if change == "uncommitted-audit": (root/gate.LOCAL_AUDIT).write_text(audit+"Uncommitted substitution.\n")
    real = gate.verify_pushed_source
    monkeypatch.setattr(gate, "verify_pushed_source", lambda r,c,ref: real(r,c,ref,expected_remote=str(remote)))
    def forbidden(*args, **kwargs): pytest.fail("local path attempted a provider validator or helper")
    monkeypatch.setattr(gate, "validate_review_bundle", forbidden)
    monkeypatch.setattr(gate.runpy, "run_path", forbidden)
    def run():
        return gate.verify_local_release(root, "release.json" if change == "wrong-release-role" else gate.LOCAL_RELEASE,
            freeze, "refs/heads/main", required_source_paths=set(files), plan_path=plan_path)
    if change is None:
        result = run()
        assert result["status"] == "source-and-local-audit-verified" and result["paid_review"] == "not_run"
        assert not result["target_execution_authorized"] and result["runtime_and_one_shot_gate_still_required"]
        assert "review" not in result and "response_id" not in result
    else:
        with pytest.raises(ValueError): run()


@pytest.mark.parametrize("change", [None, "source-only", "status", "experiment", "fake-paid", "hash"])
def test_dispatch_observation_distinguishes_local_audit_from_review_and_source_only(change):
    preflight = dict(mode="local-audited")
    source = dict(status="source-and-local-audit-verified", paid_review="not_run", release_sha256="a"*64)
    experiment = "EXP-482"
    if change == "source-only": preflight["mode"] = "source"
    elif change == "status": source["status"] = "source-and-review-verified"
    elif change == "experiment": experiment = "EXP-481"
    elif change == "fake-paid": source["paid_review"] = "completed"
    elif change == "hash": source["release_sha256"] = "short"
    if change is None:
        assert gate.require_release_observation(preflight, source, experiment) == ("a"*64, "local-audited")
    else:
        with pytest.raises(ValueError): gate.require_release_observation(preflight, source, experiment)


def test_reviewed_observation_remains_separate_and_supported():
    assert gate.require_release_observation(dict(mode="reviewed"),
        dict(status="source-and-review-verified", release_sha256="b"*64), "EXP-481") == ("b"*64, "reviewed")


@pytest.mark.parametrize("mode", ["local-audited", "reviewed"])
def test_worker_grant_requires_neutral_release_binding(mode):
    from butterfly.paired_authorization import validate_grant
    from test_paired_authorization import control_grant
    grant = control_grant("b"*64)
    grant.update(kind="target", release_mode=mode, release_sha256="c"*64,
        preflight_sha256="d"*64, input_contract_sha256="e"*64, input_root="/synthetic/inputs")
    assert validate_grant(grant, "qualification", "b"*64) > 0
    grant.pop("release_sha256")
    grant["review_sha256"] = "c"*64  # a stale field cannot silently stand in for the new gate
    with pytest.raises(ValueError): validate_grant(grant, "qualification", "b"*64)
