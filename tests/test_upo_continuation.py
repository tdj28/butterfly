from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from butterfly import RosslerParameters, SolverConfig


SCRIPT = Path(__file__).parents[1] / "scripts" / "continue_pim_upos_in_a.py"
SPEC = importlib.util.spec_from_file_location("upo_continuation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_crossing_count_uses_shifted_full_period(monkeypatch):
    captured = {}

    def fake_collect(*_args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            times=np.asarray([1.0, 1.000002, 5.0, 11.0, 11.000002]),
            integration_success=True,
        )

    monkeypatch.setattr(MODULE, "collect_crossings", fake_collect)
    count, success = MODULE._crossing_count(
        RosslerParameters(a=0.148, b=0.2, c=20.0),
        np.asarray([0.0, 1.0, 0.0]),
        10.0,
        SolverConfig(),
        16,
        phase_fraction=0.1,
    )
    assert success
    assert count == 3
    assert captured["transient"] == 1.0
    assert captured["observation_horizon"] == 10.0000001


def test_separate_section_count_qualification_does_not_change_flow_audit():
    branches = [
        {
            "rows": [
                {
                    "audit": {
                        "one_period_section_crossing_count": 12,
                        "section_count_integration_success": True,
                    }
                },
                {
                    "audit": {
                        "one_period_section_crossing_count": 12,
                        "section_count_integration_success": True,
                    }
                },
            ]
        }
    ]
    result = MODULE._section_count_summary(
        branches,
        {
            "section_count": {
                "gate": False,
                "phase_fraction": 0.1,
                "expected_crossings": 12,
            }
        },
    )
    assert result["separate_qualification"]
    assert result["evaluated_points"] == 2
    assert result["observed_counts"] == [12]
    assert result["passed"]


def test_parameter_match_tolerates_binary_grid_roundoff_only():
    matched, error = MODULE._parameter_match(
        (0.14812499999999998, 0.148125),
        0.148125,
        1e-14,
    )
    assert matched
    assert error < 1e-16
    assert not MODULE._parameter_match((0.148124, 0.148125), 0.148125, 1e-14)[0]
