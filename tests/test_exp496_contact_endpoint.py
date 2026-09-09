"""Prospective selection, arithmetic, phase, source and tamper regression gates."""
from copy import deepcopy
import json

import numpy as np
import pytest
from scripts import run_exp496_contact_endpoint as run
from scripts import audit_exp496_contact_endpoint as audit


@pytest.fixture(scope="module")
def inputs():
    return run.load_inputs()


def test_complete_selection_and_exact_section(inputs):
    p, data, folds, cycles = inputs
    assert len(data["ledger"]) == 26
    assert len(data["candidates"]) == 8
    assert sum(r["status"] == "not-evaluated-parent-ineligible" for r in data["ledger"]) == 16
    assert sum(r["status"] == "not-selected-duplicate-representation" for r in data["ledger"]) == 2
    parent = run.membership.load_inputs()[1]
    for c in data["candidates"]:
        old = next(r for r in parent if r["id"] == c["id"])
        f = next(r for r in folds["candidates"] if r["id"] == c["id"])
        assert c["initial_state"][::2] == old["initial_state"][::2]
        assert c["initial_tangent"] == old["initial_tangent"]
        assert c["initial_state"][1] == run.legacy_rossler_section(run.RosslerParameters(**c["parameters"])).offset
        assert c["parameters"] == run.cycle_node(cycles, c["case"], True)["spec"]["parameters"]
        assert c["seed_u"] == float(np.mean([s["root"]["u"] for s in f["solvers"]]))
        assert c["seed_time"] == float(np.mean([s["root"]["time"] for s in f["solvers"]]))
        assert c["u_box"] == [c["seed_u"]-.02, c["seed_u"]+.02]
        assert c["old_x_interval"] == old["old_x_interval"]
    assert p["max_step"] == .001
    assert p["limits"]["max_target_trajectories"] == 176


@pytest.mark.parametrize("mutation", ["primitive", "repeat", "correction", "phase", "pair", "order", "finite"])
def test_reject_changed_cycle_gates(inputs, mutation):
    cycles = deepcopy(inputs[3])
    r = next(r for r in cycles["rows"] if r["spec"]["arm"] == "a-" and r["spec"]["step"] == 3)
    p = r["profiles"][0]
    w = p["metric"]["windows"][0]
    if mutation == "primitive": w["conditional_minimal_period"] = False
    if mutation == "repeat": p["metric"]["repeat"]["passed"] = False
    if mutation == "correction": p["correction_gate"]["passed"] = False
    if mutation == "phase": w["phase"] = .5
    if mutation == "pair": r["pair"]["passed"] = False
    if mutation == "order": w["event_phases"]["historical"].reverse()
    if mutation == "finite": w["event_states"]["historical"][3][0] = float("nan")
    with pytest.raises(ValueError): run.cycle_node(cycles, r["spec"]["case"], True)


def synthetic_results(inputs, mode):
    p, data, folds, cycles = inputs
    results = [deepcopy(next(f for f in folds["candidates"] if f["id"] == c["id"])) for c in data["candidates"]]
    for c, r in zip(data["candidates"], results, strict=True):
        node = run.cycle_node(cycles, c["case"], True)
        for i, s in enumerate(r["solvers"]):
            events = node["profiles"][i]["metric"]["windows"][0]["event_states"]["historical"]
            o = s["observations"][1]
            o["image_state"], o["next_state"] = deepcopy(events[3]), deepcopy(events[4])
            if mode != "near": o["image_state"][0] += (.03 if mode == "opposite" else -.03)
    return results


@pytest.mark.parametrize("mode,status", [("near", "endpoint-proximate"),
    ("opposite", "opposite-sign-endpoints"), ("same", "no-qualified-bracket")])
def test_independent_scalar_contact_and_fixed_ordinal(inputs, mode, status):
    p, data, folds, cycles = inputs
    results = synthetic_results(inputs, mode)
    expected = audit.reconstruct_contact(results, data, folds, cycles, p)
    actual = run.contact_analysis(results, data, folds, cycles, p)
    assert actual == expected
    assert all(r["status"] == status for r in actual["rows"])
    assert sum(len(r["variants"])*6 for r in actual["rows"]) == 192
    assert not actual["symbolic_chains_verified"]


def test_mixed_failures_not_cherry_picked(inputs):
    p, data, folds, cycles = inputs
    results = synthetic_results(inputs, "opposite")
    results[0]["qualified_in_region"] = False
    value = run.contact_analysis(results, data, folds, cycles, p)
    assert value == audit.reconstruct_contact(results, data, folds, cycles, p)
    assert value["rows"][0]["status"] == "unresolved-fold"
    assert value["rows"][0]["variants"] == []
    assert value["cases"][0]["status"] == "mixed-representation-results"
    with pytest.raises(ValueError): run.contact_analysis(results[:-1], data, folds, cycles, p)


def test_one_disagreeing_variant_prevents_bracket(inputs):
    p = inputs[0]
    variants = [dict(pair_state_distance=[.002]*6, opposite_sign_resolved=True) for _ in range(4)]
    variants[0]["opposite_sign_resolved"] = False
    # A different nearby event cannot rescue fixed event 3.
    for v in variants: v["pair_state_distance"][0] = 0
    assert run.representation_status(variants, p) == "no-qualified-bracket"
    with pytest.raises(ValueError): run.representation_status([], p)


def test_input_hash_and_source_closure_tampering(inputs, tmp_path, monkeypatch):
    plan = deepcopy(inputs[0])
    path = tmp_path/"plan.json"
    plan["candidates_sha256"] = "0"*64
    path.write_text(json.dumps(plan))
    monkeypatch.setattr(run, "PLAN", path)
    with pytest.raises(ValueError, match="frozen"): run.load_inputs()
    plan["candidates_sha256"] = inputs[0]["candidates_sha256"]
    plan["source_paths"].remove("scripts/audit_exp496_contact_endpoint.py")
    path.write_text(json.dumps(plan))
    with pytest.raises(ValueError, match="frozen"): run.load_inputs()


def test_raw_audit_rejects_anchor_before_decisions(tmp_path):
    path = tmp_path/"summary.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="anchor"):
        audit.audit(tmp_path, "0"*64)
