from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.audit_jones_period768_decimal_criticality import (
    criticality,
    resolved_classification,
    source_is_qualified,
)


def test_resolved_classification_requires_both_tableaux() -> None:
    assert resolved_classification([-2e-6, -3e-6], 1e-6) == "unstable"
    assert resolved_classification([2e-6, 3e-6], 1e-6) == "stable"
    assert resolved_classification([-2e-6, 3e-6], 1e-6) == "neutral"


def test_criticality_requires_stability_exchange() -> None:
    assert criticality("unstable", "stable") == "supercritical"
    assert criticality("stable", "unstable") == "subcritical"
    assert criticality("stable", "stable") == "other-or-unresolved"


def test_source_qualification_binds_neutral_parent_and_stable_child() -> None:
    identity = {
        "historical_integration_success": True,
        "barrio_integration_success": True,
        "historical_phase_count": 1792,
        "barrio_phase_count": 2048,
    }
    qualification = {
        "passed": False,
        "event_receipt_sha256": "event",
        "child_multiplier_relative_spread": 1e-4,
        "classifications": {
            "dop853": {"parent": "neutral", "child": "stable"},
            "radau": {"parent": "neutral", "child": "stable"},
        },
        "results": {
            name: {
                "child": {
                    "half_period_closure": 3e-6,
                    "section_identity": identity,
                }
            }
            for name in ("dop853", "radau")
        },
    }
    manifest = {
        "event_receipt_sha256": "event",
        "qualification_solvers": ["dop853", "radau"],
        "source_requirements": {
            "parent_classification": "neutral",
            "child_classification": "stable",
            "maximum_child_multiplier_relative_spread": 0.02,
            "minimum_child_half_period_closure": 2e-6,
            "historical_phase_count": 1792,
            "barrio_phase_count": 2048,
        },
    }
    assert source_is_qualified(qualification, {"passed": True}, manifest)
