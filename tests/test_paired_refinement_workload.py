"""Frozen full-horizon expectations and conservative projection, without a run."""
from types import SimpleNamespace

import numpy as np
import pytest

from scripts.benchmark_paired_refinement import (
    BATCH, HORIZON, PERIOD, STEPS, check_circle, estimates, protocol,
)


def exact_result():
    initial = np.array([[-1.,0.,.02],[-2.,0.,.03]])
    final = initial.copy()
    final[:,0] *= np.cos(2*np.pi*HORIZON/PERIOD)
    final[:,1] = initial[:,0]*np.sin(2*np.pi*HORIZON/PERIOD)
    events = {}
    for i, name in enumerate(("historical", "barrio")):
        events[name] = dict(seed_ids=np.repeat(np.arange(2),146),
            times=np.tile((np.arange(146)+(1 if i==0 else .5))*PERIOD/2,2),
            accepted=np.tile(np.arange(146)%2==1,2))
    return SimpleNamespace(status="completed",final_states=final,failed=np.zeros(2,bool),
        ambiguous=np.zeros((2,2),bool),capture_times=np.full((2,2),np.nan),events=events),initial


def test_exact_circle_and_event_order_control():
    result, initial = exact_result()
    assert check_circle(result, initial)["passed"]
    for events in result.events.values():
        for key in events: events[key] = events[key][::-1]
    assert check_circle(result, initial)["passed"]


@pytest.mark.parametrize("fault",["state","times","accepted","capture","ambiguity","failed","status"])
def test_corrupted_analytic_expectations_fail(fault):
    result, initial = exact_result()
    if fault == "state": result.final_states[0,0] += .01
    elif fault == "times": result.events["historical"]["times"][0] += .01
    elif fault == "accepted": result.events["historical"]["accepted"][0] = True
    elif fault == "capture": result.capture_times[0,0] = 1.
    elif fault == "ambiguity": result.ambiguous[0,0] = True
    elif fault == "failed": result.failed[0] = True
    else: result.status = "incomplete"
    with pytest.raises(ValueError): check_circle(result,initial)


def test_declared_workload_matches_step_and_event_caps():
    p = protocol()
    assert [round(HORIZON/dt) for dt in STEPS] == [120000,240000]
    assert 2*146*BATCH < p["maximum_events_per_batch"]
    assert p["full_analysis_bootstrap_samples"] == 200
    assert not p["target_execution_authorized"]


def test_estimate_counts_all_cases_profiles_and_headroom():
    collection = [dict(seconds=10.,bytes=1000,files=10,replay_seconds=1.,peak_rss_bytes=1000)]*2
    q = dict(seconds=1.,bytes=1000)
    analysis = dict(seconds=10.,bytes=1000,peak_rss_bytes=1000)
    value = estimates(collection,q,analysis,dict(seconds=0.,files=20))
    assert value["collection_seconds"] == 1280.
    assert value["analysis_seconds"] == 148.
    assert value["qualification_seconds"] == 32.
    assert value["projected_collection_files"] == 640
    assert value["fits_limits"]
    saturated = estimates(collection,q,analysis,dict(seconds=1.,files=20))
    assert saturated["collection_seconds"] is None
    assert not saturated["fits_limits"]
