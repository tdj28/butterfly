"""Public replay and tamper rejection; never substitutes for the raw audit."""
from copy import deepcopy
import json
import math
import subprocess
import sys

import pytest
from scripts import verify_exp503_public_contact as public

PATH = public.run.ROOT/"docs/experiments/receipts/EXP-503-joint-contact-result.json"
SHA = "56cf4e0d13d2f082c3272494f0ef6a4719dfd92d7d9686a74c67026c995437a7"


def test_scalar_replay_tolerance_keeps_types_and_gates_exact():
    assert public.numeric_equal(dict(value=1.,passed=True),dict(value=math.nextafter(1.,2.),passed=True))
    assert not public.numeric_equal(dict(value=1.,passed=True),dict(value=1.,passed=False))
    assert not public.numeric_equal(dict(value=1.,passed=True),dict(value=1.,passed=1))
    assert not public.numeric_equal(dict(value=1.,passed=True),dict(value=1.001,passed=True))


def test_complete_public_result_without_private_archive(monkeypatch):
    def forbidden(*args,**kwargs):
        raise AssertionError("compact replay must not load private trajectories")
    monkeypatch.setattr(public.continuation,"load",forbidden)
    assert public.sha256(PATH) == SHA
    saved = json.loads(PATH.read_bytes())
    assert saved["source_commit"] == "ea11c80a49c85b1671fdaf3d6f536000c53bcb45"
    assert saved["completed_matrix_ivps"] == 1580 and saved["new_target_ivps"] == 363
    result = public.verify(PATH,SHA)
    assert result["passed"] and result["stencil_points"] == 8
    assert result["new_integrations"] == 0
    assert not result["full_raw_audit_repeated"] and not result["symbolic_chains_verified"]
    assert result["analysis"]["status"] == "qualified-proposal-without-joint-proximity"
    assert not result["analysis"]["joint_proximity"]
    assert result["analysis"]["residual_reduction"] == pytest.approx(.056397926934719234)


@pytest.mark.parametrize("kind",["missing-point","changed-point","wrong-provenance","changed-response",
    "claimed-chain","claimed-contact","reset-attempt","wrong-total","wrong-new-count","lost-failure"])
def test_compact_tampering_rejected_even_with_rehashed_envelope(tmp_path,kind):
    result = deepcopy(json.loads(PATH.read_bytes()))
    if kind == "missing-point":
        result["rows"].pop()
    elif kind == "changed-point":
        result["rows"][0]["vectors"][0]["value"][0] += .1
    elif kind == "wrong-provenance":
        result["point_counts"][0]["provenance"] = "continuation"
    elif kind == "changed-response":
        result["response"]["qualified"] = not result["response"]["qualified"]
    elif kind == "claimed-chain":
        result["symbolic_chains_verified"] = True
    elif kind == "claimed-contact":
        result["analysis"]["joint_proximity"] = not result["analysis"]["joint_proximity"]
    elif kind == "reset-attempt":
        result["original_attempt_reset"] = True
    elif kind == "wrong-total":
        result["completed_matrix_ivps"] += 1
    elif kind == "wrong-new-count":
        result["new_target_ivps"] += 1
    else:
        result["original_failure_sha256"] = "0"*64
    target = tmp_path/"mutated.json"
    public.run.write_json(target,result)
    with pytest.raises(ValueError):
        public.verify(target,public.sha256(target))


@pytest.mark.parametrize("kind",["one-ulp","material-drift","changed-gate"])
def test_reconstructed_arithmetic_tolerance_never_relaxes_gates(monkeypatch,kind):
    original = public.run.response.response
    def perturbed(*args,**kwargs):
        matrix = deepcopy(original(*args,**kwargs))
        assert matrix["qualified"]
        if kind == "one-ulp":
            value = matrix["mean_jacobian"][0][0]
            matrix["mean_jacobian"][0][0] = math.nextafter(value,math.inf)
        elif kind == "material-drift":
            matrix["mean_jacobian"][0][0] += .001
        else:
            matrix["matrices"][0]["qualified"] = False
        return matrix
    monkeypatch.setattr(public.run.response,"response",perturbed)
    if kind == "one-ulp":
        assert public.verify(PATH,public.sha256(PATH))["passed"]
    else:
        with pytest.raises(ValueError,match="response reconstruction"):
            public.verify(PATH,public.sha256(PATH))


def test_hash_refusal_precedes_plan_or_data_access(tmp_path,monkeypatch):
    path = tmp_path/"untrusted.json"
    public.run.write_json(path,{})
    monkeypatch.setattr(public.continuation,"PLAN",tmp_path/"missing-plan.json")
    with pytest.raises(ValueError,match="receipt hash"):
        public.verify(path,"0"*64)


def test_public_cli_documents_limited_scope():
    result = subprocess.run([sys.executable,"-m","scripts.verify_exp503_public_contact","--help"],
        capture_output=True,text=True,check=True)
    assert "not the full raw-data audit" in result.stdout
    assert "--expected-sha256" in result.stdout
