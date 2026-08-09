from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "refine_upo_lobe_capture.py"
SPEC = importlib.util.spec_from_file_location("upo_lobe_capture", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_phase_offsets_are_unique_integer_returns():
    assert MODULE._phase_offsets(12, [0.0, 1 / 3, 2 / 3]) == [0, 4, 8]
    with pytest.raises(ValueError, match="unique"):
        MODULE._phase_offsets(2, [0.0, 0.1])


def test_restricted_capture_mean_requires_qualification_by_horizon():
    rows = [
        {
            "captured": True,
            "capture_start_return": 20,
            "computed_returns": 24,
        },
        {
            "captured": True,
            "capture_start_return": 62,
            "computed_returns": 66,
        },
        {
            "captured": False,
            "capture_start_return": None,
            "computed_returns": 96,
        },
    ]
    assert MODULE._restricted_capture_mean(rows, 64) == pytest.approx(148 / 3)
    assert MODULE._restricted_capture_mean(rows, 96) == pytest.approx(178 / 3)


def test_candidate_summary_requires_same_endpoint_direction_at_all_phases():
    manifest = {
        "cases": [{"id": "left"}, {"id": "right"}],
        "candidates": [{"family_id": "family", "sign": 1}],
        "phase_fractions": [0.0, 1 / 3, 2 / 3],
        "administrative_horizons": [64, 96],
        "acceptance": {"minimum_absolute_endpoint_mean_difference": 5.0},
    }
    rows = []
    for phase_index in range(3):
        rows.extend(
            [
                {
                    "family_id": "family",
                    "sign": 1,
                    "phase_index": phase_index,
                    "case_id": "left",
                    "restricted_capture_means": {"64": 50.0, "96": 70.0},
                    "passed": True,
                },
                {
                    "family_id": "family",
                    "sign": 1,
                    "phase_index": phase_index,
                    "case_id": "right",
                    "restricted_capture_means": {"64": 40.0, "96": 60.0},
                    "passed": True,
                },
            ]
        )
    summary = MODULE._candidate_summaries(rows, manifest)[0]
    assert summary["classification"] == "earlier_capture_at_three_branch_endpoint"
    assert summary["passed"]

    rows[-1]["restricted_capture_means"] = {"64": 60.0, "96": 80.0}
    summary = MODULE._candidate_summaries(rows, manifest)[0]
    assert summary["classification"] == "phase_inconsistent_or_below_effect_floor"
    assert not summary["passed"]
