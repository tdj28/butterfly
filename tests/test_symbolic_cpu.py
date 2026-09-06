"""Exercise the CPU adapter against the preserved known-anchor control."""
import json
from pathlib import Path

import pytest

from scripts.run_symbolic_center_cpu import integrate_cpu
from scripts.qualify_symbolic_gpu_records import compare_records


@pytest.mark.parametrize("change", [None, "hash", "source", "producer", "passed"])
def test_postcollection_preparation_binds_qualification(tmp_path, change):
    from types import SimpleNamespace
    from scripts.analyze_frozen_symbolic_cpu import digest, qualified_preparation
    producer = tmp_path / "producer.py"
    producer.write_text("# synthetic CPU adapter\n")
    record = {"passed": True, "source_commit": "a" * 40, "producer_sha256": digest(producer)}
    if change == "source":
        record["source_commit"] = "b" * 40
    elif change == "producer":
        record["producer_sha256"] = "b" * 64
    elif change == "passed":
        record["passed"] = False
    path = tmp_path / "qualification.json"
    path.write_text(json.dumps(record))
    sha = "b" * 64 if change == "hash" else digest(path)
    cpu = SimpleNamespace(__file__=str(producer), prepare=lambda _: ({"input_hashes": {}}, {}))
    if change:
        with pytest.raises(ValueError):
            qualified_preparation(cpu, "a" * 40, path, sha)
    else:
        assert qualified_preparation(cpu, "a" * 40, path, sha)["input_hashes"] == {"cpu_adapter_qualification": sha}


def test_analysis_launcher_preserves_frozen_arguments_and_never_restarts(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import plistlib
    from scripts import analyze_frozen_symbolic_cpu as wrapper
    args = SimpleNamespace(mode="analyze", output_dir=tmp_path / "output",
        launch_state=tmp_path / "service", source_directory=tmp_path / "frozen",
        source_commit="a" * 40, qualification=tmp_path / "qualification.json",
        qualification_sha256="b" * 64, collection=tmp_path / "collection", collection_sha256="c" * 64)
    calls = []
    monkeypatch.setattr(wrapper.subprocess, "run", lambda *a, **kw: calls.append((a, kw)))
    wrapper.launch(args)
    plist = plistlib.loads((args.launch_state / "job.plist").read_bytes())
    assert plist["KeepAlive"] is False
    assert plist["WorkingDirectory"] == str(args.source_directory)
    assert plist["ProgramArguments"][:2] == ["/usr/bin/caffeinate", "-i"]
    assert "--launch-state" not in plist["ProgramArguments"]
    assert args.collection_sha256 in plist["ProgramArguments"]
    assert len(calls) == 1 and calls[0][0][0][:2] == ["launchctl", "bootstrap"]
    with pytest.raises(FileExistsError):
        wrapper.launch(args)


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
