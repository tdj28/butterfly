from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.scan_jones_period24_segmented_flip import selected_source_rows


def row(step_index: int, success: bool = True) -> dict:
    return {"step_index": step_index, "status": {"success": success}}


def test_selects_explicit_failed_continuation_prefix() -> None:
    continuation = {
        "passed": False,
        "rows": [row(-1), row(0), row(1), row(2)],
    }
    manifest = {
        "allow_failed_continuation_prefix": True,
        "maximum_source_step_index": 1,
    }
    assert [item["step_index"] for item in selected_source_rows(continuation, manifest)] == [
        -1,
        0,
        1,
    ]


def test_rejects_failed_continuation_without_prefix_authorization() -> None:
    with pytest.raises(ValueError, match="passed"):
        selected_source_rows(
            {"passed": False, "rows": [row(-1)]},
            {"allow_failed_continuation_prefix": False},
        )


def test_rejects_incomplete_frozen_prefix() -> None:
    with pytest.raises(ValueError, match="frozen prefix"):
        selected_source_rows(
            {"passed": False, "rows": [row(-1), row(0)]},
            {
                "allow_failed_continuation_prefix": True,
                "maximum_source_step_index": 1,
            },
        )
