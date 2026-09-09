import json

import numpy as np
import pytest

from butterfly.models import RosslerParameters,rossler_jacobian
from butterfly.projected_fold_shooting import equations,event_second_derivative
from butterfly.projected_fold_qualification import compare,image_from_census,qualify
from butterfly.poincare import PoincareSection
from scripts import run_exp490_direct_folds as run
from scripts.run_exp486_return_image_folds import control_field


def analytic(u,t):
    k=1e4
    x,z=-4+u,.005+.01*u
    rho=np.exp(-.03*t)
    c,s=np.cos(t),np.sin(t)
    base=x-k*z*z
    first_base=1-2*k*z*.01
    second_base=-2*k*.01**2
    q=np.array([base*c+k*z*z*rho*rho,base*s,z*rho])
    v=np.array([first_base*c+2*k*z*.01*rho*rho,first_base*s,.01*rho])
    w=np.array([second_base*c+2*k*.01**2*rho*rho,second_base*s,0.])
    return q,v,w


def test_fold_equation_jacobian_matches_analytic_finite_difference():
    rhs,jac=control_field(1e4)
    def value(u,t):
        q,v,w=analytic(u,t)
        return equations(q,v,w,rhs(t,q),jac(t,q),0.)
    u,t=.31,12.58
    residual,matrix=value(u,t)
    eps=1e-5
    numerical=np.column_stack(((value(u+eps,t)[0]-value(u-eps,t)[0])/(2*eps),
                               (value(u,t+eps)[0]-value(u,t-eps)[0])/(2*eps)))
    assert np.isfinite(residual).all()
    assert np.allclose(matrix,numerical,rtol=1e-8,atol=1e-8)


@pytest.mark.parametrize("count",[2,3,5,9])
def test_event_second_derivative_has_known_value(count):
    t=2*np.pi*count
    rhs,jac=control_field(1e4)
    q,v,w=analytic(.27,t)
    f,j=rhs(t,q),jac(t,q)
    residual,matrix=equations(q,v,w,f,j,0.)
    second=event_second_derivative(v,f,j,residual,matrix)
    assert np.isclose(second,-2*(1-np.exp(-.06*t)),rtol=0,atol=1e-12)


def test_rossler_hessian_contraction_matches_jacobian_difference():
    rng=np.random.default_rng(490)
    p=RosslerParameters(a=.21575,b=.2,c=7.212)
    for _ in range(10):
        q,v=rng.normal(size=(2,3))
        eps=1e-5
        measured=(rossler_jacobian(q+eps*v,p)-rossler_jacobian(q-eps*v,p))@v/(2*eps)
        assert np.allclose(measured,[0.,0.,2*v[0]*v[2]],rtol=0,atol=1e-9)


def test_public_candidate_table_is_complete_and_identity_bound():
    p=json.loads(run.PLAN.read_bytes())
    candidates=json.loads((run.ROOT/p["candidates_path"]).read_bytes())
    run.validate_candidates(candidates,p)
    assert len(candidates)==26
    assert len({c["family_id"] for c in candidates})==16
    candidates[-1]=candidates[0]
    with pytest.raises(ValueError,match="identity"):
        run.validate_candidates(candidates,p)


def test_missing_candidate_and_solver_rejected():
    p=json.loads(run.PLAN.read_bytes())
    candidates=json.loads((run.ROOT/p["candidates_path"]).read_bytes())
    with pytest.raises(ValueError,match="matrix"):
        run.validate_candidates(candidates[:-1],p)
    with pytest.raises(ValueError,match="matrix"):
        compare(candidates[0],[],p)
    p["thresholds"]["state"]=1e-3
    with pytest.raises(ValueError,match="settings"):
        run.validate_candidates(candidates,p)


def test_uncertain_and_missing_events_are_not_imputed():
    section=PoincareSection((0.,1.,0.),0.,-1)
    rhs=lambda t,q:np.array([1.,-1.,0.])
    p=json.loads(run.PLAN.read_bytes())
    report=dict(reconstructed=[],uncertain_extrema=[])
    assert image_from_census(report,5,rhs,section,p["thresholds"])["status"]=="unresolved"
    event=dict(time=1.,accepted=True,angle=1.,residual=0.,state=[-1.,0.,.01],raw_tangent=[1.,0.,0.])
    report=dict(reconstructed=[dict(event,time=float(i+1)) for i in range(5)],uncertain_extrema=[dict(time=.5)])
    assert image_from_census(report,5,rhs,section,p["thresholds"])["status"]=="unresolved"


