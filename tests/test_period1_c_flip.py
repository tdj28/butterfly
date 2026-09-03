from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "solve_period1_c_flip.py"
SPEC = importlib.util.spec_from_file_location("period1_c_flip", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_seed_row_selects_nearest_source_point_inside_bracket():
    receipt = {
        "schema": "butterfly.hopf-period1-to-hub-receipt.v1",
        "rows": [
            {"parameters": {"c": 3.1}},
            {"parameters": {"c": 3.2}},
            {"parameters": {"c": 3.3}},
        ],
    }
    assert MODULE._seed_row(receipt, [3.15, 3.3])["parameters"]["c"] == 3.2


def test_seed_row_rejects_missing_bracket_support():
    receipt = {
        "schema": "butterfly.hopf-period1-to-hub-receipt.v1",
        "rows": [{"parameters": {"c": 2.0}}],
    }
    with pytest.raises(ValueError, match="no row inside"):
        MODULE._seed_row(receipt, [3.0, 3.2])
