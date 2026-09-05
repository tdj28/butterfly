"""Exercise the CPU adapter against the preserved known-anchor control."""
import json
from pathlib import Path

import pytest

from scripts.run_symbolic_center_cpu import integrate_cpu
from scripts.qualify_symbolic_gpu_records import compare_records


@pytest.mark.parametrize("index", [0, 1])
def test_adapter_matches_preserved_cpu_event_records(index):
    path = Path(__file__).resolve().parents[1] / "docs/experiments/receipts/EXP-477-post-termination-cpu-control.json"
    control = json.loads(path.read_bytes())["control"]
    config, profile = control["config"], control["profiles"][index]
    run = integrate_cpu([control["candidate"]], dt=profile["dt"],
        horizon=config["ensemble"]["horizon"], checkpoints=config["ensemble"]["checkpoint_times"],
        midpoint=config["ensemble"]["midpoint_window"], ensemble=config["ensemble"],
        capture=config["capture"], gpu_options=config["gpu"], section_name="barrio_positive_x",
        section_code=1, target_cycle_state_count=8)
    assert compare_records(profile, run)["passed"]


def test_qualification_cli_serializes_numpy_diagnostics(tmp_path, monkeypatch, capsys):
    from scripts import run_symbolic_center_cpu as cpu
    path = Path(__file__).resolve().parents[1] / "docs/experiments/receipts/EXP-477-post-termination-cpu-control.json"
    monkeypatch.setattr(cpu, "prepare", lambda _: ({}, {"minimum_free_bytes": 0}))
    monkeypatch.setattr("sys.argv", ["qualify", "--source-commit", "a" * 40,
        "--mode", "qualify", "--cpu-control", str(path), "--cpu-control-sha256",
        cpu.pilot.sha256_file(path), "--output-dir", str(tmp_path / "qualification")])
    assert cpu.main() == 0
    assert json.loads(capsys.readouterr().out)["passed"] is True
