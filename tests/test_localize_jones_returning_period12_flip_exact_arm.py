from scripts.localize_jones_returning_period12_flip_exact_arm import (
    SCHEMA,
    root_row_passes,
)


def test_returning_period12_flip_exact_arm_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period12-flip-exact-arm-manifest.v1"


def test_root_gate_does_not_require_stable_child():
    row = {
        "checks": {
            "closure": True,
            "parent_unstable": True,
            "child_stable": False,
            "period_ratio": True,
            "proper_subperiod": True,
            "section_identity": True,
        },
        "child": {
            "dominant_transverse_multiplier": {"imag": 0.0},
            "neutral_multiplier_error": 1e-9,
        },
    }
    acceptance = {
        "maximum_root_multiplier_residual": 1e-6,
        "maximum_multiplier_imaginary_part": 1e-7,
        "maximum_neutral_multiplier_error": 1e-5,
    }
    assert root_row_passes(row, 1e-8, acceptance)
