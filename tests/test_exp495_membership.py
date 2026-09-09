"""Synthetic saved-state contracts; no target cross-artifact measurements."""
from copy import deepcopy
import json

import numpy as np
import pytest

from scripts import analyze_exp495_fold_cycle_membership as run
from scripts import audit_exp495_fold_cycle_membership as audit


def fixture():
    p = json.loads(run.PLAN.read_bytes())
    events = [[float(j), 0., float(j)*.001] for j in range(6)]
    candidates, folds, bases = [], [], []
    for case, a in zip(p["cases"], [.21575, .21577], strict=True):
        parameters = dict(a=a, b=.2, c=7.212)
        profiles = []
        for method in p["methods"]:
            windows = [dict(phase=phase, qualified=True, conditional_minimal_period=True,
                counts=dict(historical=6, barrio=8), event_states=dict(historical=deepcopy(events)),
                event_phases=dict(historical=[j/6+.01 for j in range(6)])) for phase in p["phases"]]
            profiles.append(dict(method=method, qualified=True,
                metric=dict(qualified=True, repeat=dict(passed=True), windows=windows)))
        bases.append(dict(spec=dict(case=case, arm="base", step=0, parameters=parameters),
                          status="qualified", pair=dict(passed=True), profiles=profiles))
        for identity in [v for v in run.expected_ids() if v.startswith(case)]:
            region = int(identity.split("--region-")[1][0])
            family = identity.rsplit("--candidate-", 1)[0]
            candidates.append(dict(id=identity, case=case, region=region, family_id=family, parameters=parameters))
            solvers = []
            for method in p["methods"]:
                row = dict(method=method, qualified=bool(region), reason=None if region else "synthetic failure")
                if region:
                    row.update(in_region=True, observations=[None,
                        dict(image_state=deepcopy(events[2]), next_state=deepcopy(events[3])), None])
                solvers.append(row)
            folds.append(dict(id=identity, case=case, family_id=family, region=region,
                              qualified=bool(region), qualified_in_region=bool(region), solvers=solvers))
    cycles = dict(experiment_id="EXP-494", status="complete-ledger", symbolic_chains_verified=False,
                  rows=bases+[dict(spec=dict(arm="not-selected")) for _ in range(64)])
    return candidates, dict(experiment_id="EXP-490", status="completed-audited", candidates=folds), cycles, p


def test_full_matrix_separate_scalar_replay_and_all_failures_preserved():
    data = fixture()
    result = run.analyze(*data)
    assert result == audit.reconstruct(*data)
    assert len(result["rows"]) == 26
    assert all(c["status"] == "proximate-at-primary-radius" for c in result["cases"])
    assert all(r["envelope"] is None and not r["variants"] for r in result["rows"] if r["region"] == 0)


def test_wrong_successor_cannot_be_rescued_by_independent_nearest_neighbors():
    c, f, s, p = fixture()
    for row in f["candidates"]:
        if row["qualified"]:
            for v in row["solvers"]:
                v["observations"][1]["next_state"] = [4., 0., .004]
    result = run.analyze(c, f, s, p)
    assert all(row["status"] == "not-proximate-at-primary-radius" for row in result["cases"])
    assert result == audit.reconstruct(c, f, s, p)


def test_x_match_does_not_hide_z_separation():
    c, f, s, p = fixture()
    for row in f["candidates"]:
        if row["qualified"]:
            for v in row["solvers"]:
                v["observations"][1]["image_state"][2] += 2e-6
    result = run.analyze(c, f, s, p)
    for row in result["cases"]:
        assert row["envelope"]["minimum_x_distance"] == 0
        assert row["status"] == "not-proximate-at-primary-radius"


def test_cyclic_wrap_and_exact_boundary():
    events = [[float(j), 0., 0.] for j in range(6)]
    r = run.pair_distances(events[-1], [0., 0., 1e-6], events, [15., 15., .01])
    e = run.envelope([r], [1e-4])
    assert e["radii"][0]["state_indices"] == [5]
    r = run.pair_distances(events[-1], [0., 0., 1.00001e-6], events, [15., 15., .01])
    assert run.envelope([r], [1e-4])["radii"][0]["state_indices"] == []


def test_one_bad_solver_or_window_blocks_joint_proximity():
    c, f, s, p = fixture()
    s["rows"][0]["profiles"][1]["metric"]["windows"][1]["event_states"]["historical"][2][2] += .00001
    result = run.analyze(c, f, s, p)
    assert result["cases"][0]["status"] == "not-proximate-at-primary-radius"
    assert result["cases"][1]["status"] == "proximate-at-primary-radius"


