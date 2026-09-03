from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).parents[1] / "scripts" / "trace_upo_unstable_lobe_atlas.py"
SPEC = importlib.util.spec_from_file_location("upo_lobe_atlas", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _manifest():
    return {
        "occupancy": {
            "bins_per_axis": 4,
            "coordinate_axes": [1, 2],
            "bounds": [[0.0, 4.0], [0.0, 4.0]],
        }
    }


def test_occupancy_reports_inside_fraction_and_endpoint_bins():
    occupied, inside = MODULE._occupancy(
        np.asarray(
            [
                [0.0, 0.0, 0.0],
                [0.0, 3.99, 3.99],
                [0.0, 5.0, 2.0],
            ]
        ),
        _manifest(),
    )
    assert inside == 2 / 3
    assert occupied[0, 0]
    assert occupied[3, 3]
    assert np.count_nonzero(occupied) == 2


def test_dilation_coverage_and_jaccard_are_bounded():
    left = np.zeros((5, 5), dtype=bool)
    right = np.zeros((5, 5), dtype=bool)
    left[2, 2] = True
    right[2, 3] = True
    assert MODULE._coverage(left, right, 0) == 0.0
    assert MODULE._coverage(left, right, 1) == 1.0
    assert MODULE._dilated_jaccard(left, left, 1) == 1.0
    value = MODULE._dilated_jaccard(left, right, 1)
    assert 0.0 < value < 1.0
