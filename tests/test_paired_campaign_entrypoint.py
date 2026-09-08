"""Production setup controls; no nominated-seed trajectories or paid reviews."""
import copy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

import pytest

from butterfly.paired_input_package import build_package
from butterfly.paired_inputs import load_references
from butterfly.paired_phases import from_reference_audit, phase_limits
from scripts.build_paired_runtime import build, ROOT
from scripts.run_paired_campaign import PLAN, STAGES, require_preflight


def numeric_plan(experiment_id="EXP-481"):
    from butterfly.paired_release import experiment_paths
    return json.loads((ROOT/experiment_paths(experiment_id)["plan"]).read_bytes())


def test_numeric_design_has_no_scientific_changes_or_approval_placeholder():
    original = json.loads((ROOT/"experiments/manifests/EXP-481-paired-sampling-proposal.json").read_bytes())
    for key in ("status", "execution_authorized", "review", "review_paths", "not_yet_implemented", "claim_scope"):
        original.pop(key)
    original["schema"] = "butterfly.paired-design.v1"
    assert numeric_plan() == original


@pytest.fixture(scope="module", params=["EXP-481", "EXP-482"])
def setup(tmp_path_factory, request):
    root = tmp_path_factory.mktemp("preflight-control")
    helpers = runpy.run_path(str(ROOT/"tests/test_paired_input_package.py"))
    inputs = helpers["synthetic_inputs"](root/"source")
    plan = numeric_plan(request.param)
    plan["inputs"] = inputs["inputs"]
    (root/"source/proposal.json").write_text(json.dumps(plan))
    packaged = build_package(root/"source/proposal.json", root/"source", root/"inputs")
    runtime = build(root/"runtime")
    contract = json.loads((root/"runtime/runtime-contract.json").read_bytes())
    audit = load_references(plan, root/"inputs")
    design, _ = from_reference_audit(plan, audit, source_commit="a"*40, plan_sha256=packaged["plan_sha256"])
    return root, plan, packaged, runtime, contract, audit, design


@pytest.mark.parametrize("kind", ["correct", "wrong-plan", "bad-source", "missing-source", "invalid-last-config"])
def test_real_worker_full_design_entrypoint_before_any_integration(setup, tmp_path, kind):
    root, plan, packaged, runtime, contract, audit, design = setup
    inputs, input_hash, plan_hash = root/"inputs", packaged["sha256"], packaged["plan_sha256"]
    if kind == "invalid-last-config":
        import shutil
        source = tmp_path/"source"
        shutil.copytree(root/"source", source)
        bad = copy.deepcopy(plan)
        bad["adaptive_qualification"]["profiles"][-1]["max_step"] = -1
        (source/"proposal.json").write_text(json.dumps(bad))
        inputs = tmp_path/"inputs"
        pkg = build_package(source/"proposal.json", source, inputs)
        input_hash, plan_hash = pkg["sha256"], pkg["plan_sha256"]
    output = tmp_path/"output"
    output.mkdir()
    command = [sys.executable, "-I", "-S", "-B", "-X", "utf8", str(root/"runtime/worker.py"),
        "--contract-sha256", runtime["sha256"], "--output-dir", str(output), "--mode", "design-preflight",
        "--input-root", str(inputs), "--input-contract-sha256", input_hash,
        "--plan-sha256", "0"*64 if kind == "wrong-plan" else plan_hash]
    if kind != "missing-source":
        command += ["--source-commit", "short" if kind == "bad-source" else "a"*40]
    with (tmp_path/"stdout").open("wb") as stdout, (tmp_path/"stderr").open("wb") as stderr:
        process = subprocess.Popen(command, cwd=tmp_path, env=contract["environment"], stdin=subprocess.PIPE,
            stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=30)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stdin.close()
    assert not (output/"phase").exists()
    witness_path = output/"design-preflight.json"
    if kind != "correct":
        assert code != 0 and not witness_path.exists()
        expected = {"wrong-plan": "external design hash", "bad-source": "full source/plan bindings",
            "missing-source": "requires external source and plan bindings", "invalid-last-config": "invalid bounded adaptive design"}[kind]
        assert expected in (tmp_path/"stderr").read_text()
        return
    assert code == 0, (tmp_path/"stderr").read_text()
    witness = json.loads(witness_path.read_bytes())
    assert witness["audit"] == audit
    require_preflight(witness, source_commit="a"*40, plan_sha256=plan_hash,
        runtime_sha256=runtime["sha256"], input_sha256=input_hash, design=design)
    assert witness["design"]["trial_counts"] == dict(qualification=128,
        collection=512 if plan["experiment_id"] == "EXP-481" else 64)
    assert [witness["design"]["phase_limits"][s]["wall_seconds"] for s in STAGES] == [1800, 14400, 7200]


