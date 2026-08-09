from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).parents[1] / "scripts" / "continue_hopf_period1_to_hub.py"
SPEC = importlib.util.spec_from_file_location("hopf_period1_to_hub", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_continuation_schedule_contains_exact_scientific_targets():
    manifest = {
        "continuation": {
            "seed_c": 1.0,
            "hub_c": 10.3084,
            "upward_count": 96,
            "downward_bridge_c_values": [0.95, 0.9],
            "near_hopf_c_offsets": [0.01, 0.001],
            "crosscheck_c_values": [1.0, 3.0, 10.3084],
        }
    }
    downward, upward = MODULE._continuation_c_values(manifest, 0.5)
    assert downward == [0.95, 0.9, 0.51, 0.501]
    assert 1.0 in upward
    assert 3.0 in upward
    assert 10.3084 in upward


def test_power_law_recovers_square_root_exponent():
    offsets = np.asarray([0.001, 0.002, 0.005, 0.01])
    result = MODULE._fit_power_law(offsets, 3.0 * np.sqrt(offsets))
    np.testing.assert_allclose(result["exponent"], 0.5, atol=1e-14)
    np.testing.assert_allclose(result["r_squared"], 1.0, atol=1e-14)


def test_minus_one_crossing_retains_parameter_bracket():
    rows = [
        {
            "parameters": {"c": 2.0},
            "primary_nontrivial_multiplier": {"real": -0.8},
        },
        {
            "parameters": {"c": 2.5},
            "primary_nontrivial_multiplier": {"real": -1.2},
        },
    ]
    crossings = MODULE._minus_one_crossings(rows)
    assert crossings == [
        {"c_bracket": [2.0, 2.5], "multiplier_bracket": [-0.8, -1.2]}
    ]
