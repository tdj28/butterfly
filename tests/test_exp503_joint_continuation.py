"""Outcome-free tests of resource continuation, not new scientific results."""
from copy import deepcopy
import json

import pytest
from scripts import run_exp503_joint_continuation as run


def ledger(count=6):
    specs = run.base.response.stencil(dict(a=.2,b=.2,c=7.))
    slots = [dict(spec=s,status="completed" if i < count else "started" if i == count else "not-run")
             for i,s in enumerate(specs)]+[dict(spec=None,status="not-run",role="proposal")]
    return specs,slots


@pytest.mark.parametrize("count",[6,7,8])
def test_reuses_every_completed_prefix_slot(count):
    specs,slots = ledger(count)
    before = deepcopy(slots)
    assert run.prefix(slots,specs) == count
    assert slots == before  # No resetting interrupted/completed attempts.


@pytest.mark.parametrize("kind",["short","hole","favorable-subset","wrong-parameter","early-proposal","multiple-started","unknown-status"])
def test_incomplete_or_selected_checkpoint_rejected(kind):
    specs,slots = ledger(6)
    if kind == "short":
        specs,slots = ledger(5)
    elif kind == "hole":
        slots[4]["status"] = "not-run"
    elif kind == "favorable-subset":
        slots[7]["status"] = "completed"
    elif kind == "wrong-parameter":
        slots[0] = deepcopy(slots[0])
        slots[0]["spec"]["parameters"]["a"] += .1
    elif kind == "early-proposal":
        slots[-1]["status"] = "started"
    elif kind == "multiple-started":
        slots[7]["status"] = "started"
    else:
        slots[6]["status"] = "discarded"
    with pytest.raises(ValueError):
        run.prefix(slots,specs)


def test_resource_plan_round_trip_and_tamper_rejection(tmp_path,monkeypatch):
    monkeypatch.setattr(run,"original_metadata",lambda path:dict(completed_prefix=6,reserved_ivps=1100))
    p = run.expected(tmp_path)
    p["source_paths"] = sorted(set(run.EXPLICIT)|set(run.base.load()["source_paths"]))
    path = tmp_path/"plan.json"
    run.write_json(path,p)
    monkeypatch.setattr(run,"PLAN",path)
    assert run.load(tmp_path) == p
    bad = deepcopy(p)
    bad["limits"]["minimum_free_bytes"] = 0
    changed = tmp_path/"changed.json"
    run.write_json(changed,bad)
    monkeypatch.setattr(run,"PLAN",changed)
    with pytest.raises(ValueError):
        run.load(tmp_path)


def test_running_original_is_not_recoverable(tmp_path):
    # No archived failure: the continuation cannot race the original worker.
    with pytest.raises(FileNotFoundError):
        run.original_metadata(tmp_path)


def test_original_numerics_remain_pinned():
    assert run.sha256(run.base.PLAN) == run.BASE_SHA
    p = run.base.load()
    assert p["primary_radius"] == 1e-4
    assert p["limits"]["output_bytes"] == 8*1024**3
    assert p["limits"]["minimum_free_bytes"] == 8*1024**3
    assert len(p["base_vectors"]) == 256


def campaign_fixture(count=6):
    anchor,vectors,points = run.prior_audit.synthetic()
    specs = [r["spec"] for r in points]
    slots = [dict(spec=s,status="completed" if i < count else "started" if i == count else "not-run")
             for i,s in enumerate(specs)]+[dict(spec=None,status="not-run",role="proposal")]
    p = dict(original=dict(completed_prefix=count,slots=slots))
    numerical = dict(stencil=specs,anchor=anchor,base_vectors=vectors)
    progress = [dict(spec=s,provenance="original" if i < count else "continuation",status="not-run")
                for i,s in enumerate(specs)]+[dict(spec=None,provenance=None,status="not-run",role="proposal")]
    return p,numerical,points,progress


def test_remaining_points_then_exactly_one_proposal():
    p,numerical,points,progress = campaign_fixture()
    fetched,measured,events = [],[],[]
    by_id = {r["spec"]["id"]:r for r in points}
    def fetch(spec):
        fetched.append(spec["id"])
        return by_id[spec["id"]]
    def measure(spec):
        measured.append(spec["id"])
        events.append(spec["id"])
        return by_id.get(spec["id"],dict(spec=spec,qualified=True,vectors=[],joint_proximity=False))
    rows,matrix,proposal = run.remaining(p,numerical,fetch,measure,progress,
        response_ready=lambda result:events.append("response-saved"))
    assert fetched == [r["spec"]["id"] for r in points[:6]]
    assert measured == [r["spec"]["id"] for r in points[6:]]+["joint-proposal"]
    assert events[-2:] == ["response-saved","joint-proposal"]
    assert len(rows) == 8 and matrix["qualified"] and proposal["spec"] == matrix["proposal"]
    assert all(r["status"] == "completed" for r in progress)


def test_failed_reused_point_still_runs_every_remaining_stencil():
    p,numerical,points,progress = campaign_fixture()
    points[0]["qualified"] = False
    measured = []
    by_id = {r["spec"]["id"]:r for r in points}
    def measure(spec):
        measured.append(spec["id"])
        return by_id[spec["id"]]
    rows,matrix,proposal = run.remaining(p,numerical,lambda s:by_id[s["id"]],measure,progress)
    assert len(rows) == 8 and measured == [r["spec"]["id"] for r in points[6:]]
    assert not matrix["qualified"] and proposal is None and progress[-1]["status"] == "not-run"


def test_resource_interruption_keeps_unfinished_slots_explicit():
    p,numerical,points,progress = campaign_fixture()
    by_id = {r["spec"]["id"]:r for r in points}
    def stop(spec):
        raise run.base.previous.cycles_run.BudgetStop("synthetic storage cap")
    with pytest.raises(run.base.previous.cycles_run.BudgetStop):
        run.remaining(p,numerical,lambda s:by_id[s["id"]],stop,progress)
    assert [r["status"] for r in progress] == ["completed"]*6+["started","not-run","not-run"]


def test_completed_original_proposal_is_reused_and_never_changed():
    p,numerical,points,progress = campaign_fixture(8)
    matrix = run.base.response.response(points,numerical["base_vectors"],numerical["anchor"])
    p["original"]["slots"][-1].update(status="completed",spec=matrix["proposal"])
    proposal = dict(spec=matrix["proposal"])
    by_id = {r["spec"]["id"]:r for r in points}|{"joint-proposal":proposal}
    def forbidden(spec):
        pytest.fail("complete original evidence was regenerated")
    rows,result,reused = run.remaining(p,numerical,lambda s:by_id[s["id"]],forbidden,progress)
    assert reused is proposal and progress[-1]["provenance"] == "original"
    p["original"]["slots"][-1]["spec"] = dict(id="different",parameters=matrix["proposal"]["parameters"])
    with pytest.raises(ValueError):
        run.remaining(p,numerical,lambda s:by_id[s["id"]],forbidden,progress)
