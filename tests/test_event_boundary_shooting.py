"""Bounded boundary-localization tests, with no target integrations."""
from copy import deepcopy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from butterfly import event_boundary_shooting as boundary
from butterfly.poincare import PoincareSection
from scripts import build_exp492_event_boundaries as builder
from scripts import run_exp492_event_boundaries as run


@pytest.fixture
def plan():
    return json.loads(run.PLAN.read_bytes())


def test_complete_public_input_reconstruction(plan):
    table,rows = run.load(plan)
    assert len(table["intervals"]) == 26 and len(rows) == 16
    assert len({r["family_id"] for r in rows}) == 10
    assert {r["accepted_prefix"] for r in rows} == {0,1,4,5,6,8}
    assert sum(len(r["evidence"]) for r in rows) == 64


@pytest.mark.parametrize("change",["missing","duplicate","seed","prefix","self-consistent-raw"])
def test_input_tampering_fails(plan,change):
    table,_ = run.load(plan)
    row = next(r for r in table["intervals"] if r["status"] == "nominated")
    if change == "missing":
        table["intervals"].pop()
    elif change == "duplicate":
        table["intervals"][-1] = deepcopy(row)
    elif change == "seed":
        row["seed_u"] += 1e-5
    elif change == "prefix":
        row["accepted_prefix"] += 1
    else:
        e = row["evidence"][0]
        e["raw"]["report"]["extrema"][0]["plane_value"] += .01
        e["sha256"] = builder.digest(e["raw"])
        table["parent_summary_metadata"]["files"][e["path"]]["sha256"] = e["sha256"]
    with pytest.raises(ValueError):
        builder.validate(table)


@pytest.mark.parametrize("key",["root_plane","side_solver_time","newton_iterations","minimum_unfolding"])
def test_frozen_settings_not_weakened(plan,key):
    plan[key] *= 2
    with pytest.raises(ValueError):
        run.load(plan)


@pytest.mark.parametrize("prefix",[0,1,4,5,6,8])
def test_polynomial_control_jacobian_and_grazing_coefficients(prefix):
    rhs,jac = run.polynomial_field(prefix)
    target = 2*prefix+1.
    q = np.array([0.,0.,target])
    assert rhs(target,q)[1] == 0.
    assert jac(target,q)[1,2] == pytest.approx(2.,rel=1e-13)
    assert jac(target,q)[1,0] == pytest.approx(sum(1/j for j in range(1,2*prefix+1)),rel=1e-13,abs=1e-15)
    q = np.array([.001,0.,target+.02])
    h = 1e-6
    fd = np.column_stack([(rhs(0.,q+h*e)-rhs(0.,q-h*e))/(2*h) for e in np.eye(3)])
    np.testing.assert_allclose(jac(0.,q),fd,rtol=1e-7,atol=1e-8)


@pytest.mark.parametrize("method",["DOP853","Radau"])
def test_real_analytic_shooting_and_hard_box(plan,method):
    c = run.control_specs()[0]
    rhs,jac = run.fields_for_control(c)
    raw = []
    r = boundary.shoot(rhs,jac,PoincareSection((0.,1.,0.),0.,-1),c,plan,method,lambda i,a:raw.append(a))
    assert r["converged"] and len(raw) == len(r["trace"])
    assert r["trace"][-1]["u"] == pytest.approx(-1e-5,abs=1e-10)
    bad = dict(c,u_box=[-1e-8,1e-8])
    r = boundary.shoot(rhs,jac,PoincareSection((0.,1.,0.),0.,-1),bad,plan,method,lambda *_:None)
    assert not r["converged"] and r["reason"] == "prospective search box exceeded"


def test_resource_guard_runs_before_any_ivp(plan,monkeypatch):
    calls = []
    monkeypatch.setattr(boundary,"solve_ivp",lambda *a,**k:calls.append(True))
    def guard():
        raise RuntimeError("test cap")
    c = run.control_specs()[0]
    rhs,jac = run.fields_for_control(c)
    with pytest.raises(RuntimeError,match="test cap"):
        boundary.shoot(rhs,jac,PoincareSection((0.,1.,0.),0.,-1),c,plan,"DOP853",lambda *_:None,guard)
    assert not calls


