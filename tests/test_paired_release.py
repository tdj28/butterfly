"""Independent Git anchors and synthetic provider-bundle tampering controls."""
import copy
import json
from pathlib import Path
import runpy
import shutil
import subprocess

import pytest

from butterfly import paired_release as gate


ROOT = Path(__file__).resolve().parents[1]


def review_text(verdict="READY TO FREEZE", blocking="None.", important="None."):
    return (f"# Verdict\n\nSynthetic advisory only.\n\n{verdict}\n\n# Blocking findings\n\n{blocking}\n\n"
        f"# Important non-blocking findings\n\n{important}\n\n# What should remain unchanged\n\nFixed sample.\n\n"
        "# Minimal revised design\n\nAs specified.\n\n# Freeze checklist\n\n- B09 is not a finding heading.\n")


def self_hash(value):
    value["self_sha256"] = gate.digest(gate.canonical({k: v for k, v in value.items() if k != "self_sha256"}))
    return value


@pytest.mark.parametrize("verdict", gate.VERDICTS)
def test_exact_verdict_and_structural_findings(verdict):
    text = review_text(verdict, "## B01 — A defect\n\nThe text mentions I99, not another finding.",
                       "## I01 — A limitation\n\nNo B02 is needed.")
    result, findings = gate.parse_review(text)
    assert result == verdict and findings == {"B01": "blocking", "I01": "important"}


def test_fenced_quotes_do_not_create_finding_ids():
    text = review_text(blocking="## B01 — Actual finding\n\n```text\n## B02 — Quoted example, not a finding\n```\nFix B01.")
    assert gate.parse_review(text)[1] == {"B01": "blocking"}


@pytest.mark.parametrize("change", ["bold", "substring", "duplicate", "absent", "after-verdict", "duplicate-section",
    "missing-section", "duplicate-id", "misplaced-id", "malformed-heading", "silent-none", "fenced", "reordered"])
def test_ambiguous_or_malformed_review_fails_closed(change):
    text = review_text()
    if change == "bold": text = text.replace("READY TO FREEZE", "**READY TO FREEZE**")
    elif change == "substring": text = text.replace("READY TO FREEZE", "This is NOT READY TO FREEZE.")
    elif change == "duplicate": text = text.replace("READY TO FREEZE", "NOT READY TO FREEZE\nREADY TO FREEZE")
    elif change == "absent": text = text.replace("READY TO FREEZE", "Ready, perhaps.")
    elif change == "after-verdict": text = text.replace("READY TO FREEZE", "READY TO FREEZE\nMore ambiguity.")
    elif change == "duplicate-section": text += "\n# Verdict\nREADY TO FREEZE\n"
    elif change == "missing-section": text = text.split("# Freeze checklist")[0]
    elif change == "duplicate-id": text = review_text(blocking="## B01 — First\n## B01 — Second")
    elif change == "misplaced-id": text = review_text(blocking="## I01 — Wrong section")
    elif change == "malformed-heading": text = review_text(blocking="## **B01** — Unsupported markup")
    elif change == "silent-none": text = review_text(blocking="Probably fine, except an unspecified problem.")
    elif change == "fenced": text += "\n```\n"
    else: text = text.replace("# Minimal revised design", "# TEMP").replace("# What should remain unchanged", "# Minimal revised design").replace("# TEMP", "# What should remain unchanged")
    with pytest.raises(ValueError):
        gate.parse_review(text)


def adjudication_fixture():
    text = review_text("READY AFTER SPECIFIED FIXES", "## B01 — Bound the source\nFix the code.")
    old = {"code.py": {"bytes": 1, "sha256": "a"*64}}
    new = {"code.py": {"bytes": 2, "sha256": "b"*64}}
    a = dict(approved_for_execution=True, verdict="READY AFTER SPECIFIED FIXES", review_sha256=gate.digest(text.encode()),
        reviewed_inventory_sha256=gate.digest(gate.canonical(old)), final_inventory_sha256=gate.digest(gate.canonical(new)),
        findings=[dict(id="B01", decision="accept", rationale="Source mismatch can change the experiment.",
            resolution="Add and test an exact source gate.", authorizes_change=True)],
        changes=[dict(path="code.py", before=old["code.py"], after=new["code.py"], findings=["B01"])])
    return text, self_hash(a), old, new


def test_every_finding_and_changed_path_is_accounted_for():
    text, a, old, new = adjudication_fixture()
    assert gate.adjudicate(text, a, old, new)["changed_paths"] == ["code.py"]
    text = review_text()
    a = self_hash(dict(approved_for_execution=True, verdict="READY TO FREEZE", review_sha256=gate.digest(text.encode()),
        reviewed_inventory_sha256=gate.digest(gate.canonical(old)), final_inventory_sha256=gate.digest(gate.canonical(old)),
        findings=[], changes=[]))
    assert gate.adjudicate(text, a, old, old)["changed_paths"] == []


