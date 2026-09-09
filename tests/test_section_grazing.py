import copy
import json

import numpy as np
import pytest

from butterfly.section_grazing import grazing_equations, shoot, side_verdict
from butterfly.poincare import PoincareSection
from scripts import run_exp489_section_grazing as run


def plan():
    return json.loads(run.PLAN.read_bytes())


def test_equations_match_finite_differences():
    # x=t-.5, y=(t-.5)^2+delta; derivative matrix [[1,2x],[0,2]].
    delta,t = .001,.48
    q = np.array([t-.5,(t-.5)**2+delta,0.])
    f = np.array([1.,2*q[0],0.])
    j = np.array([[0.,0.,0.],[2.,0.,0.],[0.,0.,0.]])
    residual,matrix = grazing_equations(q,[0.,1.,0.],f,j,[0.,1.,0.],0.)
    def fun(d,t):
        return np.array([(t-.5)**2+d,2*(t-.5)])
    eps = 1e-6
    numerical = np.column_stack(((fun(delta+eps,t)-fun(delta-eps,t))/(2*eps),
                                 (fun(delta,t+eps)-fun(delta,t-eps))/(2*eps)))
    assert np.allclose(matrix,numerical,rtol=0,atol=1e-9)
    assert np.allclose(residual,fun(delta,t))


@pytest.mark.parametrize("method",["DOP853","Radau"])
def test_known_grazing_root_and_search_box(method):
    rhs = lambda t,q:np.array([1.,2*q[0],0.])
    jac = lambda t,q:np.array([[0.,0.,0.],[2.,0.,0.],[0.,0.,0.]])
    section = PoincareSection((0.,1.,0.),0.,-1)
    p = plan()
    r = shoot(rhs,jac,[-.5,.25001,0.],[0.,1.,0.],section,.498,method=method,plan=p,retain=lambda *_:None)
    assert r["converged"]
    assert abs(r["trace"][-1]["delta"]+1e-5) < 1e-10
    p["delta_bound"] = 1e-12
    r = shoot(rhs,jac,[-.5,.25001,0.],[0.,1.,0.],section,.498,method=method,plan=p,retain=lambda *_:None)
    assert not r["converged"]


def test_pair_no_pair_and_uncertain_are_distinct():
    p = plan()
    p["accepted_prefix"] = 0
    root = dict(time=.5,jacobian=[[1.,0.],[0.,2.]])
    dose = -1e-6
    pair = [dict(time=t,accepted=t<.5,residual=0.,angle=.01) for t in (.499,.501)]
    report = dict(reconstructed=pair,uncertain_extrema=[])
    assert side_verdict(report,root,dose,p)["passed"]
    assert not side_verdict(report,root,-dose,p)["passed"]
    report["uncertain_extrema"] = [dict(time=.5)]
    assert not side_verdict(report,root,dose,p)["passed"]
    report["uncertain_extrema"] = []
    p["accepted_prefix"] = 4
    assert not side_verdict(report,root,dose,p)["passed"]
    report["reconstructed"] = [dict(time=t,accepted=True) for t in (.1,.2,.3,.4)]+pair
    assert side_verdict(report,root,dose,p)["passed"]


def test_missing_matrix_and_weakened_plan_rejected():
    p = plan()
    run.validate_plan(p)
    with pytest.raises(ValueError,match="matrix"):
        run.compare_case("synthetic",[],p)
    p["doses"].pop()
    with pytest.raises(ValueError,match="matrix"):
        run.validate_plan(p)


def test_all_normal_form_profiles_pass():
    controls = run.controls(plan())
    assert len(controls) == 2
    assert all(c["passed"] for c in controls)
    assert all(abs(c["verdict"]["square_root_ratio"]-np.sqrt(10)) < 1e-4 for c in controls)
    bad = copy.deepcopy(controls[0])
    bad["sides"].pop()
    with pytest.raises(ValueError,match="matrix"):
        run.evaluate_root(bad["shooting"],bad["sides"],plan())
