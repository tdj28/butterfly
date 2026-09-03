from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "trace_midpoint_upo_lobe.py"
SPEC = importlib.util.spec_from_file_location("midpoint_upo_lobe", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_left_lobe_points_use_capture_truncation_and_nested_indices():
    traces = [
        {
            "amplitude_index": 0,
            "retained_pre_capture_returns": 2,
            "states": [[0.0, -32.0, 0.0], [0.0, -30.0, 0.0], [0.0, -40.0, 0.0]],
        },
        {
            "amplitude_index": 1,
            "retained_pre_capture_returns": 1,
            "states": [[0.0, -33.0, 0.0]],
        },
    ]
    count, minimum = MODULE._left_lobe_points(traces, [0], 1, -31.0)
    assert count == 1
    assert minimum == -32.0
