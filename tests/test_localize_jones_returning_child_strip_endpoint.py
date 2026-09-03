from scripts.localize_jones_returning_child_strip_endpoint import (
    SCHEMA,
    double_cover_passes,
)


def test_returning_child_endpoint_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-child-strip-endpoint-manifest.v1"


def test_double_cover_requires_stable_parent_and_half_period_collapse():
    row = {
        "checks": {
            "closure": True,
            "child_stable": True,
            "period_ratio": True,
            "section_identity": True,
            "parent_unstable": False,
            "proper_subperiod": False,
        }
    }
    metrics = {
        "parent_multiplier_modulus": 0.99,
        "parent_child_state_distance": 1e-6,
        "child_half_period_closure": 1e-6,
        "period_ratio_error": 1e-10,
        "multiplier_square_error": 1e-6,
    }
    acceptance = {
        "maximum_right_parent_multiplier_modulus": 0.9999,
        "maximum_double_cover_state_distance": 1e-4,
        "maximum_double_cover_half_period_closure": 1e-4,
        "maximum_period_ratio_error": 5e-4,
        "maximum_multiplier_square_error": 1e-4,
    }
    assert double_cover_passes(row, metrics, acceptance)
    row["checks"]["proper_subperiod"] = True
    assert not double_cover_passes(row, metrics, acceptance)
