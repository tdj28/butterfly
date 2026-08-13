from __future__ import annotations

import json

import pytest

from butterfly.scan import canonical_json, sha256_bytes
from scripts.switch_jones_period12_segmented_child import qualified_audit_bytes


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
