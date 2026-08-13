from scripts.adapt_jones_period6_flip_below_grazing import (
    SCHEMA,
    adaptive_step_after_success,
    correction_status_passes,
)


def test_adaptive_below_grazing_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-adaptive-below-grazing-manifest.v1"


def test_correction_status_gate_rejects_inaccurate_corrector():
    acceptance = {
        "maximum_orbit_residual": 1e-8,
        "maximum_phase_residual": 1e-8,
        "maximum_tangent_residual": 1e-8,
        "maximum_normalization_residual": 1e-8,
        "maximum_arclength_residual": 1e-8,
    }
    status = {
        "solver_success": True,
        "orbit_residual": 1e-12,
        "phase_residual": 1e-12,
        "tangent_residual": 1e-12,
        "normalization_residual": 1e-12,
        "arclength_residual": 1e-12,
    }
    assert correction_status_passes(status, acceptance)
    status["tangent_residual"] = 1e-3
    assert not correction_status_passes(status, acceptance)


def test_adaptive_step_policy_grows_only_after_frozen_streak():
    continuation = {
        "hard_evaluations": 18,
        "easy_evaluations": 7,
        "growth_after_easy_steps": 3,
        "minimum_step_length": 0.00025,
        "maximum_step_length": 0.03,
        "shrink_factor": 0.5,
        "growth_factor": 1.2,
    }
    step, streak = adaptive_step_after_success(0.01, 5, 0, continuation)
    step, streak = adaptive_step_after_success(step, 5, streak, continuation)
    assert step == 0.01
    step, streak = adaptive_step_after_success(step, 5, streak, continuation)
    assert step == 0.012
    assert streak == 0


def test_adaptive_step_policy_shrinks_after_hard_acceptance():
    continuation = {
        "hard_evaluations": 18,
        "easy_evaluations": 7,
        "growth_after_easy_steps": 3,
        "minimum_step_length": 0.00025,
        "maximum_step_length": 0.03,
        "shrink_factor": 0.5,
        "growth_factor": 1.2,
    }
    step, streak = adaptive_step_after_success(0.01, 18, 2, continuation)
    assert step == 0.005
    assert streak == 0
