"""Analytic-only checks: no new Rössler target outcomes."""
from copy import deepcopy
from decimal import Decimal as D, localcontext
import pytest
from butterfly import decimal_grazing as n
from butterfly.decimal_taylor import load_stream
from scripts import exp501_analytic_controls as c
from scripts import audit_exp501_limiting_contact as audit


def test_augmented_quadratic_differentiates_both_factors():
    f = dict(constant=[0,0,0],linear=[],quadratic=[[0,1,1,2]])
    augmented = n.augment(f)
    assert augmented["quadratic"] == [[0,1,1,2],[3,4,1,2],[3,1,4,2]]
    assert n.field_value([0,3,0,0,5,0],augmented) == [18,0,0,60,0,0]


@pytest.mark.parametrize("config",n.CONFIGS)
def test_quadratic_exponential_state_and_variation(config):
    field = n.augment(dict(constant=[1,0,0],linear=[],quadratic=[[2,0,2,1]]))
    initial = ["0","0","1","1","0","0"]
    raw = n.integrate(initial,field,"0.3",config)
    audit.check_raw(raw,initial,field,"0.3",config)
    with localcontext() as ctx:
        ctx.prec = 70
        expected = D("0.045").exp()
        assert abs(D(raw["final"][2])-expected) < D("1e-25")
        assert abs(D(raw["final"][5])-D("0.3")*expected) < D("1e-25")


def test_raw_coefficient_corruption_rejected():
    _,f,_ = c.case("parabola")
    initial = ["-1","1","1","0","1","0"]
    raw = n.integrate(initial,f,"0.05",n.CONFIGS[0])
    raw["steps"][0]["coefficients"][5][3] = "1"
    with pytest.raises(ValueError,match="recurrence"):
        audit.check_raw(raw,initial,f,"0.05",n.CONFIGS[0])


def test_singular_newton_and_invalid_configuration():
    with pytest.raises(ValueError,match="singular"):
        n.newton_delta([D(1),D(2)],[[D(1),D(2)],[D(2),D(4)]])
    with pytest.raises(ValueError):
        n.integrate([0]*6,dict(constant=[0]*6,linear=[],quadratic=[]),1,dict(n.CONFIGS[0],step="0"))


def test_box_exit_does_not_integrate():
    candidate,field,offset = c.case("rotation")
    candidate["seed_u"] = "1"
    def forbidden(*args):
        pytest.fail("box-exit must not integrate")
    result,raw = n.shooting(candidate,field,offset,n.CONFIGS[0],forbidden)
    assert result["status"] == "box-exit" and raw is None and result["trace"] == []


def test_initial_decimal_curve_is_not_silently_old_float_arithmetic():
    candidate = dict(initial_state=[.1,0.,.2],initial_tangent=[.3,0.,.4])
    with localcontext() as ctx:
        ctx.prec = 50
        initial = n.initial_at(candidate,D("0.123"))
        assert D(initial[0]) == n.exact(.1)+D("0.123")*n.exact(.3)
        assert D(initial[0]) != n.exact(.1+.123*.3)


def test_prefix_preserves_polynomials_and_excludes_final_tangency():
    _,field,_ = c.case("parabola")
    raw = n.integrate(["-1","1","1","0","1","0"],field,"1",n.CONFIGS[0])
    prefix = n.prefix_state(raw,D("0.955"))
    assert prefix["horizon"] == "0.955"
    assert prefix["steps"][-1]["step"] == "0.015"
    assert all(r["coefficients"] == old["coefficients"][:3] for r,old in zip(prefix["steps"],raw["steps"]))
    with pytest.raises(ValueError):
        n.prefix_state(raw,1)


def test_full_analytic_controls_and_separate_raw_audit(tmp_path):
    output = tmp_path/"controls"
    receipt = c.run(output)
    audit.check_controls(output,receipt)
    assert len(receipt["profiles"]) == 4 and all(r["passed"] for r in receipt["profiles"])
    broken = deepcopy(receipt)
    broken["profiles"].pop()
    with pytest.raises(ValueError):
        audit.check_controls(output,broken)


def test_partial_archive_rejected(tmp_path):
    from butterfly.decimal_taylor import StreamArchive
    path = tmp_path/"partial.json.gz"
    archive = StreamArchive(path,{})
    archive.step(dict(time="0"))
    archive.close()
    with pytest.raises(ValueError,match="incomplete"):
        load_stream(path)
