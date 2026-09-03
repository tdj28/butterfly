from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "analyze_upo_lobe_pim_overlap.py"
SPEC = importlib.util.spec_from_file_location("upo_lobe_pim_overlap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_distance_summary_uses_declared_scaled_coordinates():
    source = np.asarray([[0.0, 0.0, 0.0], [0.0, 30.0, 0.0006]])
    target = np.asarray([[0.0, 15.0, 0.0003]])
    result = MODULE._distance_summary(
        source, target, np.asarray([1, 2]), np.asarray([30.0, 0.0006])
    )
    assert result["minimum"] == pytest.approx(np.sqrt(0.5))
    assert result["maximum"] == pytest.approx(np.sqrt(0.5))


def test_lobe_points_honor_capture_truncation_and_seed_subset():
    atlas = {
        "traces": [
            {
                "case_id": "case",
                "amplitude_index": 0,
                "retained_pre_capture_returns": 2,
                "states": [[0.0, -32.0, 0.0], [0.0, -30.0, 0.0], [0.0, -40.0, 0.0]],
            },
            {
                "case_id": "case",
                "amplitude_index": 1,
                "retained_pre_capture_returns": 1,
                "states": [[0.0, -33.0, 0.0]],
            },
        ]
    }
    result = MODULE._lobe_points(atlas, "case", [0], 1, -31.0)
    assert result.shape == (1, 3)
    assert result[0, 1] == -32.0
