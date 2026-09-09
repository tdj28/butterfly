"""Analytic full side-matrix controls for the saved-trajectory consumer."""
from copy import deepcopy
import json
import numpy as np
import pytest

from butterfly.models import RosslerParameters,rossler_equilibria
from scripts import analyze_exp493_projected_inner_turn as run


@pytest.mark.parametrize("key",["window","angle_ceiling","radius_floor","paired_radius_relative","relative_turn_error","parent_summary_sha256","parent_receipt_sha256"])
def test_prospective_settings_and_parent_anchors_are_immutable(tmp_path,monkeypatch,key):
    p = run.load_plan()
    p[key] = "0"*64 if isinstance(p[key],str) else p[key]*2
    path = tmp_path/"altered-plan.json"
    path.write_text(json.dumps(p))
    monkeypatch.setattr(run,"PLAN",path)
    with pytest.raises(ValueError):
        run.load_plan()


def test_complete_exact_consumer_controls(plan):
    result = run.controls(plan)
    assert result["passed"] and result["analytic_profiles"] == 12 and result["new_integrations"] == 0
    assert all(v["geometry"]["measures"]["midpoint_enriched"]["cut_index"] is None for v in result["origin_negative"])


@pytest.fixture
def plan():
    return dict(window=.05,radius_floor=1e-10,angle_ceiling=2.9,angle_agreement=1e-6,
        paired_angle=1e-6,paired_scaled_endpoint=1e-6,paired_radius_relative=.01,
        relative_turn_error=.01,scales=[15.,15.,.01])


def synthetic_matrix(monkeypatch,p):
    c = dict(parameters=dict(a=.2,b=.2,c=7.),doses=[-2e-5,-2e-6,2e-6,2e-5])
    eq = rossler_equilibria(RosslerParameters(**c["parameters"]))[0]
    monkeypatch.setattr(run,"rossler_rhs",lambda t,q,par:np.array([-1.,-(t-1.),0.]))
    rows = []
    for height in c["doses"]:
        q = lambda t:eq+np.array([-(t-1.),height-.5*(t-1.)**2,13.])
        raw = dict(integration_times=np.array([.9,1.1]),integration_augmented_states=np.column_stack([np.array([q(.9),q(1.1)]),np.zeros((2,3))]))
        events = [dict(time=1+np.sqrt(2*height),accepted=True)] if height > 0 else []
        profiles = [run.profile(raw,dict(method=m,extrema=[dict(time=1.,state=q(1).tolist())],reconstructed=events),c,1.,p) for m in ("DOP853","Radau")]
        rows.append(dict(dose=height,profiles=profiles))
    return c,rows


def test_actual_analytic_consumer_and_complete_matrix(monkeypatch,plan):
    c,rows = synthetic_matrix(monkeypatch,plan)
    a = run.compare(rows,c,plan,True)
    assert a["qualified"] and len(a["paired_profiles"]) == len(a["relative_turns"]) == 4
    assert all(v["extra_cut_index"] == 1 for v in a["relative_turns"])
    assert all(p["minimum_polygon_distance_3d"] >= 13. for r in rows for p in r["profiles"])
    assert all(p["geometry"]["measures"]["raw"]["cut_index"] == 0 for r in rows for p in r["profiles"])


@pytest.mark.parametrize("change",["missing-dose","solver","event-count","angle","radius","endpoint","parent"])
def test_matrix_failures_not_dropped(monkeypatch,plan,change):
    c,rows = synthetic_matrix(monkeypatch,plan)
    parent = True
    if change == "missing-dose":
        rows.pop()
    elif change == "solver":
        rows[0]["profiles"][1]["method"] = "DOP853"
    elif change == "event-count":
        rows[0]["profiles"][0]["local_negative_crossings"] = 1
    elif change == "angle":
        rows[0]["profiles"][0]["geometry"]["measures"]["midpoint_enriched"]["angle_change"] += .1
    elif change == "radius":
        rows[0]["profiles"][0]["geometry"]["measures"]["midpoint_enriched"]["minimum_radius"] *= 2
    elif change == "endpoint":
        rows[0]["profiles"][0]["endpoints"][0][2] += .1
    else:
        parent = False
    if change in ("missing-dose","solver"):
        with pytest.raises(ValueError):
            run.compare(rows,c,plan,parent)
    else:
        assert not run.compare(rows,c,plan,parent)["qualified"]


def test_reported_crossing_is_not_used_to_construct_polygon(monkeypatch,plan):
    c,rows = synthetic_matrix(monkeypatch,plan)
    r = rows[-1]["profiles"][0]
    assert r["geometry"]["measures"]["extrema_augmented"]["cut_index"] == 1
    # A false report cannot turn the measured geometry into an accepted match.
    eq = rossler_equilibria(RosslerParameters(**c["parameters"]))[0]
    q = lambda t:eq+np.array([-(t-1.),2e-5-.5*(t-1.)**2,13.])
    raw = dict(integration_times=np.array([.9,1.1]),integration_augmented_states=np.column_stack([np.array([q(.9),q(1.1)]),np.zeros((2,3))]))
    bad = run.profile(raw,dict(method="DOP853",extrema=[dict(time=1.,state=q(1).tolist())],reconstructed=[]),c,1.,plan)
    assert bad["geometry"]["qualified"] and not bad["event_index_agrees"] and not bad["qualified"]
