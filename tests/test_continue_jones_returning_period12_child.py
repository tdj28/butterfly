import pytest

from scripts.continue_jones_returning_period12_child import SCHEMA, select_seed


def test_returning_child_continuation_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period12-child-continuation-manifest.v1"


def test_select_seed_requires_one_passed_exact_candidate():
    receipt = {
        "events": [
            {
                "c": 1.0,
                "candidates": [
                    {
                        "step_length": 0.5,
                        "source_direction": -1,
                        "candidate_a": 2.0,
                        "passed": True,
                    }
                ],
            }
        ]
    }
    selector = {"c": 1.0, "step_length": 0.5, "source_direction": -1, "candidate_a": 2.0}
    _, candidate = select_seed(receipt, selector)
    assert candidate["passed"]
    selector["candidate_a"] = 3.0
    with pytest.raises(ValueError):
        select_seed(receipt, selector)
