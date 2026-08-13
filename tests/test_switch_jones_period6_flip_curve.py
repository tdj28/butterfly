from __future__ import annotations

from scripts.switch_jones_period6_flip_curve import SCHEMA


def test_period6_branch_switch_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-branch-switch-manifest.v1"
