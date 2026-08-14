from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.qualify_jones_period24_near_event import selected_child_seed


def continuation_manifest() -> dict:
    return {
        "continuation_schema": "continuation.v1",
        "allow_failed_continuation_prefix": True,
        "source_candidate": {
            "selection_rule": "first_absolute_event_separation",
            "minimum_absolute_event_separation": 1e-3,
            "maximum_prefix_matching_residual": 1e-8,
            "minimum_prefix_half_node_rms": 5e-6,
        },
    }


def row(a: float, residual: float = 1e-9) -> dict:
    return {
        "a": a,
        "half_node_rms": 1e-5,
        "status": {"success": True, "matching_residual": residual},
    }


def test_selects_first_continuation_row_crossing_separation() -> None:
    receipt = {
        "schema": "continuation.v1",
        "passed": False,
        "rows": [row(1.0), row(0.9995), row(0.9989), row(0.997)],
    }
    selected = selected_child_seed(
        receipt,
        {"corrected_a": 1.0},
        continuation_manifest(),
        "continuation",
    )
    assert selected is receipt["rows"][2]


def test_rejects_failed_matching_gate_before_selected_row() -> None:
    receipt = {
        "schema": "continuation.v1",
        "passed": False,
        "rows": [row(1.0), row(0.9995, residual=2e-8), row(0.9989)],
    }
    with pytest.raises(ValueError, match="matching gate"):
        selected_child_seed(
            receipt,
            {"corrected_a": 1.0},
            continuation_manifest(),
            "continuation",
        )


def test_rejects_failed_continuation_without_explicit_prefix_authorization() -> None:
    manifest = continuation_manifest()
    manifest["allow_failed_continuation_prefix"] = False
    receipt = {
        "schema": "continuation.v1",
        "passed": False,
        "rows": [row(1.0), row(0.9989)],
    }
    with pytest.raises(ValueError, match="not authorized"):
        selected_child_seed(
            receipt,
            {"corrected_a": 1.0},
            manifest,
            "continuation",
        )
