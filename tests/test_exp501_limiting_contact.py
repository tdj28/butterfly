"""Prospective input/closure checks and synthetic all-variant decision tests."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
from scripts import run_exp501_limiting_contact as run
from scripts import exp501_contact_analysis as a


def test_parent_anchored_complete_matrix():
    p = run.load()
    assert len(p["candidates"]) == 8 and len(p["cycles"]) == 4 and len(p["ledger"]) == 26
    assert sum(c["parent_qualified"] is False for c in p["candidates"]) == 1
    assert sum(c["original_exp498_qualified"] is False for c in p["candidates"]) == 2
    assert p["limits"]["target_ivps"] == 128
    assert p["thresholds"]["contact"] == "1e-4"
    assert p["section"]["offset"] == p["candidates"][0]["initial_state"][1]


@pytest.mark.parametrize("kind",["candidate","cycle","ledger","threshold","source"])
def test_self_consistent_plan_substitutions_fail(kind,tmp_path,monkeypatch):
    p = deepcopy(run.load())
    if kind == "candidate":
        p["candidates"].pop()
    elif kind == "cycle":
        p["cycles"][0]["states"].pop()
    elif kind == "ledger":
        p["ledger"].pop()
    elif kind == "threshold":
        p["thresholds"]["contact"] = "0.1"
    else:
        p["source_paths"].remove("python/butterfly/decimal_grazing.py")
    path = tmp_path/"plan.json"
    run.write_json(path,p)
    monkeypatch.setattr(run,"PLAN",path)
    with pytest.raises(ValueError):
        run.load()


def synthetic_rows():
    profiles = [dict(configuration=c["name"],shooting=dict(status="qualified",trace=[dict(u="0",time="1",state=["0"]*3)]),
                    census=dict(complete=True,events=[dict(time="0.1",state=["0"]*3,accepted=True)])) for c in run.numeric.CONFIGS]
    cycles = [dict(method=m,phase=phase,states=[[0.,0.,0.]]*6) for m in ("DOP853","Radau") for phase in (0.,.5)]
    return [dict(id=str(i),profiles=deepcopy(profiles),comparison=a.compare(profiles,dict(accepted_prefix=1),cycles)) for i in range(8)]


def test_all_variants_not_best_case_govern_membership():
    rows = synthetic_rows()
    result = a.aggregate(rows)
    assert result["complete"] and result["verdict"] == "proximate" and result["comparison_cells"] == 384
    for cell in rows[-1]["comparison"]["comparisons"]:
        cell["scaled_distance"] = "0.01"
    result = a.aggregate(rows)
    assert result["verdict"] == "not-proximate" and not any(v["all_proximate"] for v in result["cycle_indices"])
    rows[-1]["comparison"]["qualified"] = False
    assert a.aggregate(rows)["verdict"] == "mixed"
    with pytest.raises(ValueError):
        a.aggregate(rows[:7])


def test_missing_profile_and_wrong_prefix_do_not_pass():
    profiles = synthetic_rows()[0]["profiles"]
    with pytest.raises(ValueError):
        a.compare(profiles[:1],dict(accepted_prefix=1),[])
    assert not a.compare(profiles,dict(accepted_prefix=2),run.load()["cycles"])["qualified"]


def test_exact_sealed_source_startup(tmp_path):
    p = run.load()
    stage = tmp_path/"source"
    for name in sorted(set(p["source_paths"])|set(p["inputs"])):
        target = stage/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(run.ROOT/name,target)
    code = ('import sys,runpy;from pathlib import Path;root=Path(sys.argv.pop(1));'
            'sys.path[:0]=[str(root),str(root/"python")];'
            'runpy.run_module("scripts.run_exp501_limiting_contact",run_name="__main__");'
            'assert all(Path(m.__file__).resolve().is_relative_to(root.resolve()) '
            'for n,m in sys.modules.items() if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    result = subprocess.run([sys.executable,"-I","-B","-c",code,str(stage)],cwd=tmp_path,
                            env={"PATH":os.defpath,"LANG":"C"},capture_output=True,text=True,timeout=60)
    assert result.returncode == 0,result.stderr
    assert json.loads(result.stdout) == dict(valid=True,candidates=8,target_integrations=0,import_closure=True)
    assert not list(stage.rglob("*.pyc"))
