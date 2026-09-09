"""Complete prospective grid and real failure-path dispatch controls."""
from copy import deepcopy
from dataclasses import asdict
import json

import numpy as np
import pytest

from scripts import run_exp494_periodic_winding_transport as r


def fake_profile(method):
    correction = dict(initial_state=[1., 2., .01], period_time=10., success=True, optimizer_success=True,
                      closure_error=1e-12, phase_residual=1e-12)
    window = dict(counts=dict(historical=1, barrio=1),
        event_states=dict(historical=[[1., 2., .01]], barrio=[[2., 3., .02]]),
        event_phases=dict(historical=[.2], barrio=[.4]))
    return dict(method=method, qualified=True, correction=correction, metric=dict(windows=[window, deepcopy(window)]))


def parents(p):
    return dict(profiles=[dict(candidate_id=c, profile=dict(name="dop853-refined"),
                              correction=fake_profile("DOP853")["correction"]) for c in p["cases"]])


def test_complete_grid_has_both_axes_signs_cases_and_endpoints():
    p = r.load_plan()
    rows = r.grid(p)
    assert len(rows) == len({x["id"] for x in rows}) == 66
    assert sum(x["step"] > 0 for x in rows) == 64
    for case in p["cases"]:
        for arm in ("a-", "a+", "c-", "c+"):
            selected = [x for x in rows if x["case"] == case and x["arm"] == arm]
            assert [x["step"] for x in selected] == list(range(1, 9))


@pytest.mark.parametrize("key", ["steps", "rtol", "maximum_scaled_step", "maximum_seconds", "parent_receipt_sha256"])
def test_mutated_plan_fails_independent_constants(tmp_path, monkeypatch, key):
    p = r.load_plan()
    p[key] = "0"*64 if isinstance(p[key], str) else p[key]*2
    path = tmp_path/"plan.json"
    path.write_text(json.dumps(p))
    monkeypatch.setattr(r, "PLAN", path)
    with pytest.raises(ValueError):
        r.load_plan()


def test_complete_dispatch_both_methods_same_seed():
    p = r.load_plan()
    calls = []
    def execute(spec, method, seed):
        calls.append((spec["id"], method, seed))
        return fake_profile(method)
    rows = r.campaign(p, parents(p), execute)
    assert len(calls) == 132 and all(x["status"] == "qualified" for x in rows)
    assert all(calls[i][2] == calls[i+1][2] for i in range(0, 132, 2))


def test_failed_arm_retains_failure_and_unrun_rows_others_continue():
    p = r.load_plan()
    target = r.grid(p)[2]["id"]
    calls = []
    def execute(spec, method, seed):
        calls.append(spec["id"])
        return dict(fake_profile(method), qualified=not (spec["id"] == target and method == "Radau"))
    rows = r.campaign(p, parents(p), execute)
    assert rows[2]["status"] == "unqualified" and len(rows[2]["profiles"]) == 2
    assert all(x["status"] == "not-run" for x in rows[3:9])
    assert all(x["status"] == "qualified" for x in rows[9:])
    assert len(calls) == 120


def test_failed_base_does_not_block_other_case():
    p = r.load_plan()
    rows = r.campaign(p, parents(p), lambda spec,m,s:dict(fake_profile(m), qualified=spec["case"] != p["cases"][0]))
    assert rows[0]["status"] == "unqualified"
    assert all(x["status"] == "not-run" for x in rows[1:33])
    assert all(x["status"] == "qualified" for x in rows[33:])


def test_budget_interruption_retains_complete_grid():
    p = r.load_plan()
    def execute(spec, method, seed):
        raise r.BudgetStop("test deadline")
    rows = r.campaign(p, parents(p), execute)
    assert len(rows) == 66 and rows[0]["status"] == "interrupted"
    assert all(x["status"] == "not-run" and x["reason"] == "test deadline" for x in rows[1:])


@pytest.mark.parametrize("change", ["missing", "duplicate", "state", "period", "qualification"])
def test_pair_failure_matrix(change):
    p = r.load_plan()
    rows = [fake_profile(m) for m in p["methods"]]
    if change == "missing":
        rows.pop()
    elif change == "duplicate":
        rows[1]["method"] = "DOP853"
    elif change == "state":
        rows[1]["correction"]["initial_state"][2] += .001
    elif change == "period":
        rows[1]["correction"]["period_time"] += .01
    else:
        rows[1]["qualified"] = False
    if change in ("missing", "duplicate"):
        with pytest.raises(ValueError):
            r.compare_profiles(rows, p)
    else:
        assert not r.compare_profiles(rows, p)["passed"]


@pytest.mark.parametrize("key", ["optimizer_success", "success", "closure_error", "phase_residual", "initial_state", "period_time"])
def test_corrector_gate_enforced(key):
    p = r.load_plan()
    seed = fake_profile("DOP853")["correction"]
    c = deepcopy(seed)
    c[key] = False if key in ("success", "optimizer_success") else ([1., 2., 1.] if key == "initial_state" else 1.)
    assert not r.correction_gate(c, seed, p)["passed"]


def test_actual_failed_corrector_mesh_is_retained(tmp_path, monkeypatch):
    p = r.load_plan()
    seed = fake_profile("DOP853")["correction"]
    def correction(par, initial, period, **kwargs):
        r.periodic.solve_ivp(lambda t,q:np.zeros_like(q), (0., .01), np.r_[initial, np.eye(3).ravel()])
        return r.periodic.PeriodicOrbitCorrection(np.array(initial), period, np.array(initial),
                                                 1., 0., 0., 1, False, False, "intentional failure")
    monkeypatch.setattr(r.periodic, "correct_periodic_orbit", correction)
    calls = []
    row = r.run_profile(r.grid(p)[0], "DOP853", seed, p, tmp_path, calls.append)
    assert not row["qualified"] and len(row["raw_files"]) == 1
    assert (tmp_path/row["raw_files"][0]).is_file()
    assert True in calls and "observation" not in row


@pytest.mark.parametrize("method", ["DOP853", "Radau"])
def test_coefficient_audit_replays_known_circles_and_rejects_changed_membership(monkeypatch, method):
    from scripts import audit_exp494_periodic_winding_transport as audit
    from test_periodic_winding import circle
    raw, report, metric, _, field = circle(method)
    monkeypatch.setattr(r, "rossler_rhs", lambda t,q,p:field(t,q))
    monkeypatch.setattr(r, "rossler_equilibria", lambda p:np.zeros((1,3)))
    monkeypatch.setattr(r, "legacy_rossler_section", lambda p:r.PoincareSection((0.,1.,0.),0.,-1,0,0.))
    monkeypatch.setattr(r, "barrio_rossler_section", lambda p:r.PoincareSection((1.,0.,0.),0.,1))
    result = audit.audit_observation(raw, report, None, method, 2*np.pi)
    assert audit.numeric_equal(result, metric)
    report["events"]["historical"][0]["accepted"] = not report["events"]["historical"][0]["accepted"]
    with pytest.raises(ValueError, match="membership"):
        audit.audit_observation(raw, report, None, method, 2*np.pi)


def test_portable_comparison_does_not_waive_boolean_or_integer_decisions():
    from scripts.audit_exp494_periodic_winding_transport import numeric_equal
    assert numeric_equal(dict(value=1., passed=True, count=6),dict(value=np.nextafter(1.,2.),passed=True,count=6))
    assert not numeric_equal(dict(passed=True),dict(passed=1))
    assert not numeric_equal(dict(count=6),dict(count=7))