def test_failed_integration_mesh_and_trace_retained(plan,monkeypatch):
    c = run.control_specs()[0]
    initial = np.r_[c["initial_state"],c["initial_tangent"]]
    monkeypatch.setattr(boundary,"solve_ivp",lambda *a,**k:SimpleNamespace(success=False,t=np.array([0.,.1]),y=np.column_stack([initial,initial])))
    kept = []
    rhs,jac = run.fields_for_control(c)
    r = boundary.shoot(rhs,jac,PoincareSection((0.,1.,0.),0.,-1),c,plan,"DOP853",lambda i,a:kept.append(a))
    assert not r["converged"] and len(kept) == len(r["trace"]) == 1
    assert not r["trace"][0]["solver_success"]


def roots_for_test(c):
    root = dict(u=-1e-5,time=1.,state=[0.,0.,1.],residual=[0.,0.],jacobian=[[2.,0.],[0.,2.]])
    return [dict(method=m,shooting=dict(converged=True,trace=[deepcopy(root)])) for m in ("DOP853","Radau")]


def test_common_center_and_joint_side_gate(plan):
    c = run.control_specs()[0]
    roots = roots_for_test(c)
    roots[1]["shooting"]["trace"][-1]["u"] += 1e-11
    result = boundary.root_pair(roots,c,plan)
    assert result["eligible"] and result["common_center_u"] == (-1e-5+(-1e-5+1e-11))/2
    roots[1]["shooting"]["trace"][-1]["jacobian"][0][0] = 0.
    result = boundary.assess(roots,[],c,plan)
    assert not result["qualified"] and not result["roots"]["eligible"]
    with pytest.raises(ValueError):
        boundary.assess(roots,[{}],c,plan)


def test_missing_solver_or_side_not_a_pass(plan):
    c = run.control_specs()[0]
    roots = roots_for_test(c)
    for bad in (roots[:1],roots[::-1],[roots[0],roots[0]]):
        with pytest.raises(ValueError):
            boundary.root_pair(bad,c,plan)
    with pytest.raises(ValueError):
        boundary.assess(roots,[],c,plan)


def test_side_doses_must_fit_frozen_box(plan):
    c = dict(run.control_specs()[0],u_box=[-1.01e-5,1e-3])
    assert not boundary.root_pair(roots_for_test(c),c,plan)["eligible"]


def synthetic_sides(c):
    sides = []
    for dose in c["doses"]:
        events = []
        if dose < 0:
            dt = np.sqrt(-2*dose)
            events = [dict(time=1+sign*dt,accepted=sign == -1,
                           state=[2*dose,0.,1+sign*dt],residual=0.,angle=.01,
                           bracket=[.9,1.1]) for sign in (-1,1)]
        sides.append(dict(dose=dose,u=-1e-5+dose,reports=[
            dict(method=m,reconstructed=deepcopy(events),uncertain_extrema=[])
            for m in ("DOP853","Radau")]))
    return sides


def test_complete_side_matrix_and_empty_sequence(plan):
    c = run.control_specs()[0]
    r = boundary.assess(roots_for_test(c),synthetic_sides(c),c,plan)
    assert r["qualified"]
    assert r["paired_sides"][-1]["counts"] == [0,0]
    assert all(v["square_root_ratio"] == pytest.approx(np.sqrt(10)) for v in r["solvers"])


@pytest.mark.parametrize("change",["count","time","state","prefix-uncertain","adjacent-uncertain","wrong-prefix","ratio"])
def test_side_failures_are_not_filtered(plan,change):
    c = run.control_specs()[0]
    sides = synthetic_sides(c)
    report = sides[0]["reports"][1]
    if change == "count":
        report["reconstructed"].pop(0)
    elif change == "time":
        report["reconstructed"][0]["time"] += 2e-7
    elif change == "state":
        report["reconstructed"][0]["state"][2] += 2e-8
    elif change.endswith("uncertain"):
        report["uncertain_extrema"] = [dict(time=.5 if change == "prefix-uncertain" else 1.1)]
    elif change == "wrong-prefix":
        c = dict(c,accepted_prefix=1)
    else:
        report["reconstructed"][0]["time"] -= .001
    assert not boundary.assess(roots_for_test(c),sides,c,plan)["qualified"]


@pytest.mark.parametrize("change",["missing-dose","duplicate-solver","side-input"])
def test_malformed_side_matrix_rejected(plan,change):
    c = run.control_specs()[0]
    sides = synthetic_sides(c)
    if change == "missing-dose":
        sides.pop()
    elif change == "duplicate-solver":
        sides[0]["reports"][1]["method"] = "DOP853"
    else:
        sides[0]["u"] += 1e-12
    with pytest.raises(ValueError):
        boundary.assess(roots_for_test(c),sides,c,plan)
