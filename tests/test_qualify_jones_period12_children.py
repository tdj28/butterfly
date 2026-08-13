from __future__ import annotations

import pytest

from scripts.qualify_jones_period12_children import (
    SCHEMA,
    proper_subperiod_fractions,
    select_candidate,
)


def test_period12_qualification_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period12-child-qualification-manifest.v1"


def test_proper_subperiod_fractions_cover_all_period12_divisors():
    assert proper_subperiod_fractions(12) == [1 / 12, 1 / 6, 1 / 4, 1 / 3, 1 / 2]


def test_select_candidate_requires_exact_frozen_row():
    events = [
        {
            "c": 7.18,
            "branches": [
                {"direction": -1, "rows": [{"a": 0.2158, "value": "selected"}]},
                {"direction": 1, "rows": []},
            ],
        }
    ]
    event, row = select_candidate(
        events, {"c": 7.18, "candidate_a": 0.2158, "source_direction": -1}
    )
    assert event["c"] == 7.18
    assert row["value"] == "selected"
    with pytest.raises(ValueError, match="target a"):
        select_candidate(
            events, {"c": 7.18, "candidate_a": 0.2159, "source_direction": -1}
        )
