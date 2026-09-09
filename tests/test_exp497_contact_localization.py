"""Prospective adaptive-ledger, common-phase and independent arithmetic tests."""
from copy import deepcopy
import json

import numpy as np
import pytest
from scripts import run_exp497_contact_localization as run
from scripts import audit_exp497_contact_localization as audit


@pytest.fixture(scope="module")
def inputs():
    return run.load()


def test_complete_parent_eligibility_and_strict_interpolation(inputs):
    p,s = inputs
    left,right = run.initial_endpoints(p["cases"][0],s)
    a = run.propose(left,right)
    assert left["a"] == .21545 and right["a"] == .21575
    assert left["a"] < a < right["a"]
    independent = (left["a"]*right["mean_residual"]-right["a"]*left["mean_residual"])/(right["mean_residual"]-left["mean_residual"])
    assert abs(a-independent) < 1e-15
    with pytest.raises(ValueError): run.initial_endpoints(p["cases"][1],s)
    assert len(s["data"]["ledger"]) == 26


@pytest.mark.parametrize("left,right", [(0,1),(1,2),(-1,-2),(float("nan"),1)])
def test_invalid_endpoint_signs_never_propose(left,right):
    with pytest.raises(ValueError): run.propose(dict(a=0.,mean_residual=left),dict(a=1.,mean_residual=right))


def test_new_curve_uses_common_interpolated_seed_and_shifted_section(inputs):
    p,s = inputs
    case = p["cases"][0]
    left,right = run.initial_endpoints(case,s)
    a = run.propose(left,right)
    candidates = run.candidates_at(case,1,a,left,right,s)
    assert len(candidates) == 4
    for c,old in zip(candidates,s["data"]["candidates"][:4],strict=True):
        assert c["parameters"] == dict(a=a,b=.2,c=7.212)
        assert c["initial_state"][::2] == old["initial_state"][::2]
        assert c["initial_tangent"] == old["initial_tangent"]
        assert c["initial_state"][1] == run.legacy_rossler_section(run.RosslerParameters(**c["parameters"])).offset
        assert c["u_box"] == [c["seed_u"]-.02,c["seed_u"]+.02]
        assert c["horizon"] == c["seed_time"]+3


def fake_result(spec,candidates,seed,s,status,mean=.001):
    cycle = deepcopy(run.parent.cycle_node(s["cycles"],spec["case"],False))
    cycle["spec"] = spec
    folds = []
    for c in candidates:
        f = deepcopy(next(f for f in s["old_folds"]["candidates"] if f["id"] == c["parent_id"]))
        f.update(id=c["id"],parent_id=c["parent_id"])
        folds.append(f)
    if status == "cycle-unqualified": cycle["status"] = "unqualified"
    return dict(cycle=cycle,folds=folds,contact=dict(status=status,mean_residual=mean))


@pytest.mark.parametrize("status", ["proximate","fold-unqualified","sign-unresolved","cycle-unqualified"])
def test_stops_and_retains_all_six_levels_without_rescue(inputs,status):
    p,s = inputs
    calls = []
    def evaluate(spec,candidates,seed):
        calls.append(spec)
        return fake_result(spec,candidates,seed,s,status)
    rows = run.campaign(p,s,evaluate)
    assert len(calls) == 1 and len(rows) == 6
    assert rows[0]["status"] == status
    assert all(r["status"] == "not-run" for r in rows[1:])
    assert all(r["reason"] == "parent endpoint representation matrix unqualified" for r in rows[3:])


def test_three_point_bound_keeps_original_phase_reference(inputs):
    p,s = inputs
    calls,seeds = [],[]
    def evaluate(spec,candidates,seed):
        calls.append(spec)
        seeds.append(deepcopy(seed))
        return fake_result(spec,candidates,seed,s,"replace-high",.001/len(calls))
    rows = run.campaign(p,s,evaluate)
    assert len(calls) == 3 and len(rows) == 6
    assert all(seed == seeds[0] for seed in seeds)
    assert seeds[0] == run.parent.cycle_node(s["cycles"],p["cases"][0],False)["profiles"][0]["correction"]
    assert all(calls[i]["parameters"]["a"] > calls[i+1]["parameters"]["a"] for i in range(2))
    assert all(r["status"] == "not-run" for r in rows[3:])


@pytest.mark.parametrize("offset,status", [(0.,"proximate"),(.03,"replace-low"),(-.03,"replace-high")])
def test_scalar_contact_replay_all_variants(inputs,offset,status):
    p,s = inputs
    cycle = deepcopy(run.parent.cycle_node(s["cycles"],p["cases"][0],False))
    folds = deepcopy([f for f in s["result"]["candidates"] if f["case"] == p["cases"][0]])
    for f in folds:
        for i,profile in enumerate(f["solvers"]):
            events = cycle["profiles"][i]["metric"]["windows"][0]["event_states"]["historical"]
            o = profile["observations"][1]
            o["image_state"],o["next_state"] = deepcopy(events[3]),deepcopy(events[4])
            o["image_state"][0] += offset
    a,b = run.measure(folds,cycle,p),audit.scalar_contact(folds,cycle)
    assert audit.periodic_audit.numeric_equal(a,b)
    assert a["status"] == status
    assert sum(len(r["variants"]) for r in a["rows"]) == 16
    folds[0]["qualified_in_region"] = False
    assert run.measure(folds,cycle,p)["status"] == "fold-unqualified"


def test_binding_tamper_rejected_before_targets(inputs,tmp_path,monkeypatch):
    p = deepcopy(inputs[0])
    path = tmp_path/"plan.json"
    p["levels"] = 4
    path.write_text(json.dumps(p))
    monkeypatch.setattr(run,"PLAN",path)
    with pytest.raises(ValueError,match="frozen"): run.load()


def test_wrong_raw_anchor_never_replays(tmp_path):
    (tmp_path/"summary.json").write_text("{}")
    with pytest.raises(ValueError,match="anchor"): audit.audit(tmp_path,"0"*64)


def test_actual_circle_controls_replay_dense_extremum_roots(tmp_path):
    controls = run.cycles_run.controls(tmp_path)
    assert controls["passed"]
    assert len(audit.check_periodic_controls(tmp_path)) == 5