@pytest.mark.parametrize("kind", ["correct", "design", "count", "budget", "authority", "source", "plan", "runtime", "inputs", "target", "imports"])
def test_preflight_consumer_uses_independent_expected_design(setup, kind):
    _, plan, packaged, runtime, _, _, design = setup
    plan_sha = packaged["plan_sha256"]
    witness = dict(status="passed", runtime_contract_sha256=runtime["sha256"],
        input_contract_sha256=packaged["sha256"], loaded_modules={"butterfly.paired_phases": {}},
        target_execution_authorized=False, target_trajectories_generated=0,
        design=dict(source_commit="a"*40, plan_sha256=plan_sha, design_sha256=design.identity(),
            trial_counts=dict(qualification=128, collection=512 if plan["experiment_id"] == "EXP-481" else 64),
            phase_limits={s: asdict(phase_limits(design.plan, s)) for s in STAGES}, guard_seconds=120.,
            scope="all fixed configurations validated without calling a field, integrator or map fit"))
    if kind == "design": witness["design"]["design_sha256"] = "0"*64
    elif kind == "count": witness["design"]["trial_counts"]["collection"] = 511
    elif kind == "budget": witness["design"]["phase_limits"]["collection"]["wall_seconds"] = 60.
    elif kind == "authority": witness["target_execution_authorized"] = True
    elif kind == "source": witness["design"]["source_commit"] = "b"*40
    elif kind == "plan": witness["design"]["plan_sha256"] = "0"*64
    elif kind in ("runtime", "inputs"): witness[("input" if kind == "inputs" else kind)+"_contract_sha256"] = "0"*64
    elif kind == "target": witness["target_trajectories_generated"] = 1
    elif kind == "imports": witness["loaded_modules"] = {}
    # These are mutually consistent saved bytes; a local self-hash isn't the
    # reason rejection occurs. The independent inputs/design disagree.
    encoded = json.dumps(witness, sort_keys=True).encode()
    assert len(hashlib.sha256(encoded).hexdigest()) == 64
    kwargs = dict(source_commit="a"*40, plan_sha256=plan_sha, runtime_sha256=runtime["sha256"],
        input_sha256=packaged["sha256"], design=design)
    if kind == "correct": require_preflight(json.loads(encoded), **kwargs)
    else:
        with pytest.raises(ValueError, match="independently"):
            require_preflight(json.loads(encoded), **kwargs)


def test_setup_refusal_is_preserved_and_never_consumes_slot(tmp_path, monkeypatch):
    from scripts import run_paired_campaign as controller
    def refuse(*args):
        raise ValueError("synthetic live source refusal")
    monkeypatch.setattr(controller, "bind_setup", refuse)
    with pytest.raises(ValueError, match="source refusal"):
        controller.preflight(tmp_path/"attempt", "a"*40, "refs/heads/synthetic")
    failure = json.loads((tmp_path/"attempt/failure.json").read_bytes())
    assert failure["target_slot_consumed"] is False and failure["target_trajectories_generated"] == 0
    assert not (tmp_path/"attempt/receipt.json").exists()
    with pytest.raises(FileExistsError):
        controller.preflight(tmp_path/"attempt", "a"*40, "refs/heads/synthetic")


def test_host_setup_is_not_a_forged_sealed_worker_receipt(tmp_path):
    command = [sys.executable, "-I", "-B", "-c",
        "import runpy,sys; api=runpy.run_path(sys.argv[1]); "
        "api['select_host_runtime'](sys.argv[2]); "
        "assert sys.path[0] == sys.argv[2]+'/python'; "
        "assert not any(type(f).__name__ == 'BoundImports' for f in sys.meta_path)",
        str(ROOT/"scripts/run_paired_campaign.py"), str(tmp_path)]
    subprocess.run(command, check=True, capture_output=True, timeout=10)


def test_host_setup_refuses_already_imported_numerics(tmp_path):
    from scripts.run_paired_campaign import select_host_runtime
    with pytest.raises(ValueError, match="preceded source/runtime"):
        select_host_runtime(tmp_path)


def test_preimport_guard_preserves_parent_pipe_across_stdin_redirection():
    # pytest's FD capture replaces fd0 with /dev/null after the guard starts.
    # That must not be mistaken for parent death; the original pipe stays live.
    program = ("import os,runpy,sys,time; "
        "guard=runpy.run_path(sys.argv[1])['install_parent_guard'](5.); "
        "fd=os.open(os.devnull,os.O_RDONLY); os.dup2(fd,0); os.close(fd); "
        "time.sleep(.3); assert guard.is_alive(); print('original-pipe-live',flush=True)")
    process = subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", program,
        str(ROOT/"python/butterfly/_process_guard.py")], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        assert process.wait(timeout=10) == 0, process.stderr.read().decode()
        assert process.stdout.read() == b"original-pipe-live\n"
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
