"""Synthetic integrity tests; never read target artifacts or open SSH."""
import hashlib
import json

import pytest

from scripts import archive_exp480_to_prax as backup
from scripts import summarize_historical_event_run as report


def test_report_audits_declared_bytes_and_rejects_extras(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "RUN", tmp_path)
    child = tmp_path / "profile.json"
    child.write_text("{}")
    receipt = {"source": {"commit": report.SOURCE}, "status": "completed", "files": [
        {"path": child.name, "bytes": 2, "sha256": hashlib.sha256(b"{}").hexdigest()}]}
    raw = json.dumps(receipt).encode()
    (tmp_path / "receipt.json").write_bytes(raw)
    (tmp_path / "started.json").write_text("{}")
    monkeypatch.setattr(report, "RECEIPT_SHA", hashlib.sha256(raw).hexdigest())
    assert report.audit() == receipt
    (tmp_path / "extra.json").write_text("{}")
    with pytest.raises(ValueError, match="unexpected"):
        report.audit()
    child.write_text("changed")
    with pytest.raises(ValueError, match="hash/size"):
        report.audit()


def test_report_rejects_terminal_receipt_tampering(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "RUN", tmp_path)
    (tmp_path / "receipt.json").write_text("{}")
    with pytest.raises(ValueError, match="receipt changed"):
        report.audit()


def test_backup_preflight_requires_exact_bytes_and_permissions(tmp_path, monkeypatch):
    monkeypatch.setattr(backup, "OUTPUT", tmp_path)
    path = tmp_path / "evidence.tar"
    path.write_bytes(b"synthetic")
    path.chmod(0o600)
    monkeypatch.setattr(backup, "ARCHIVE_BYTES", 9)
    monkeypatch.setattr(backup, "ARCHIVE_SHA", hashlib.sha256(b"synthetic").hexdigest())
    assert backup.preflight() == path
    path.chmod(0o644)
    with pytest.raises(ValueError, match="owner-only"):
        backup.preflight()


def test_backup_default_does_not_open_ssh(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["archive"])
    monkeypatch.setattr(backup, "preflight", lambda: tmp_path / "unused.tar")
    monkeypatch.setattr(backup.subprocess, "run", lambda *a, **kw: pytest.fail("unexpected SSH"))
    assert backup.main() == 0
