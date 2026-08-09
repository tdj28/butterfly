from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "evaluate_midpoint_lobe_pim_association.py"
SPEC = importlib.util.spec_from_file_location("midpoint_lobe_pim", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _acceptance():
    return {
        "maximum_two_branch_left_lobe_points_per_line": 0,
        "minimum_three_branch_left_lobe_points_per_line": 10,
        "maximum_fine_directed_distance": 5e-5,
        "maximum_coarse_directed_distance": 1e-4,
    }


def test_two_branch_requires_complete_lobe_exclusion():
    assert MODULE._line_pass(2, 0, None, None, _acceptance())
    assert not MODULE._line_pass(2, 1, None, None, _acceptance())


def test_three_branch_requires_support_and_both_distance_gates():
    fine = {"maximum": 4e-5}
    coarse = {"maximum": 9e-5}
    assert MODULE._line_pass(3, 10, fine, coarse, _acceptance())
    assert not MODULE._line_pass(3, 9, fine, coarse, _acceptance())
    assert not MODULE._line_pass(3, 10, {"maximum": 6e-5}, coarse, _acceptance())
