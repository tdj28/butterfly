from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.correct_jones_period1536_decimal_augmented_bracket import secant_seed


def test_secant_seed_interpolates_bound_rows() -> None:
    source = {
        "rows": [
            {
                "a": 1.0,
                "period_time": 10.0,
                "nodes": [[0.0, 0.0, 0.0]],
                "status": {"success": True},
            },
            {
                "a": 2.0,
                "period_time": 12.0,
                "nodes": [[2.0, 4.0, 6.0]],
                "status": {"success": True},
            },
        ]
    }
    bracket = {
        "left_index": 0,
        "right_index": 1,
        "left_multiplier": {"real": 0.0},
        "right_multiplier": {"real": -3.0},
    }
    seed = secant_seed(source, bracket)
    assert seed["a"] == 4.0 / 3.0
    assert np.isclose(seed["period_time"], 10.0 + 2.0 / 3.0)
    assert np.allclose(seed["nodes"], [[2.0 / 3.0, 4.0 / 3.0, 2.0]])
    assert seed["source_row_indices"] == [0, 1]
