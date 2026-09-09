"""Source/plan/complete-input guards; never inspect a new target census."""
import builtins
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
from scripts import run_exp500_polynomial_census as run
from scripts import exp500_census_analysis as analysis


@pytest.fixture(scope="module")
def inputs(): return run.load()


def test_complete_matrix_preserves_both_configurations_and_ledger(inputs):
    p,old = inputs
    assert len(p["ledger"]) == 26 and len(p["trials"]) == 32
    assert sum(len(r["profiles"]) for r in p["trials"]) == 64
    assert [r["id"] for r in p["trials"]] == [r["id"] for r in old["rows"]]
    assert all([v["configuration"] for v in r["profiles"]] == ["decimal-40","decimal-50"] for r in p["trials"])
    assert p["new_integrations"] == 0 and p["repairs_exp498"] is False
    assert p["isolation"]["time_width"] == "1e-25" and p["comparison"]["scaled_state"] == "1e-9"


@pytest.mark.parametrize("kind",["row","profile","threshold","raw-anchor","ledger"])
def test_self_consistent_plan_edits_fail(inputs,tmp_path,monkeypatch,kind):
    p = deepcopy(inputs[0])
    if kind == "row": p["trials"].pop()
    elif kind == "profile": p["trials"][0]["profiles"].pop()
    elif kind == "threshold": p["comparison"]["scaled_state"] = "1e-6"
    elif kind == "raw-anchor": p["raw_summary_sha256"] = "0"*64
    else: p["ledger"].pop()
    path = tmp_path/"plan.json"
    run.write_json(path,p)
    monkeypatch.setattr(run,"PLAN",path)
    with pytest.raises(ValueError): run.load()


def test_complete_comparison_rejects_missing_nominations_or_profiles(inputs):
    p,old = inputs
    parent = old["rows"][0]
    profiles = []
    for v in parent["profiles"]:
        events = [dict(e,direction=-1,half_plane="inside",time_class="after",classification_qualified=True,accepted=True) for e in v["events"]]
        profiles.append(dict(configuration=v["configuration"],analysis=dict(complete=True,events=events)))
    assert analysis.compare(profiles,parent,p["scales"])["qualified"]
    profiles[0]["analysis"]["events"].pop()
    assert not analysis.compare(profiles,parent,p["scales"])["qualified"]
    with pytest.raises(ValueError): analysis.compare(profiles[:1],parent,p["scales"])


def test_read_inputs_are_in_sealed_inventory(monkeypatch):
    seen = set()
    def wrap(opener):
        def observed(file,*args,**kwargs):
            if isinstance(file,(str,os.PathLike)):
                path = Path(file).resolve()
                if path.is_relative_to(run.ROOT):
                    name = path.relative_to(run.ROOT).as_posix()
                    if name.startswith(("docs/","experiments/")): seen.add(name)
            return opener(file,*args,**kwargs)
        return observed
    monkeypatch.setattr(io,"open",wrap(io.open))
    monkeypatch.setattr(builtins,"open",wrap(builtins.open))
    p,_ = run.load()
    assert seen <= set(p["source_paths"])|set(p["inputs"])


def test_actual_sealed_source_validate_and_fixture_cli(inputs,tmp_path):
    p,_ = inputs
    stage = tmp_path/"source"
    for name in sorted(set(p["source_paths"])|set(p["inputs"])):
        target = stage/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(run.ROOT/name,target)
    code = ('import sys,runpy;from pathlib import Path;root=Path(sys.argv.pop(1));'
            'sys.path[:0]=[str(root),str(root/"python")];'
            'runpy.run_module("scripts.run_exp500_polynomial_census",run_name="__main__");'
            'assert all(Path(m.__file__).resolve().is_relative_to(root.resolve()) '
            'for n,m in sys.modules.items() if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    for options in ([],["--fixture-controls"]):
        result = subprocess.run([sys.executable,"-I","-B","-c",code,str(stage),*options],cwd=tmp_path,
            env={"PATH":os.defpath,"LANG":"C","MPLCONFIGDIR":str(tmp_path/"cache")},
            capture_output=True,text=True,timeout=60)
        assert result.returncode == 0,result.stderr
        assert json.loads(result.stdout)["new_integrations"] == 0
    assert not list(stage.rglob("*.pyc"))


def test_fixture_controls_need_no_trajectory_integrator(monkeypatch):
    def forbidden(*args,**kwargs): pytest.fail("fixture must not integrate")
    monkeypatch.setattr(run.taylor,"integrate",forbidden)
    assert run.fixture_controls()["passed"]
