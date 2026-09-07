"""Synthetic benchmark controls are explicit and do not change target plans."""
import pytest

from scripts.benchmark_paired_sections import step_profile


def test_original_benchmark_profile_is_unchanged():
    assert step_profile("original") == ([.02,.01],3000)


def test_refined_profile_fits_the_fixed_synthetic_horizon():
    steps, cap=step_profile("refined")
    assert steps==[.0025,.00125]
    assert [round(20.5/dt) for dt in steps]==[8200,16400]
    assert all(20.5/dt <= cap for dt in steps)


def test_unknown_profile_cannot_select_arbitrary_settings():
    with pytest.raises(ValueError):step_profile("target")
