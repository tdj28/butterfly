from copy import deepcopy

import numpy as np
import pytest

from scripts.qualify_symbolic_gpu_records import compare_records
from scripts import qualify_symbolic_gpu_records as qualification


def fixture_pair():
    cpu = {"records": [{"seed_id": 2, "times": [1.0, 2.0],
                         "states": [[0.0, -1.0, 0.1], [0.0, -2.0, 0.2]]}],
           "survivor_counts": [1, 1], "failed_count": 0}
    gpu = {"records": [{"seed_ids": np.array([2]),
                        "times": [np.array([1.0, 2.0])],
                        "states": [np.array([[0.0, -1.0, 0.1], [0.0, -2.0, 0.2]])]}],
           "survivor_counts": np.array([[1, 1]]), "failed_counts": np.array([0])}
    return cpu, gpu


def test_identical_records_pass():
    cpu, gpu = fixture_pair()
    assert compare_records(cpu, gpu)["passed"]


@pytest.mark.parametrize("mutation", ["seed", "count", "failure", "state", "time", "nan", "length"])
def test_parity_fails_closed(mutation):
    cpu, gpu = fixture_pair()
    gpu = deepcopy(gpu)
    if mutation == "seed":
        gpu["records"][0]["seed_ids"][0] = 4
    elif mutation == "count":
        gpu["survivor_counts"][0, 0] = 2
    elif mutation == "failure":
        gpu["failed_counts"][0] = 1
    elif mutation == "state":
        gpu["records"][0]["states"][0][0, 1] += 1e-4
    elif mutation == "time":
        gpu["records"][0]["times"][0][0] += 1e-4
    elif mutation == "nan":
        gpu["records"][0]["states"][0][0, 1] = np.nan
    else:
        gpu["records"][0]["times"][0] = np.array([1.0])
    assert not compare_records(cpu, gpu)["passed"]


def test_no_record_is_not_positive_parity():
    cpu, gpu = fixture_pair()
    cpu["records"][0].update(times=[], states=[])
    gpu["records"][0].update(times=[np.empty(0)], states=[np.empty((0, 3))])
    assert not compare_records(cpu, gpu)["passed"]


def test_capacity_equality_is_conservatively_rejected():
    cpu, gpu = fixture_pair()
    states = np.tile([0.0, -1.0, 0.1], (32, 1))
    times = np.arange(32, dtype=float)
    cpu["records"][0].update(times=times.tolist(), states=states.tolist())
    gpu["records"][0].update(times=[times], states=[states])
    assert not compare_records(cpu, gpu)["passed"]


@pytest.mark.parametrize("mutation", ["missing_times", "extra_states", "extra_candidate", "broadcast_states",
                                     "scalar_times", "fractional_failures", "duplicate_ids", "negative_counts"])
