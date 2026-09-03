from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.solve_jones_period12_augmented_flip import selected_event_bracket


def test_selects_frozen_stability_bracket() -> None:
    receipt = {
        "passed": True,
        "stability_brackets": [
            {"a_bracket": [1.0, 2.0]},
            {"a_bracket": [3.0, 4.0]},
        ],
    }
    manifest = {
        "bracket_collection": "stability_brackets",
        "bracket_index": 0,
        "a_bounds": [1.0, 2.0],
    }
    assert selected_event_bracket(receipt, manifest) is receipt["stability_brackets"][0]


def test_rejects_mismatched_frozen_bracket_bounds() -> None:
    receipt = {
        "passed": True,
        "stability_brackets": [{"a_bracket": [1.0, 2.0]}],
    }
    manifest = {
        "bracket_collection": "stability_brackets",
        "bracket_index": 0,
        "a_bounds": [1.0, 3.0],
    }
    with pytest.raises(ValueError, match="bounds"):
        selected_event_bracket(receipt, manifest)