@pytest.mark.parametrize("change", ["missing-finding", "duplicate-finding", "needs-human", "deferred-blocker", "no-rationale",
    "no-resolution", "unmapped-change", "unapproved-change", "wrong-before", "unknown-finding", "wrong-review", "wrong-inventory", "negative"])
def test_rehashed_false_adjudications_are_rejected(change):
    text, a, old, new = adjudication_fixture()
    if change == "missing-finding": a["findings"] = []
    elif change == "duplicate-finding": a["findings"].append(copy.deepcopy(a["findings"][0]))
    elif change == "needs-human": a["findings"][0]["decision"] = "needs_human"
    elif change == "deferred-blocker": a["findings"][0].update(decision="defer", claim_narrowing="Later.")
    elif change == "no-rationale": a["findings"][0]["rationale"] = ""
    elif change == "no-resolution": a["findings"][0]["resolution"] = ""
    elif change == "unmapped-change": a["changes"] = []
    elif change == "unapproved-change": a["findings"][0]["authorizes_change"] = False
    elif change == "wrong-before": a["changes"][0]["before"] = new["code.py"]
    elif change == "unknown-finding": a["changes"][0]["findings"] = ["B02"]
    elif change == "wrong-review": a["review_sha256"] = "f"*64
    elif change == "wrong-inventory": a["final_inventory_sha256"] = "f"*64
    else:
        text = text.replace("READY AFTER SPECIFIED FIXES", "NOT READY TO FREEZE")
        a.update(verdict="NOT READY TO FREEZE", review_sha256=gate.digest(text.encode()))
    self_hash(a)  # all local self-hashes remain mutually consistent
    with pytest.raises(ValueError):
        gate.adjudicate(text, a, old, new)


def command(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, stderr=subprocess.PIPE).decode().strip()


@pytest.fixture
def repository(tmp_path):
    root, remote = tmp_path/"checkout", tmp_path/"remote.git"
    command("git", "init", "--bare", str(remote))
    command("git", "init", "-b", "main", str(root))
    command("git", "config", "user.name", "Synthetic Test", cwd=root)
    command("git", "config", "user.email", "test@example.invalid", cwd=root)
    (root/"code.py").write_text("print(1)\n")
    command("git", "add", "code.py", cwd=root)
    command("git", "commit", "-m", "synthetic source", cwd=root)
    command("git", "remote", "add", "origin", str(remote), cwd=root)
    command("git", "push", "origin", "main", cwd=root)
    commit = command("git", "rev-parse", "HEAD", cwd=root)
    raw = (root/"code.py").read_bytes()
    files = {"code.py": {"bytes": len(raw), "sha256": gate.digest(raw)}}
    return root, remote, commit, files


def test_actual_git_objects_and_live_remote_are_independent_anchors(repository):
    root, remote, commit, files = repository
    assert gate.verify_pushed_source(root, commit, "refs/heads/main", expected_remote=str(remote))["live_remote_matches"]
    assert gate.verify_inventory(root, commit, files, required_paths=["code.py"]) == gate.digest(gate.canonical(files))
    with pytest.raises(ValueError, match="origin"):
        gate.verify_pushed_source(root, commit, "refs/heads/main")  # a local mirror is not the public repository
    (root/"code.py").write_text("print(2)\n")
    false = {"code.py": {"bytes": 9, "sha256": gate.digest((root/"code.py").read_bytes())}}
    with pytest.raises(ValueError, match="committed bytes"):
        gate.verify_inventory(root, commit, false, required_paths=["code.py"])
    with pytest.raises(ValueError, match="tracked checkout"):
        gate.verify_pushed_source(root, commit, "refs/heads/main", expected_remote=str(remote))


def test_unpushed_head_and_incomplete_closure_rejected(repository):
    root, remote, old, files = repository
    with pytest.raises(ValueError, match="closure"):
        gate.verify_inventory(root, old, files, required_paths=["code.py", "missing.py"])
    (root/"code.py").write_text("print(3)\n")
    command("git", "add", "code.py", cwd=root)
    command("git", "commit", "-m", "not pushed", cwd=root)
    commit = command("git", "rev-parse", "HEAD", cwd=root)
    with pytest.raises(ValueError, match="live remote"):
        gate.verify_pushed_source(root, commit, "refs/heads/main", expected_remote=str(remote))


@pytest.mark.parametrize("path", ["../file", "./file", "/file", "a//b", "", ".", "a\nb", "a\tb", "a\\b"])
def test_noncanonical_release_paths_fail(path):
    with pytest.raises(ValueError):
        gate.relative_path(path)


