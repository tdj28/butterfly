from __future__ import annotations

import numpy as np

from scripts.qualify_jones_period12_normal_form import (
    SCHEMA,
    fit_power_law,
    flip_multiplier_ratio,
)


def test_period12_normal_form_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period12-normal-form-manifest.v1"


def test_power_law_fit_recovers_square_root():
    offsets = np.geomspace(1e-6, 1e-3, 9)
    amplitudes = 2.5 * np.sqrt(offsets)
    fit = fit_power_law(offsets, amplitudes)
    assert abs(fit["exponent"] - 0.5) < 1e-12
    assert fit["r_squared"] > 1.0 - 1e-14


def test_flip_multiplier_ratio_matches_cubic_normal_form_limit():
    assert abs(flip_multiplier_ratio(-1.02, 0.92) - 4.0) < 1e-12
