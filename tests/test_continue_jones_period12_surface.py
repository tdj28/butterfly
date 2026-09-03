from __future__ import annotations

from scripts.continue_jones_period12_surface import SCHEMA, select_child_seed


def test_period12_surface_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period12-surface-manifest.v1"


def test_surface_seed_selects_nearest_frozen_offset():
    receipt = {
        "targets": [
            {
                "c": 7.18,
                "rows": [
                    {
                        "offset_a": 5e-6,
                        "child": {"initial_state": [1, 2, 3], "period_time": 10},
                    },
                    {
                        "offset_a": 15e-6,
                        "child": {"initial_state": [4, 5, 6], "period_time": 20},
                    },
                ],
            }
        ]
    }
    state, period = select_child_seed(receipt, 7.18, 14e-6)
    assert state.tolist() == [4.0, 5.0, 6.0]
    assert period == 20.0
