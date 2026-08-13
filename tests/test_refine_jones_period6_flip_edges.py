from __future__ import annotations

from scripts.refine_jones_period6_flip_edges import SCHEMA


def test_flip_refinement_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-refinement-manifest.v1"
