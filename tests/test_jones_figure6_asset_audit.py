import json
from pathlib import Path

import pytest

from scripts.audit_jones_figure6_asset import audit_asset


SOURCE = Path(
    "experiments/source-transcriptions/jones2012-figure6-asset-audit.json"
)


def test_separate_asset_audit_preserves_the_frozen_transcription() -> None:
    result = audit_asset(json.loads(SOURCE.read_text()))
    assert result == {
        "passed": True,
        "image_verified": False,
        "dimensions": [823, 534],
        "vector_geometry": False,
        "attachment_status": "not fully resolved",
    }


def test_asset_audit_rejects_a_fabricated_vector_source() -> None:
    document = json.loads(SOURCE.read_text())
    document["figure6_asset"]["has_recoverable_vector_geometry"] = True
    with pytest.raises(ValueError, match="raster rather than vector"):
        audit_asset(document)
