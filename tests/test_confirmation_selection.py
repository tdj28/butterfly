import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "confirm_candidates.py"
SPEC = importlib.util.spec_from_file_location("confirm_candidates", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def source_result() -> dict:
    return {
        "shape": [2, 2],
        "rows": [
            {"point_index": index, "candidate_normalized_error": float(index + 1)}
            for index in range(4)
        ],
    }


def test_explicit_selection_preserves_core_order_and_sorts_targets() -> None:
    selection = MODULE.selection_for_manifest(
        {"selection": {"point_indices": [3, 0, 2]}}, source_result()
    )
    assert selection.core_indices == (3, 0, 2)
    assert selection.selected_indices == (0, 2, 3)
    assert selection.parent_core_indices == {0: (0,), 2: (2,), 3: (3,)}


def test_explicit_selection_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="unique nonempty"):
        MODULE.selection_for_manifest(
            {"selection": {"point_indices": [1, 1]}}, source_result()
        )