def completed_bundle(root, monkeypatch, *, context_text=None, prepare_packet=None):
    (root/"tools").mkdir(parents=True)
    shutil.copyfile(ROOT/gate.CANONICAL_REVIEW_HELPER, root/gate.CANONICAL_REVIEW_HELPER)
    helper = runpy.run_path(str(root/gate.CANONICAL_REVIEW_HELPER))
    namespace = helper["main"].__globals__
    (root/"BRIEF.md").write_text("# Synthetic director brief\n\nFixed samples; no target observations.\n")
    (root/"CONTEXT.md").write_text(context_text or "# Synthetic context\n\nNo provider call or real research approval.\n")
    packet_commit = "a"*40 if prepare_packet is None else prepare_packet()
    monkeypatch.setitem(namespace, "load_api_key", lambda *_: "synthetic-placeholder")
    monkeypatch.setitem(namespace, "count_input_tokens", lambda **_: 100)
    def respond(*, payload, **_):
        return dict(id="resp_synthetic_fixture", status="completed", model=payload["model"], metadata=payload["metadata"],
            output=[dict(type="message", content=[dict(type="output_text", text=review_text())])],
            usage=dict(input_tokens=100, output_tokens=20, total_tokens=120, input_tokens_details=dict(cache_write_tokens=0)))
    monkeypatch.setitem(namespace, "call_responses_api", respond)
    def forbidden(*a, **k):
        pytest.fail("offline fixture attempted actual network access")
    monkeypatch.setattr(namespace["urllib"].request, "urlopen", forbidden)
    assert helper["main"](["--plan", str(root/"BRIEF.md"), "--context", str(root/"CONTEXT.md"),
        "--output-dir", str(root/"review"), "--input-rate-usd-per-million", "5", "--cache-write-rate-usd-per-million", "6.25",
        "--output-rate-usd-per-million", "30", "--reviewed-packet-git-head-commit", packet_commit, "--execute"]) == 0
    def row(name):
        raw = (root/name).read_bytes()
        return dict(path=name, bytes=len(raw), sha256=gate.digest(raw))
    manifest = json.loads((root/"review/review_manifest.json").read_bytes())
    return dict(reviewed_packet_commit=packet_commit, model=manifest["model"], response_id="resp_synthetic_fixture",
        review_input_sha256=manifest["review_input_sha256"], artifacts=dict(brief=row("BRIEF.md"), contexts=[row("CONTEXT.md")],
            bundle={k: row("review/"+v) for k, v in dict(manifest="review_manifest.json", request_payload="request_payload.json",
                request="review_request.md", response="response.json", review="review.md").items()}))


def test_canonical_bundle_validator_is_offline_and_does_not_authorize_targets(tmp_path, monkeypatch):
    declaration = completed_bundle(tmp_path, monkeypatch)
    result = gate.validate_review_bundle(tmp_path, declaration)
    assert result["status"] == "completed_review_bundle_valid" and result["verdict"] == "READY TO FREEZE"
    assert not result["target_execution_authorized"] and result["finding_ids"] == []


@pytest.mark.parametrize("change", ["context", "response-metadata", "review-text", "model", "packet-commit", "input-hash", "helper", "missing-role"])
def test_coherently_rehashed_review_artifact_cannot_replace_provider_packet(tmp_path, monkeypatch, change):
    declaration = completed_bundle(tmp_path, monkeypatch)
    roles = declaration["artifacts"]
    if change == "model": declaration["model"] = "different-model"
    elif change == "packet-commit": declaration["reviewed_packet_commit"] = "b"*40
    elif change == "input-hash": declaration["review_input_sha256"] = "b"*64
    elif change == "helper": (tmp_path/gate.CANONICAL_REVIEW_HELPER).write_text("raise AssertionError('must not load')\n")
    elif change == "missing-role": roles["bundle"].pop("response")
    else:
        row = roles["contexts"][0] if change == "context" else roles["bundle"]["response" if change == "response-metadata" else "review"]
        path = tmp_path/row["path"]
        if change == "context": path.write_text("# CONTEXT\nSubstituted scientific choices.\n")
        elif change == "review-text": path.write_text(review_text("NOT READY TO FREEZE"))
        else:
            data = json.loads(path.read_bytes())
            data["metadata"]["review_input_sha256"] = "b"*64
            path.write_text(json.dumps(data, sort_keys=True, indent=2)+"\n")
        # Rehash the substituted role; the independently reconstructed request
        # and provider-echoed metadata must still reject the false relation.
        row.update(bytes=path.stat().st_size, sha256=gate.digest(path.read_bytes()))
    with pytest.raises(ValueError):
        gate.validate_review_bundle(tmp_path, declaration)


