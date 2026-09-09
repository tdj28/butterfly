"""Prospective matrix, scalar replay and anti-tampering controls."""
from copy import deepcopy
from decimal import Decimal as D
import json
import builtins
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
from scripts import run_exp499_decimal_reference as run
from scripts import audit_exp499_decimal_reference as audit
from scripts import exp499_reference_controls as analytic


@pytest.fixture(scope="module")
def inputs():
    return run.load()


def test_exact_complete_matrix_includes_original_failures(inputs):
    p,old = inputs
    audit.check_inputs(p,old)
    assert len(p["ledger"]) == 26 and len(p["trials"]) == 32
    assert sum(len(row["boxes"]) for row in p["trials"]) == 240
    assert sum(not row["historical_parent_qualified"] for row in p["trials"]) == 4
    assert sum(not row["original_candidate_qualified"] for row in p["trials"]) == 8
    assert p["original_state"] == 1e-6 and p["reference_state"] == 1e-9
    assert p["configurations"] == analytic.CONFIGS


def test_every_read_public_input_is_in_sealed_inventory(monkeypatch):
    seen = set()
    def wrap(opener):
        def observed(file,*args,**kwargs):
            if isinstance(file,(str,os.PathLike)):
                path = Path(file).resolve()
                if path.is_relative_to(run.ROOT):
                    name = path.relative_to(run.ROOT).as_posix()
                    if name.startswith(("docs/", "experiments/")): seen.add(name)
            return opener(file,*args,**kwargs)
        return observed
    monkeypatch.setattr(io,"open",wrap(io.open))
    monkeypatch.setattr(builtins,"open",wrap(builtins.open))
    p,_ = run.load()
    assert seen <= set(p["source_paths"])|set(p["inputs"])
    assert set(run.TRANSITIVE_INPUTS) <= seen


def test_actual_isolated_source_load_without_host_checkout(inputs,tmp_path):
    p,_ = inputs
    stage = tmp_path/"source"
    for name in sorted(set(p["source_paths"])|set(p["inputs"])):
        target = stage/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(run.ROOT/name,target)
    code = ('import sys,runpy;from pathlib import Path;root=Path(sys.argv.pop(1));'
            'sys.path[:0]=[str(root),str(root/"python")];'
            'runpy.run_module("scripts.run_exp499_decimal_reference",run_name="__main__");'
            'assert all(Path(m.__file__).resolve().is_relative_to(root.resolve()) '
            'for n,m in sys.modules.items() if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    result = subprocess.run([sys.executable,"-I","-B","-c",code,str(stage)],cwd=tmp_path,
        env={"PATH":os.defpath,"LANG":"C","MPLCONFIGDIR":str(tmp_path/"cache")},
        capture_output=True,text=True,timeout=60)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["new_integrations"] == 0
    assert not list(stage.rglob("*.pyc"))


@pytest.mark.parametrize("kind",["missing","precision","radius","initial","box","failure"])
def test_self_consistent_plan_mutations_rejected(inputs,tmp_path,monkeypatch,kind):
    p = deepcopy(inputs[0])
    if kind == "missing": p["trials"].pop()
    elif kind == "precision": p["configurations"][0]["digits"] += 1
    elif kind == "radius": p["reference_state"] *= 2
    elif kind == "initial": p["trials"][0]["initial"][0] += .01
    elif kind == "box": p["trials"][0]["boxes"][0][0] = "0"
    else: next(r for r in p["trials"] if not r["original_candidate_qualified"])["original_candidate_qualified"] = True
    path = tmp_path/"plan.json"
    run.write_json(path,p)
    monkeypatch.setattr(run,"PLAN",path)
    with pytest.raises(ValueError): run.load()


def test_independent_box_mean_rejects_equal_width_shift(inputs):
    p,old = deepcopy(inputs)
    box = p["trials"][0]["boxes"][0]
    box[:] = [str(D(v)+1) for v in box]
    with pytest.raises(ValueError,match="root box"):
        audit.check_inputs(p,old)


def test_scalar_comparison_uses_every_reference_and_original(inputs):
    p,old = inputs
    trial = p["trials"][0]
    source = old["rows"][0]["boundary"]["sides"][0]["reports"][0]
    events = [dict(time=str(run.taylor.exact(e["time"])),state=[str(run.taylor.exact(v)) for v in e["state"]])
              for e in source["reconstructed"] if e["accepted"]]
    profiles = [dict(configuration=c["name"],events=deepcopy(events)) for c in p["configurations"]]
    actual = run.compare(trial,profiles,old,p)
    assert actual["reference_qualified"]
    assert all(len(e["original_comparisons"]) == 4 for e in actual["events"])
    assert audit.agree(actual,audit.scalar_comparison(trial,profiles,old,p))
    profiles[1]["events"][0]["state"][0] = str(D(profiles[1]["events"][0]["state"][0])+D(".01"))
    bad = run.compare(trial,profiles,old,p)
    assert not bad["reference_qualified"] and not bad["repairs_exp498"]
    assert audit.agree(bad,audit.scalar_comparison(trial,profiles,old,p))
    with pytest.raises(ValueError,match="configuration"):
        run.compare(trial,profiles[:1],old,p)
    profiles[0]["events"].pop()
    with pytest.raises(ValueError,match="configuration"):
        run.compare(trial,profiles,old,p)


@pytest.mark.parametrize("kind",["coefficient","missing-step","horizon","initial"])
def test_independent_raw_audit_detects_changes(kind):
    config = analytic.CONFIGS[0]
    field = analytic.polynomial()
    raw = run.taylor.integrate([0,0,1],field,.1,config,analytic.SCALES)
    audit.check_raw(raw,[0,0,1],field,.1,config,analytic.SCALES)
    if kind == "coefficient": raw["steps"][0]["coefficients"][2][2] = "0.7"
    elif kind == "missing-step": raw["steps"].pop()
    elif kind == "horizon": raw["horizon"] = "1"
    else: raw["initial"][0] = "1"
    with pytest.raises(ValueError):
        audit.check_raw(raw,[0,0,1],field,.1,config,analytic.SCALES)


def test_actual_analytic_controls_replay_without_integrations(tmp_path,monkeypatch):
    output = tmp_path/"controls"
    receipt = analytic.controls(output)
    def forbidden(*args,**kwargs): pytest.fail("audit integrated a trajectory")
    monkeypatch.setattr(run.taylor,"integrate",forbidden)
    audit.check_controls(output,receipt)
    bad = deepcopy(receipt)
    bad["profiles"][0]["events"][0]["state"][2] = "0.1"
    with pytest.raises(ValueError): audit.check_controls(output,bad)
