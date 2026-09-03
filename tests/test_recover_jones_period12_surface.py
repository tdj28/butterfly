from __future__ import annotations

from scripts.recover_jones_period12_surface import (
    SCHEMA,
    interpolate_normal_form_seed,
)


def test_period12_surface_recovery_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period12-surface-recovery-manifest.v1"


def test_normal_form_seed_interpolates_offset_then_c():
    receipt = {
        "targets": [
            {
                "c": c_value,
                "rows": [
                    {
                        "offset_a": offset,
                        "child": {
                            "initial_state": [c_value + offset, 2 * offset, c_value],
                            "period_time": 10 + c_value + offset,
                        },
                    }
                    for offset in (1.0, 3.0)
                ],
            }
            for c_value in (2.0, 4.0)
        ]
    }
    state, period = interpolate_normal_form_seed(receipt, 3.0, 2.0)
    assert state.tolist() == [5.0, 4.0, 3.0]
    assert period == 15.0
