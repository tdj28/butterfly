from __future__ import annotations

from scripts.continue_jones_period6_flip_curve import SCHEMA


def test_flip_curve_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-curve-manifest.v1"