def test_missing_family_is_incomplete_not_zero_or_success():
    c, f, s, p = fixture()
    family = "local-a025-c083--region-1--depth-4--direction-0"
    for row in f["candidates"]:
        if row["family_id"] == family:
            row["qualified_in_region"] = False
    result = run.analyze(c, f, s, p)
    assert result["cases"][0]["status"] == "incomplete-fold-representation"
    with pytest.raises(ValueError, match="empty"):
        run.envelope([], [1e-4])


@pytest.mark.parametrize("mutation", ["missing-candidate", "duplicate-candidate", "missing-method",
    "missing-window", "missing-event", "nonprimitive", "parameter", "nonfinite"])
def test_bad_input_contract_fails(mutation):
    c, f, s, p = fixture()
    profile = s["rows"][0]["profiles"][0]
    if mutation == "missing-candidate":
        f["candidates"].pop()
    elif mutation == "duplicate-candidate":
        f["candidates"][-1] = deepcopy(f["candidates"][-2])
    elif mutation == "missing-method":
        s["rows"][0]["profiles"].pop()
    elif mutation == "missing-window":
        profile["metric"]["windows"].pop()
    elif mutation == "missing-event":
        profile["metric"]["windows"][0]["event_states"]["historical"].pop()
    elif mutation == "nonprimitive":
        profile["metric"]["windows"][0]["conditional_minimal_period"] = False
    elif mutation == "parameter":
        c[0]["parameters"] = dict(a=.21576, b=.2, c=7.212)
    else:
        profile["metric"]["windows"][0]["event_states"]["historical"][0][0] = np.nan
    with pytest.raises(ValueError):
        run.analyze(c, f, s, p)


def test_scalar_audit_rejects_rehashed_semantic_distance_tampering():
    data = fixture()
    result = run.analyze(*data)
    selected = next(r for r in result["rows"] if r["variants"])
    selected["variants"][0]["pair_state_distance"][2] = 10.
    with pytest.raises(ValueError, match="scalar"):
        audit.check_result(result, *data)


def test_default_preflight_does_not_call_distance_function(monkeypatch, capsys):
    p = json.loads(run.PLAN.read_bytes())
    monkeypatch.setattr(run, "load_inputs", lambda: (p, [None]*26, None, None))
    monkeypatch.setattr(run, "analyze", lambda *_: pytest.fail("preflight opened distances"))
    monkeypatch.setattr("sys.argv", ["analysis"])
    run.main()
    assert json.loads(capsys.readouterr().out)["new_distances_measured"] is False


def test_real_public_input_preflight_opens_no_cross_artifact_distances(monkeypatch):
    monkeypatch.setattr(run, "pair_distances", lambda *_: pytest.fail("input check measured outcome"))
    p, c, _, _ = run.load_inputs()
    assert len(c) == p["fold_candidates"] == 26


def test_execute_writes_exclusive_attempt_and_rejects_second_call(tmp_path, monkeypatch):
    c, f, s, p = fixture()
    frozen = "a"*40
    reference = "refs/heads/synthetic"
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setattr(run, "SOURCES", [])
    monkeypatch.setattr(run, "load_inputs", lambda: (p, c, f, s))
    def git(args, **_):
        return frozen if args[1] == "rev-parse" else ("" if args[1] == "status" else frozen+"\t"+reference)
    monkeypatch.setattr(run.subprocess, "check_output", git)
    run.execute(tmp_path/"first", frozen, reference)
    original = (tmp_path/"artifacts/EXP-495/analysis-once.json").read_bytes()
    assert json.loads((tmp_path/"first/result.json").read_bytes())["new_integrations"] == 0
    with pytest.raises(FileExistsError):
        run.execute(tmp_path/"second", frozen, reference)
    assert (tmp_path/"artifacts/EXP-495/analysis-once.json").read_bytes() == original
    assert not (tmp_path/"second/result.json").exists()


def test_public_replay_requires_no_local_attempt_files(tmp_path, monkeypatch):
    c, f, s, p = fixture()
    result = run.analyze(c, f, s, p)
    result.update(binding=dict(sources={}, inputs=p["inputs"], plan_sha256=run.sha256(run.PLAN),
                              started_utc="2026-09-09T00:00:00+00:00", source_commit="a"*40),
                  completed_utc="2026-09-09T00:01:00+00:00")
    path = tmp_path/"public.json"
    run.write(path, result)
    monkeypatch.setattr(run, "SOURCES", [])
    monkeypatch.setattr(run, "load_inputs", lambda: (p, c, f, s))
    r = audit.audit(path, run.sha256(path), public=True)
    assert r["passed"] and not r["local_attempt_witness_checked"]
    with pytest.raises(FileNotFoundError):
        audit.audit(path, run.sha256(path))
