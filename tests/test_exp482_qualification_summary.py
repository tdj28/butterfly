"""Read-only EXP-482 replay boundary; never requires live research data."""
import pytest
import subprocess
import sys

from scripts import summarize_exp482_qualification as report


def test_direct_cli_help_needs_no_target_inputs(tmp_path):
    result = subprocess.run([sys.executable, "-B", str(report.ROOT/"scripts/summarize_exp482_qualification.py"),
        "--help"], cwd=tmp_path, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert "Read-only raw replay" in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_bad_anchor_rejected_before_inputs_or_replay(tmp_path, monkeypatch):
    (tmp_path/"receipt.json").write_text("{}")
    monkeypatch.setattr(report, "RUN", tmp_path)
    monkeypatch.setattr(report, "ANCHORS", {"receipt.json": "0"*64})
    def forbidden(*args, **kwargs): pytest.fail("invalid anchor reached input loading or numerical replay")
    monkeypatch.setattr(report, "load_package", forbidden)
    monkeypatch.setattr(report, "_compare_qualification", forbidden)
    with pytest.raises(ValueError, match="anchor"):
        report.audit()


def test_completed_phase_anchor_check_ignores_active_collection(tmp_path, monkeypatch):
    phase = tmp_path/"qualification.json"
    phase.write_text("{\"completed\":true}")
    monkeypatch.setattr(report, "RUN", tmp_path)
    monkeypatch.setattr(report, "ANCHORS", {"qualification.json": report.sha256(phase)})
    report.check_anchors()
    (tmp_path/"collection.json").write_text("active changing evidence")
    report.check_anchors()
    phase.write_text("{\"completed\":false}")
    with pytest.raises(ValueError, match="anchor"):
        report.check_anchors()
