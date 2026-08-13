from __future__ import annotations

import numpy as np

from scripts.switch_jones_period6_flip_curve import (
    SCHEMA,
    bounded_predictor,
    primary_tangent_offsets,
)


def test_period6_branch_switch_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-branch-switch-manifest.v1"


def test_bounded_predictor_preserves_nominal_step_inside_guard():
    base = np.asarray((0.0, 0.0, 0.0, 1.0, 0.5))
    tangent = np.asarray((1.0, 0.0, 0.0, 0.0, 0.01))
    predictor, step = bounded_predictor(base, tangent, 0.1, (0.4, 0.6))
    assert step == 0.1
    np.testing.assert_allclose(predictor, base + step * tangent)


def test_bounded_predictor_shortens_before_upper_guard():
    base = np.asarray((0.0, 0.0, 0.0, 1.0, 0.59))
    tangent = np.asarray((1.0, 0.0, 0.0, 0.0, 0.5))
    predictor, step = bounded_predictor(base, tangent, 0.1, (0.4, 0.6))
    assert step < 0.1
    assert 0.59 < predictor[4] < 0.6


def test_primary_tangent_offsets_preserve_legacy_and_allow_one_sided_rule():
    assert primary_tangent_offsets({"primary_a_offset": 1e-5}) == [-1e-5, 0.0, 1e-5]
    assert primary_tangent_offsets(
        {"primary_tangent_offsets": [-2e-5, -1e-5, 0.0]}
    ) == [-2e-5, -1e-5, 0.0]
