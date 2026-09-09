import copy
import json

import pytest

from scripts.plot_exp490_direct_folds import TABLE,derive


def fixture():
    rows=[]
    for c in json.loads(TABLE.read_bytes()):
        rows.append(dict(id=c["id"],qualified=False,qualified_in_region=False,
                         solvers=[dict(method=m,qualified=False,reason="fixed search box exceeded") for m in ("DOP853","Radau")]))
    return dict(experiment_id="EXP-490",status="completed-audited",candidates=rows)


def test_figure_keeps_all_unresolved_candidates_and_both_solvers():
    data=derive(fixture())
    assert len(data)==26
    assert all(d["paired"]=="U" and d["input_x"] is None for d in data)
    assert sum(len(d["solvers"]) for d in data)==52


@pytest.mark.parametrize("damage",["candidate","solver","duplicate","false_pair"])
def test_figure_rejects_incomplete_or_conflicting_results(damage):
    result=fixture()
    if damage=="candidate":
        result["candidates"].pop()
    elif damage=="solver":
        result["candidates"][0]["solvers"].pop()
    elif damage=="duplicate":
        result["candidates"][-1]=copy.deepcopy(result["candidates"][0])
    else:
        result["candidates"][0]["qualified"]=True
    with pytest.raises(ValueError):
        derive(result)


def test_figure_distinguishes_failed_checks_invalid_projection_and_qualified_location():
    result=fixture()
    row=result["candidates"][0]
    row["solvers"][0]["checks"]={"event_time":False}
    row["solvers"][1]["observations"]=[]
    data=derive(result)
    assert [s["code"] for s in data[0]["solvers"]]==["F","E"]
    row["qualified"]=True
    for s in row["solvers"]:
        s["qualified"]=True
        s["observations"]=[{},dict(image_state=[-6.8,0.,.01])]
    assert derive(result)[0]["input_x"]==[-6.8,-6.8]
    assert not derive(result)[0]["in_region"]
