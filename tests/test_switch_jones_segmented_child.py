from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from butterfly.scan import canonical_json, sha256_bytes

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.switch_jones_period12_segmented_child import (
    normalized_event,
    qualified_audit_bytes,
)


def test_passed_event_needs_no_audit() -> None:
    event = {"passed": True}
    assert qualified_audit_bytes(event, canonical_json(event), {}, None) is None


def test_failed_event_requires_bound_passing_audit(tmp_path) -> None:
    event = {"passed": False}
    event_bytes = canonical_json(event)
    audit = {
        "schema": "audit.v1",
        "passed": True,
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "checks": {"independent": True},
    }
    audit_bytes = canonical_json(audit)
    audit_path = tmp_path / "audit.json"
    audit_path.write_bytes(audit_bytes)
    manifest = {
        "audit_schema": "audit.v1",
        "audit_receipt_sha256": sha256_bytes(audit_bytes),
    }

    assert (
        qualified_audit_bytes(event, event_bytes, manifest, audit_path)
        == audit_bytes
    )


def test_failed_event_rejects_unbound_audit(tmp_path) -> None:
    event = {"passed": False}
    event_bytes = canonical_json(event)
    audit = {
        "schema": "audit.v1",
        "passed": True,
        "event_receipt_sha256": "wrong",
        "checks": {"independent": True},
    }
    audit_bytes = canonical_json(audit)
    audit_path = tmp_path / "audit.json"
    audit_path.write_bytes(audit_bytes)
    manifest = {
        "audit_schema": "audit.v1",
        "audit_receipt_sha256": sha256_bytes(audit_bytes),
    }

    with pytest.raises(ValueError, match="not qualified"):
        qualified_audit_bytes(event, event_bytes, manifest, audit_path)


def test_normalized_event_exposes_decimal_augmented_finest_profile() -> None:
    receipt = {
        "schema": "butterfly.jones-period768-decimal-augmented-independent-receipt.v1",
        "passed": True,
        "nodes_decimal": [["1", "2", "3"], ["4", "5", "6"]],
        "tangent_nodes_decimal": [["0", "1", "0"], ["1", "0", "0"]],
        "profiles": [
            {"a_decimal": "0.24", "period_time_decimal": "57"},
            {"a_decimal": "0.25", "period_time_decimal": "58"},
        ],
    }
    event = normalized_event(receipt, {"fixed_b": 0.2, "fixed_c": 7.6})
    assert event["corrected_a"] == "0.25"
    assert event["period_time"] == "58"
    assert event["segment_count"] == 2
    assert event["nodes"] == receipt["nodes_decimal"]
    assert event["tangent_nodes"] == receipt["tangent_nodes_decimal"]


def test_normalized_event_exposes_8192_profile() -> None:
    receipt = {
        "schema": "butterfly.jones-period768-decimal-augmented-8192-receipt.v1",
        "passed": True,
        "nodes_decimal": [["1", "2", "3"]],
        "tangent_nodes_decimal": [["0", "1", "0"]],
        "profile": {"a_decimal": "0.26", "period_time_decimal": "59"},
    }
    event = normalized_event(receipt, {"fixed_b": 0.2, "fixed_c": 7.6})
    assert event["corrected_a"] == "0.26"
    assert event["period_time"] == "59"
    assert event["segment_count"] == 1
