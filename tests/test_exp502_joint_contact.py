"""Outcome-free response, production wrapper, and frozen-startup tests."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest
from butterfly.poincare import PoincareSection
from scripts import run_exp502_joint_contact as run
from scripts import audit_exp502_joint_contact as audit


def test_synthetic_response_controls():
    result = audit.response_controls()
    assert result["passed"] and len(result["cases"]) == 6


def test_complete_anchored_plan():
    p = run.load()
    assert len(p["stencil"]) == 8 and len(p["base_vectors"]) == 256 and len(p["ledger"]) == 26
    assert len(p["fold_candidates"]) == 4 and len(p["boundary_candidates"]) == 8
    assert [c["accepted_prefix"] for c in p["boundary_candidates"]] == [4,1,4,1,5,8,5,8]
    for spec in p["stencil"]:
        folds,boundaries,field,section = run.point_inputs(p,spec)
        assert field["linear"][3][2] == spec["parameters"]["a"]
        assert all(c["initial_state"][1] == section["offset"] for c in folds+boundaries)
        for c,old in zip(folds+boundaries,p["fold_candidates"]+p["boundary_candidates"],strict=True):
            assert c["initial_state"][::2] == old["initial_state"][::2]
            assert c["seed_u"] == old["seed_u"] and c["seed_time"] == old["seed_time"]
    original = run.point_inputs(p,dict(parameters=p["anchor"]))
    assert original[2:] == (json.loads((run.ROOT/list(run.INPUTS)[2]).read_bytes())["field"],
                            json.loads((run.ROOT/list(run.INPUTS)[2]).read_bytes())["section"])


@pytest.mark.parametrize("kind",["seed","stencil","ledger","source","threshold"])
def test_plan_substitution_rejected(kind,tmp_path,monkeypatch):
    p = deepcopy(run.load())
    if kind == "seed":
        p["cycle_seed"]["period_time"] += .1
    elif kind == "stencil":
        p["stencil"].pop()
    elif kind == "ledger":
        p["ledger"].pop()
    elif kind == "threshold":
        p["primary_radius"] = .1
    else:
        p["source_paths"].remove("scripts/exp502_response.py")
    path = tmp_path/"plan.json"
    run.write_json(path,p)
    monkeypatch.setattr(run,"PLAN",path)
    with pytest.raises(ValueError):
        run.load()


def test_cyclic_transport_cannot_rotate_failed_primary():
    reference = run.load()["reference_cycle"]
    assert run.response.correspondence(reference,reference)["passed"]
    shifted = deepcopy(reference)
    for profile in shifted["profiles"]:
        for window in profile["metric"]["windows"]:
            events = window["event_states"]["historical"]
            window["event_states"]["historical"] = events[1:]+events[:1]
    assert not run.response.correspondence(shifted,reference)["passed"]


def test_complete_variant_order_and_nonfinite_rejection():
    anchor,base,points = audit.synthetic()
    with pytest.raises(ValueError):
        run.response.response(points[:7],base,anchor)
    points[-1]["vectors"].reverse()
    assert not run.response.response(points,base,anchor)["qualified"]
    anchor,base,points = audit.synthetic()
    points[-1]["vectors"][0]["value"][0] = float('nan')
    assert not run.response.response(points,base,anchor)["qualified"]


def test_residual_reduction_is_not_contact():
    anchor,base,points = audit.synthetic()
    matrix = run.response.response(points,base,anchor)
    proposal = dict(qualified=True,joint_proximity=False,
        vectors=[dict(r,value=[0.,0.]) for r in base])
    verdict = run.response.verdict(matrix,proposal,base)
    assert verdict["reduction_at_least_twenty_percent"] and not verdict["joint_proximity"]
    assert verdict["status"] == "qualified-proposal-without-joint-proximity"


def test_one_variant_orientation_failure_cannot_be_dropped():
    anchor,base,points = audit.synthetic()
    for point in points:
        point["vectors"][-1]["value"][0] *= -1
    assert not run.response.response(points,base,anchor)["qualified"]


def test_zero_step_and_ill_conditioning_rejected():
    for matrix,f0 in ((None,[0.,0.]),([[1.,0.],[0.,1e-8]],None)):
        anchor,base,points = audit.synthetic(matrix=matrix,f0=f0)
        assert not run.response.response(points,base,anchor)["qualified"]


def test_guard_wrapper_counts_before_calls_and_retains_mesh(tmp_path,monkeypatch):
    p = run.load()["fold"]
    candidate = deepcopy(run.load()["fold_candidates"][0])
    candidate["id"] = "synthetic-guard"
    state,tangent = np.array([1.,.3,0.]),np.array([.1,0.,0.])
    calls = []
    def synthetic_candidate(c,method,p,rhs,jac,hvv,section,retain):
        report,raw = run.section_census.collect(lambda t,q: np.array([-q[1],q[0],0.]),
            lambda t,q: np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,0.]]),state,tangent,
            PoincareSection((0.,1.,0.),0.,-1),method=method,horizon=1.,guard=p["guard"])
        retain("census-0",raw)
        return dict(method=method,censuses=[dict(report=report)])
    monkeypatch.setattr(run.previous.folds_run,"run_candidate",synthetic_candidate)
    original = run.section_census.solve_ivp
    def checked(*args,**kwargs):
        assert len(calls) == (1 if args[1][0] == 0. else 2)
        return original(*args,**kwargs)
    monkeypatch.setattr(run.section_census,"solve_ivp",checked)
    row = run.fold_profile(tmp_path,candidate,"DOP853",p,lambda flag:calls.append(flag))
    assert calls == [True,True]
    raw = audit.old.load_raw(tmp_path/"synthetic-guard--DOP853--guard-0.npz")
    main = audit.old.load_raw(tmp_path/"synthetic-guard--DOP853--census-0.npz")
    audit.check_guard(raw,main,row["censuses"][0]["report"],p["guard"])
    raw["augmented_states"][-1,0] += 1.
    with pytest.raises(ValueError):
        audit.check_guard(raw,main,row["censuses"][0]["report"],p["guard"])


def test_budget_stops_before_solve(tmp_path,monkeypatch):
    c = deepcopy(run.load()["fold_candidates"][0])
    def forbidden(*args,**kwargs):
        pytest.fail("integration after budget rejection")
    def stop(flag):
        raise run.previous.cycles_run.BudgetStop("test cap")
    monkeypatch.setattr(run.projected_fold_shooting,"solve_ivp",forbidden)
    with pytest.raises(run.previous.cycles_run.BudgetStop):
        run.fold_profile(tmp_path,c,"DOP853",run.load()["fold"],stop)


def test_copied_source_startup():
    result = run.startup(run.load())
    assert result["passed"] and result["isolated"] and result["target_integrations"] == 0
