import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "qualify_sprinkler_convergence.py"
SPEC = importlib.util.spec_from_file_location("sprinkler_qualification", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _run(branch_count, *, resolved=True):
    robust = {"resolved": resolved, "branch_count": branch_count}
    return {
        "coordinates": {
            "y": {"robust_oracle": dict(robust)},
            "z": {"robust_oracle": dict(robust)},
        }
    }


def _case(a, observed, expected=None, *, passed=True):
    return {
        "parameters": {"a": a},
        "observed_saddle_branch_count": observed,
        "expected_saddle_branch_count": expected,
        "passed": passed,
    }


def test_observed_branch_count_requires_complete_consensus():
    coordinates = [{"name": "y"}, {"name": "z"}]
    assert MODULE._observed_branch_count([_run(2), _run(2)], coordinates, {2, 3}) == 2

    disagreement = _run(2)
    disagreement["coordinates"]["z"]["robust_oracle"]["branch_count"] = 3
    assert MODULE._observed_branch_count([disagreement], coordinates, {2, 3}) is None
    assert MODULE._observed_branch_count([_run(2, resolved=False)], coordinates, {2, 3}) is None


def test_path_evaluation_accepts_one_blind_ordered_transition():
    cases = [
        _case(0.118, 2, 2),
        _case(0.120, 2),
        _case(0.140, 3),
        _case(0.145, 3),
        _case(0.149, 3, 3),
    ]
    manifest = {
        "path_acceptance": {
            "required_observed_counts": [2, 3],
            "required_transition_count": 1,
        }
    }
    result = MODULE._path_evaluation(cases, manifest)
    assert result["passed"]
    assert result["transitions"] == [
        {
            "lower_a": 0.12,
            "upper_a": 0.14,
            "lower_branch_count": 2,
            "upper_branch_count": 3,
        }
    ]


def test_path_evaluation_rejects_nonmonotone_labels():
    cases = [
        _case(0.118, 2, 2),
        _case(0.120, 3),
        _case(0.140, 2),
        _case(0.149, 3, 3),
    ]
    manifest = {
        "path_acceptance": {
            "required_observed_counts": [2, 3],
            "required_transition_count": 1,
        }
    }
    result = MODULE._path_evaluation(cases, manifest)
    assert not result["passed"]
    assert not result["nondecreasing"]