def test_record_shapes_cannot_be_silently_truncated_or_broadcast(mutation):
    cpu, gpu = fixture_pair()
    if mutation == "missing_times":
        cpu["records"].append({**deepcopy(cpu["records"][0]), "seed_id": 3})
        cpu["survivor_counts"] = [2, 2]
        gpu["records"][0]["seed_ids"] = np.array([2, 3])
        gpu["records"][0]["states"].append(deepcopy(gpu["records"][0]["states"][0]))
        gpu["survivor_counts"] = np.array([[2, 2]])
    elif mutation == "extra_states":
        gpu["records"][0]["states"].append(np.ones((2, 3)))
    elif mutation == "extra_candidate":
        gpu["records"].append(deepcopy(gpu["records"][0]))
    elif mutation == "broadcast_states":
        cpu["records"][0]["states"] = [[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]
        gpu["records"][0]["states"][0] = np.array([[1.0], [2.0]])
    elif mutation == "scalar_times":
        gpu["records"][0]["times"][0] = np.array(1.0)
    elif mutation == "fractional_failures":
        gpu["failed_counts"] = np.array([0.1])
    elif mutation == "duplicate_ids":
        cpu["records"].append(deepcopy(cpu["records"][0]))
        cpu["survivor_counts"] = [2, 2]
        gpu["records"][0]["seed_ids"] = np.array([2, 2])
        gpu["records"][0]["states"] *= 2
        gpu["records"][0]["times"] *= 2
        gpu["survivor_counts"] = np.array([[2, 2]])
    else:
        cpu["survivor_counts"][0] = -1
        gpu["survivor_counts"][0, 0] = -1
    result = compare_records(cpu, gpu)
    assert not result["passed"] and not result["checks"]["structure"]


@pytest.fixture
def synthetic_control():
    parent = qualification.parent_design()
    config = deepcopy(parent)
    config["ensemble"].update(x_count=8, z_count=8)
    row, _ = fixture_pair()
    candidate = {"parameters": parent["anchor"]["parameters"],
                 "section_states": np.tile([0.0, -1.0, 0.1], (8, 1)).tolist()}
    return {"candidate": candidate, "config": config,
            "profiles": [{**deepcopy(row), "dt": profile["dt"]} for profile in parent["profiles"]]}


@pytest.mark.parametrize("mutation", ["empty_profiles", "one_profile", "different_step", "different_config", "different_anchor"])
def test_deployment_control_requires_complete_frozen_inputs(synthetic_control, monkeypatch, mutation):
    if mutation == "empty_profiles":
        synthetic_control["profiles"] = []
    elif mutation == "one_profile":
        synthetic_control["profiles"].pop()
    elif mutation == "different_step":
        synthetic_control["profiles"][0]["dt"] = 0.02
    elif mutation == "different_config":
        synthetic_control["config"]["ensemble"]["x_count"] = 4
    else:
        synthetic_control["candidate"]["parameters"] = {"a": 0.1, "b": 0.2, "c": 7.6}
    monkeypatch.setattr(qualification, "integrate", lambda *args: pytest.fail("invalid control must not launch GPU"))
    with pytest.raises(ValueError):
        qualification.gpu_control(synthetic_control)


def test_projection_uses_full_call_and_raw_preservation_wall_time(synthetic_control, monkeypatch):
    _, gpu = fixture_pair()
    monkeypatch.setattr(qualification, "integrate", lambda *args: deepcopy(gpu))
    benchmark_calls = []

    def benchmark(candidates, **kwargs):
        benchmark_calls.append((len(candidates), kwargs["dt"]))
        return {"failed_counts": np.zeros(8, dtype=int), "elapsed_seconds": 1e-9}

    monkeypatch.setattr(qualification, "integrate_gpu", benchmark)
    saved = []

    def preserve(*args, **kwargs):
        saved.append(True)
        return {"validity_passed": True, "raw": {"bytes": 100}}

    monkeypatch.setattr(qualification, "archive_raw", preserve)
    times = iter([0.0, 2.0, 3.0, 10.0, 12.0, 14.0])
    monkeypatch.setattr(qualification.time, "perf_counter", lambda: next(times))
    result = qualification.gpu_control(synthetic_control)
    assert result["passed"]
    assert benchmark_calls == [(8, 0.005), (8, 0.005)]
    assert len(saved) == 2
    assert result["benchmark"]["batch_eight_seconds"] == [3.0, 4.0]
    assert result["benchmark"]["projected_collection_seconds_with_margin"] == 4.0 * 69 * 1.5 * 2
    assert result["benchmark"]["components"][1]["raw_preservation_wall_seconds"] == 2.0


def test_parity_failure_does_not_launch_large_timing_batch(synthetic_control, monkeypatch):
    _, gpu = fixture_pair()
    gpu["failed_counts"][0] = 1
    monkeypatch.setattr(qualification, "integrate", lambda *args: gpu)
    monkeypatch.setattr(qualification, "integrate_gpu", lambda *args, **kwargs: pytest.fail("failed parity must stop"))
    result = qualification.gpu_control(synthetic_control)
    assert not result["passed"] and result["benchmark"] is None
