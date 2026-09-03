from scripts.continue_jones_returning_period12_child_adaptive import (
    SCHEMA,
    step_is_acceptable,
)


def test_adaptive_returning_child_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period12-child-adaptive-manifest.v1"


def test_step_acceptance_requires_science_and_coherence():
    assert step_is_acceptable({"passed": True}, 0.002, 0.003)
    assert not step_is_acceptable({"passed": False}, 0.002, 0.003)
    assert not step_is_acceptable({"passed": True}, 0.004, 0.003)
    assert not step_is_acceptable({"passed": True}, float("nan"), 0.003)