def test_nonfinite_equations_rejected():
    with pytest.raises(ValueError,match="nonfinite"):
        equations([np.nan,0.,0.],[0.,0.,0.],[0.,0.,0.],[1.,1.,1.],np.eye(3),0.)


@pytest.mark.parametrize("power,expected",[(2,True),(3,False)])
def test_stationary_inflection_is_not_a_fold(power,expected):
    p=json.loads(run.PLAN.read_bytes())
    eps=1e-6
    c=dict(count=2,epsilon=eps,old_x_interval=[-4.,0.])
    root=dict(u=0.,time=2.,state=[-3.,0.,.01],event_second_derivative=2. if power==2 else 0.)
    shooting=dict(converged=True,trace=[root])
    reports=[]
    for u in (-eps,0.,eps):
        events=[dict(time=1.,state=[-2+u,0.,.01],raw_tangent=[1.,0.,0.],accepted=True,angle=1.,residual=0.),
                dict(time=2.,state=[-3+u**power,0.,.01],raw_tangent=[power*u**(power-1),0.,0.],accepted=True,angle=1.,residual=0.)]
        reports.append(dict(offset=u,report=dict(reconstructed=events,uncertain_extrema=[])))
    result=qualify(shooting,reports,c,lambda t,q:np.array([0.,-1.,0.]),PoincareSection((0.,1.,0.),0.,-1),p)
    assert result["qualified"] is expected
    if power==3:
        assert not result["checks"]["opposite_slopes"]
        assert not result["checks"]["nondegenerate"]


def test_separate_rossler_fold_algebra_matches_vector_formula():
    from scripts.audit_exp490_direct_folds import separate_algebra
    from butterfly.models import rossler_rhs
    rng=np.random.default_rng(49002)
    p=RosslerParameters(a=.21575,b=.2,c=7.212)
    for _ in range(10):
        q,v,w=rng.normal(size=(3,3))
        a,b,_=separate_algebra(dict(state=q,first=v,second=w),p,-.027)
        r,j=equations(q,v,w,rossler_rhs(0,q,p),rossler_jacobian(q,p),-.027)
        assert np.allclose(a,r,rtol=1e-12,atol=1e-12)
        assert np.allclose(b,j,rtol=1e-12,atol=1e-12)


def test_actual_control_pipeline_rejects_both_negatives():
    p=json.loads(run.PLAN.read_bytes())
    p["controls"]["counts"]=[2]
    p["solvers"]=["DOP853"]
    rows=run.controls(p)
    assert [r["kind"] for r in rows]==["fold","no-fold","projection-degenerate"]
    assert all(r["passed"] for r in rows)


def test_integration_failure_keeps_auditable_iteration(monkeypatch,tmp_path):
    from types import SimpleNamespace
    from butterfly import projected_fold_shooting as kernel
    from scripts.audit_exp490_direct_folds import check_trace
    p=json.loads(run.PLAN.read_bytes())
    c=json.loads((run.ROOT/p["candidates_path"]).read_bytes())[0]
    par=RosslerParameters(**c["parameters"])
    from butterfly.poincare import legacy_rossler_section
    section=legacy_rossler_section(par)
    def failed(_rhs,interval,initial,**kwargs):
        return SimpleNamespace(t=np.array([0.,.2]),y=np.column_stack((initial,initial)),success=False)
    monkeypatch.setattr(kernel,"solve_ivp",failed)
    retained=[]
    def retain(i,raw):
        retained.append(f"newton-{i}")
        with (tmp_path/f"test--newton-{i}.npz").open("xb") as stream:
            np.savez_compressed(stream,**raw)
    result=kernel.shoot(lambda *_:None,lambda *_:None,lambda *_:None,c,section,"DOP853",p,retain)
    result["retained_labels"]=retained
    assert not result["converged"]
    assert result["trace"][0]["integration_failed"]
    assert check_trace(result,c,"DOP853",p,tmp_path,"test",par,section)==["test--newton-0.npz"]
