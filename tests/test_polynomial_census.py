"""Exact known-root and separate Sturm controls; no Rössler outcomes."""
from copy import deepcopy
from fractions import Fraction as F
import pytest
from butterfly import polynomial_census as census
from scripts import exp500_census_analysis as analysis
from scripts import verify_quadratic_symbolic_control as sturm


@pytest.mark.parametrize("power,count", [([1,0,1],0),([-1,2],1),([3,-16,16],2),
    ([0,-1,1],2),([0,2,-6,4],3),([1,-4,4],1),([-2,0,4],1)])
def test_known_complete_roots(power,count):
    proof = census.isolate(power,F(1))
    result = census.verify(power,F(1),proof)
    assert result["complete"] and len(result["roots"]) == count
    for row in result["roots"]:
        assert F(row[1])-F(row[0]) <= F("1e-25")


def test_two_roots_with_identical_endpoint_signs():
    # (u-1/2)^2-1e-24: no endpoint sign-change detector sees this pair.
    power = census.integers([F(1,4)-F("1e-24"),-1,1])
    checked = census.verify(power,1,census.isolate(power,1))
    assert checked["complete"] and len(checked["roots"]) == 2
    assert census.evaluate(power,F(0))*census.evaluate(power,F(1)) > 0


@pytest.mark.parametrize("power",[[-2,0,4],[3,-16,16],[0,2,-6,4],[-3,22,-48,32]])
def test_distinct_root_counts_match_independent_sturm(power):
    count = sturm.isolate_roots(tuple(power),F(0),F(1),bits=30,budget=sturm.Budget())[1]
    checked = census.verify(power,1,census.isolate(power,1))
    assert checked["complete"] and len(checked["roots"]) == count


@pytest.mark.parametrize("power",[[0,0,0],[4,-12,9]])
def test_flat_and_nondyadic_repeated_roots_remain_unresolved(power):
    result = census.verify(power,1,census.isolate(power,1,max_depth=12))
    assert not result["complete"] and result["unresolved"]


def test_forced_search_and_refinement_limits_do_not_become_empty():
    power = census.integers([F(1,9)-F("1e-24"),F(-2,3),1])
    for kwargs in (dict(max_depth=1),dict(max_nodes=1)):
        assert not census.verify(power,1,census.isolate(power,1,**kwargs))["complete"]
    assert not census.verify([-2,0,4],1,census.isolate([-2,0,4],1,max_refinements=1))["complete"]


def test_scaled_power_and_direct_affine_transform():
    coefficients = ["0.125","-0.3","0.7","-0.0003"]
    power = census.scaled_power(coefficients,F("0.02"),F("0.01"))
    ratios = [F(a)/(F(v)*F("0.02")**i-(F("0.01") if i == 0 else 0)) for i,(a,v) in enumerate(zip(power,coefficients))]
    assert len(set(ratios)) == 1 and ratios[0] > 0
    initial = census.bernstein(power)
    for path in ("L","R","LRR","RLL"):
        b = initial
        for c in path: b = census.split(b)[c == "R"]
        direct = census.direct_bernstein(power,*census.path_interval(path))
        ratios = [F(x)/y for x,y in zip(b,direct) if y]
        assert len(set(ratios)) == 1 and ratios[0] > 0


@pytest.mark.parametrize("mutation",["missing","root","count","point"])
def test_complete_certificate_tampering_is_rejected(mutation):
    power = [0,2,-6,4]
    proof = deepcopy(census.isolate(power,1))
    if mutation == "missing": proof["leaves"].pop()
    elif mutation == "point": proof["points"].pop()
    elif mutation == "count": proof["leaves"][0] = dict(path="",kind="dominance")
    else:
        power = [-2,0,4]
        proof = census.isolate(power,1)
        proof["leaves"][0]["root"] = ["1/8","1/8"]
    with pytest.raises(ValueError): census.verify(power,1,proof)


def raw_fixture():
    return dict(config=dict(digits=40,order=3),horizon="1",scales=[15.,15.,.01],
        field=dict(constant=[0,1,0],linear=[],quadratic=[]),
        steps=[dict(time="0",step="1",coefficients=[["0"]*4,["-0.5","1","0","0"],["1","0","0","0"]])])


def test_actual_profile_census_and_classifier_replay():
    raw = raw_fixture()
    section = dict(offset=0,gate_upper=1)
    result,proof = analysis.profile(raw,section)
    replay,_ = analysis.profile(raw,section,certificate=proof)
    assert result == replay and result["complete"]
    assert len(result["events"]) == 1
    assert result["events"][0]["direction"] == 1 and not result["events"][0]["accepted"]


def test_exact_decimal_zero_with_extreme_exponent_does_not_expand_power():
    assert analysis.exact("0E-999999999") == 0
    assert analysis.exact("-0E+999999999") == 0
    assert analysis.exact("1.25E-20") == F(125,10**22)
    assert analysis.exact("1/3") == F(1,3)


def test_certificate_audit_does_not_use_producer_subdivision(monkeypatch):
    power = census.integers([F(1,9)-F("1e-24"),F(-2,3),1])
    proof = census.isolate(power,1)
    def forbidden(*args,**kwargs): pytest.fail("audit used producer subdivision")
    monkeypatch.setattr(census,"split",forbidden)
    monkeypatch.setattr(census,"isolate",forbidden)
    assert census.verify(power,1,proof)["complete"]


def test_inconsistent_join_is_not_silently_bridged():
    raw = raw_fixture()
    raw["steps"][0]["step"] = ".5"
    raw["steps"].append(dict(time=".5",step=".5",coefficients=[["0"]*4,[".01","1","0","0"],["1","0","0","0"]]))
    result,_ = analysis.profile(raw,dict(offset=0,gate_upper=1))
    assert not result["complete"] and result["join_failures"]


@pytest.mark.parametrize("kind",["field-direction","gate","cutoff"])
def test_ambiguous_classification_cannot_qualify(kind):
    raw = raw_fixture()
    section = dict(offset=0,gate_upper=1)
    if kind == "field-direction": raw["field"]["constant"][1] = -1
    if kind == "gate": section["gate_upper"] = 0
    if kind == "cutoff":
        poly = [[F(v) for v in p] for p in raw["steps"][0]["coefficients"]]
        event = analysis.classify(poly,F(0),F(1),["0.0000000099999999","0.0000000100000001"],raw["field"],section)
        assert not event["classification_qualified"]
    else:
        result,_ = analysis.profile(raw,section)
        assert not result["complete"]