@pytest.mark.parametrize("experiment_id", ["EXP-481", "EXP-482"])
@pytest.mark.parametrize("change", [None, "wrong-plan-context", "unmapped-code", "false-reviewed-inventory", "different-packet-commit", "wrong-experiment"])
def test_complete_source_and_review_consumer_with_real_git_and_mock_provider(repository, monkeypatch, change, experiment_id):
    root, remote, _, code_files = repository
    helper_raw = (ROOT/gate.CANONICAL_REVIEW_HELPER).read_bytes()
    source_files = {**code_files, gate.CANONICAL_REVIEW_HELPER: dict(bytes=len(helper_raw), sha256=gate.digest(helper_raw))}
    plan_raw = (json.dumps(dict(kind="synthetic design",seed_count=16,experiment_id=experiment_id))+"\n").encode()
    (root/"plan.json").write_bytes(plan_raw)
    before = {**source_files, "plan.json": dict(bytes=len(plan_raw), sha256=gate.digest(plan_raw))}
    context = gate.decision_context(json.loads(plan_raw), gate.digest(gate.canonical(before)))
    if change == "wrong-plan-context": context = context.replace('"seed_count": 16', '"seed_count": 32')
    def prepare():
        command("git", "add", "BRIEF.md", "CONTEXT.md", "plan.json", gate.CANONICAL_REVIEW_HELPER, cwd=root)
        command("git", "commit", "-m", "synthetic reviewed packet", cwd=root)
        return command("git", "rev-parse", "HEAD", cwd=root)
    review = completed_bundle(root, monkeypatch, context_text=context, prepare_packet=prepare)
    after = copy.deepcopy(before)
    if change == "unmapped-code":
        (root/"code.py").write_text("print(2)\n")
        after["code.py"] = dict(bytes=9, sha256=gate.digest((root/"code.py").read_bytes()))
        source_files["code.py"] = after["code.py"]
        command("git", "add", "code.py", cwd=root)
        command("git", "commit", "-m", "synthetic unadjudicated code change", cwd=root)
    code_commit = command("git", "rev-parse", "HEAD", cwd=root)
    a = self_hash(dict(approved_for_execution=True, verdict="READY TO FREEZE", review_sha256=gate.digest(review_text().encode()),
        reviewed_inventory_sha256=gate.digest(gate.canonical(before)), final_inventory_sha256=gate.digest(gate.canonical(after)),
        findings=[], changes=[]))
    (root/"adjudication.json").write_bytes(gate.canonical(a))
    release = dict(schema="butterfly.paired-reviewed-release.v1", experiment_id=experiment_id, approved_for_execution=True,
        code_freeze_commit=code_commit, source_files=source_files, plan=dict(path="plan.json", **after["plan.json"]),
        review=review, adjudication=dict(path="adjudication.json", sha256=gate.digest(gate.canonical(a))),
        reviewed_inventory=before, final_inventory=after)
    if change == "false-reviewed-inventory":
        release["reviewed_inventory"]["code.py"]["sha256"] = "f"*64
        a["reviewed_inventory_sha256"] = gate.digest(gate.canonical(release["reviewed_inventory"]))
        (root/"adjudication.json").write_bytes(gate.canonical(self_hash(a)))
        release["adjudication"]["sha256"] = gate.digest(gate.canonical(a))
    elif change == "different-packet-commit": release["review"]["reviewed_packet_commit"] = code_commit+"0"
    elif change == "wrong-experiment": release["experiment_id"] = "EXP-482" if experiment_id == "EXP-481" else "EXP-481"
    (root/"release.json").write_bytes(gate.canonical(release))
    command("git", "add", "release.json", "adjudication.json", "review/review_manifest.json", "review/request_payload.json",
        "review/review_request.md", "review/response.json", "review/review.md", cwd=root)
    command("git", "commit", "-m", "synthetic release", cwd=root)
    command("git", "push", "origin", "main", cwd=root)
    freeze = command("git", "rev-parse", "HEAD", cwd=root)
    # Only the origin location is substituted. The actual Git object, HEAD,
    # tracked-clean and live remote checks run against a real private test repo.
    real = gate.verify_pushed_source
    monkeypatch.setattr(gate, "verify_pushed_source", lambda r, c, ref: real(r, c, ref, expected_remote=str(remote)))
    def run():
        return gate.verify_reviewed_release(root, "release.json", freeze, "refs/heads/main",
            required_source_paths=set(source_files), plan_path="plan.json", experiment_id=experiment_id)
    if change is None:
        result = run()
        assert result["status"] == "source-and-review-verified" and not result["target_execution_authorized"]
        assert result["runtime_and_one_shot_gate_still_required"]
    else:
        with pytest.raises(ValueError):
            run()
