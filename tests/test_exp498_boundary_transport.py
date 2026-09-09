"""Prospective transport, complete-ledger and independent scalar guards."""
from copy import deepcopy
import json

import numpy as np
import pytest
from scripts import run_exp498_boundary_transport as run
from scripts import audit_exp498_boundary_transport as audit


@pytest.fixture(scope="module")
def inputs():
    return run.load()


def test_all_eight_nominations_and_prior_failure_retained(inputs):
    p,anchor = inputs
    audit.check_inputs(p,anchor)
    assert len(p["ledger"]) == 26
    assert [r["status"] for r in p["ledger"]].count("selected") == 8
    assert [r["status"] for r in p["ledger"]].count("not-run-no-anchor") == 8
    assert [r["status"] for r in p["ledger"]].count("not-run-parent-unselected") == 10
    failed = [c for c in p["candidates"] if c["parent_qualified"] is False]
    assert len(failed) == 1
    assert failed[0]["parent_id"] == "local-a025-c083--region-0--depth-8--direction-0--candidate-1"
    assert len({c["family_id"] for c in p["candidates"]}) == 4
    assert {c["accepted_prefix"] for c in p["candidates"]} == {1,4,5,8}
    assert p["limits"]["target_ivps"] == 8*2*(8+4)


def test_exact_section_shift_and_common_seeds(inputs):
    p,anchor = inputs
    for c in p["candidates"]:
        assert c["parameters"] == dict(a=.21558015990653545,b=.2,c=7.212)
        assert c["u_box"] == [c["seed_u"]-.02,c["seed_u"]+.02]
        assert c["time_box"] == [c["seed_time"]-1,c["seed_time"]+1]
        assert c["initial_state"][1] == run.legacy_rossler_section(run.RosslerParameters(**c["parameters"])).offset
        assert c["time_box"][1] < c["horizon"]
        assert c["accepted_prefix"] > 0


@pytest.mark.parametrize("change",["radius","solver","missing","old-failure","dose","prefix"])
def test_plan_tampering_fails(inputs,tmp_path,monkeypatch,change):
    p,_ = inputs
    p = deepcopy(p)
    if change == "radius": p["ordering_gap"] *= 2
    elif change == "solver": p["boundary"]["side_solver_scaled_state"] *= 2
    elif change == "missing": p["candidates"].pop()
    elif change == "old-failure":
        next(c for c in p["candidates"] if c["parent_qualified"] is False)["parent_qualified"] = True
    elif change == "dose": p["candidates"][0]["doses"][0] *= 2
    else: p["candidates"][0]["accepted_prefix"] += 1
    path = tmp_path/"plan.json"
    run.write_json(path,p)
    monkeypatch.setattr(run,"PLAN",path)
    with pytest.raises(ValueError): run.load()


def synthetic_result():
    predecessor = dict(time=.2,state=[-3.,0.,.01],accepted=True)
    unaccepted = dict(time=.5,state=[200.,0.,40.],accepted=False)
    local = dict(time=.999,state=[0.,0.,9.],accepted=True)
    reports = [dict(method=m,reconstructed=[predecessor,unaccepted,local]) for m in ("DOP853","Radau")]
    return dict(roots=[dict(shooting=dict(trace=[dict(time=1.)])) for _ in range(2)],
        sides=[dict(dose=d,u=d,reports=deepcopy(reports)) for d in (-2e-6,-2e-7,2e-7,2e-6)])


def test_predecessor_is_not_the_grazing_or_next_return(inputs):
    p,anchor = inputs
    c = dict(accepted_prefix=1)
    result = synthetic_result()
    actual = run.predecessors(c,result,anchor,p)
    assert len(actual) == 8
    assert all(v["event"]["time"] == .2 and v["event"]["state"] == [-3.,0.,.01] for v in actual)
    assert all(len(w["state_distances"]) == 6 for v in actual for w in v["windows"])
    assert run.polygon_audit.same_numeric(actual,audit.scalar_predecessors(c,result,anchor,p))
    missing = run.predecessors(dict(accepted_prefix=2),result,anchor,p)
    assert all(not v["eligible"] and v["event"] is None and not v["windows"] for v in missing)


def synthetic_rows(anchor,p,offset):
    fold_x = anchor["result"]["contact"]["rows"][0]["variants"][0]["fold_input"][0]
    rows = []
    for i in range(8):
        result = synthetic_result()
        for side in result["sides"]:
            for report in side["reports"]:
                report["reconstructed"][0]["state"][0] = fold_x+offset
        pred = run.predecessors(dict(accepted_prefix=1),result,anchor,p)
        rows.append(dict(predecessors=pred,geometry=dict(analysis=dict(qualified=True))))
    return rows


@pytest.mark.parametrize("offset,ordering",[(-1.,"left"),(1.,"right"),(0.,"overlap-or-unresolved-gap")])
def test_complete_scalar_matrix_and_ordering(inputs,offset,ordering):
    p,anchor = inputs
    rows = synthetic_rows(anchor,p,offset)
    actual = run.diagnostic(rows,anchor,p)
    assert actual["ordering"] == ordering
    assert actual["predecessors"] == 64 and actual["comparison_cells"] == 768
    assert len(actual["worst_cycle_distances"]) == 6 and len(actual["sensitivity"]) == 4
    assert run.polygon_audit.same_numeric(actual,audit.scalar_diagnostic(rows,anchor,p))


@pytest.mark.parametrize("kind",["missing","failed","ineligible","empty"])
def test_no_subset_or_missing_arm_rescue(inputs,kind):
    p,anchor = inputs
    rows = synthetic_rows(anchor,p,-1.)
    if kind == "missing": rows.pop()
    elif kind == "failed": rows[0]["geometry"]["analysis"]["qualified"] = False
    elif kind == "ineligible": rows[0]["predecessors"][0]["eligible"] = False
    else: rows = []
    actual = run.diagnostic(rows,anchor,p)
    assert not actual["complete_qualified_matrix"] and actual["ordering"] == "unresolved"
    assert run.polygon_audit.same_numeric(actual,audit.scalar_diagnostic(rows,anchor,p))


def test_exact_winding_controls_and_ray_replay(inputs):
    p,_ = inputs
    controls = run.winding.controls(p["winding"])
    assert controls["passed"] and controls["new_integrations"] == 0 and controls["analytic_profiles"] == 12
    audit.check_polygons(dict(sides=controls["positive_sides"]),p["winding"])


def test_scalar_audits_do_not_call_integrators(inputs,monkeypatch):
    def forbidden(*args,**kwargs): pytest.fail("scalar replay integrated a trajectory")
    from butterfly import event_boundary_shooting,section_census,section_grazing
    for m in (event_boundary_shooting,section_census,section_grazing): monkeypatch.setattr(m,"solve_ivp",forbidden)
    p,anchor = inputs
    audit.check_inputs(p,anchor)
    result = synthetic_result()
    audit.scalar_predecessors(dict(accepted_prefix=1),result,anchor,p)
    audit.scalar_diagnostic(synthetic_rows(anchor,p,-1),anchor,p)
