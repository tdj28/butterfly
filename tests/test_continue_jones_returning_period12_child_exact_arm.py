from scripts.continue_jones_returning_period12_child_exact_arm import (
    SCHEMA,
    event_manifest,
)


def test_returning_child_exact_arm_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period12-child-exact-arm-manifest.v1"


def test_event_manifest_isolates_event_acceptance():
    manifest = {
        "fixed_b": 0.2,
        "acceptance": {"maximum_closure_error": 1.0},
        "event_correction": {
            "a_guard": [0.23, 0.26],
            "corrector": {"tolerance": 1e-10},
            "acceptance": {"maximum_orbit_residual": 1e-8},
        },
    }
    result = event_manifest(manifest)
    assert result["acceptance"] == {"maximum_orbit_residual": 1e-8}
    assert result["a_guard"] == [0.23, 0.26]
