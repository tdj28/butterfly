import sys
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_jones_period1536_decimal_augmented_independent import (  # noqa: E402
    accepted_a_envelope,
)


def test_accepted_a_envelope_ignores_failed_rows():
    receipt = {
        "rows": [
            {"a": 0.25, "status": {"success": True}},
            {"a": 0.20, "status": {"success": False}},
            {"a": 0.23, "status": {"success": True}},
        ]
    }
    assert accepted_a_envelope(receipt) == (Decimal("0.23"), Decimal("0.25"), 2)


def test_accepted_a_envelope_requires_success():
    with pytest.raises(ValueError, match="no successful rows"):
        accepted_a_envelope({"rows": []})
