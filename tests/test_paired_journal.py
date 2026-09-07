"""Durability/integrity controls on synthetic constant and circular fields."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

import numpy as np
import pytest

from butterfly import paired_journal as journal
from butterfly.paired_sections import CaptureSection, collect_paired_sections
from butterfly.poincare import PoincareSection


def setup():
    sections = {f"plane{n}": CaptureSection(PoincareSection((1, 0, 0), n, 1),
        np.array([[float(n), 0, 0]]), (1, 2), (1., 1.), .01, 1) for n in (1, 2)}
    config = dict(dt=.25, horizon=3., checkpoint_times=[1., 3.], state_scales=[1., 1., 1.],
        gate_margin=1e-4, angle_margin=1e-4, escape_radius=100., maximum_events=100, maximum_steps=20)
    return np.array([[0., 0, 0], [0, 1., 0]]), np.array([901, 17]), sections, config


def field(states):
    return np.tile([1., 0, 0], (len(states), 1))


def recorded(path, **kwargs):
    initial, ids, sections, config = setup()
    return journal.record_collection(kwargs.pop("rhs", field), initial, ids, sections, config,
        directory=path, binding={"kind": "synthetic"}, journal_interval_steps=2, **kwargs)


def test_roundtrip_retains_raw_masks_global_ids_and_missing_values(tmp_path):
    result, audit = recorded(tmp_path / "run")
    assert audit["status"] == "completed" and audit["durable_steps"] == 12 and audit["records"] == 6
    assert audit["global_seed_ids"] == [901, 17] and audit["event_counts"] == {"plane1": 2, "plane2": 2}
    assert audit["scientific_qualification"] is False
    for name in result.events:
        index = list(result.events).index(name)
        rows = []
        for path in sorted((tmp_path / "run").glob("journal-*.npz")):
            with np.load(path, allow_pickle=False) as raw:
                rows.append(raw[f"section_{index}__global_seed_ids"])
                assert np.isnan(raw["failure_states"]).all()
                assert raw["global_seed_ids"].tolist() == [901, 17]
        assert np.concatenate(rows).tolist() == [901, 17]
    assert np.isnan(result.capture_times[1]).all()
    assert all("NaN" not in p.read_text() for p in (tmp_path / "run").glob("journal-*.json"))
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in (tmp_path / "run").iterdir())


def test_existing_output_is_not_overwritten_or_used_for_resume(tmp_path):
    recorded(tmp_path / "run")
    before = (tmp_path / "run/terminal.json").read_bytes()
    with pytest.raises(FileExistsError):
        recorded(tmp_path / "run")
    assert (tmp_path / "run/terminal.json").read_bytes() == before


def test_invalid_seed_mapping_and_byte_limit_fail_before_field(tmp_path):
    initial, _, sections, config = setup()
    for ids, limit in [([1, 1], 65536), ([-1, 2], 65536), ([1, 2], 4096)]:
        with pytest.raises(ValueError):
            journal.record_collection(lambda x: pytest.fail("field ran"), initial, ids, sections, config,
                directory=tmp_path / "unused", binding={}, journal_interval_steps=2, maximum_snapshot_bytes=limit)
    assert not (tmp_path / "unused").exists()


def test_tampered_npz_fails_hash_audit(tmp_path):
    recorded(tmp_path / "run")
    (tmp_path / "run/journal-000000.npz").write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash/size"):
        journal.audit_journal(tmp_path / "run")


def test_rehashed_global_event_id_tampering_still_fails(tmp_path):
    recorded(tmp_path / "run")
    root = tmp_path / "run"
    # Third chunk contains first plane crossing (step4 is rounded to its
    # ending step by the kernel; locate by data instead of assuming the chunk).
    for path in sorted(root.glob("journal-*.npz")):
        with np.load(path, allow_pickle=False) as raw:
            arrays = {k: raw[k] for k in raw.files}
        if len(arrays["section_0__global_seed_ids"]):
            arrays["section_0__global_seed_ids"][0] = 999
            with path.open("wb") as stream:
                np.savez_compressed(stream, **arrays)
            metadata = path.with_suffix(".json")
            row = json.loads(metadata.read_bytes())
            row["raw"].update(bytes=path.stat().st_size, sha256=journal.sha256(path))
            metadata.write_text(json.dumps(row))
            break
    with pytest.raises(ValueError, match="seed mapping"):
        journal.audit_journal(root)


def test_interruption_flushes_last_partial_block_without_retry(tmp_path):
    calls = 0
    def interrupted(states):
        nonlocal calls
        calls += 1
        if calls == 33:
            raise KeyboardInterrupt("synthetic")
        return field(states)
    result, audit = recorded(tmp_path / "run", rhs=interrupted)
    assert calls == 33 and result.status == "interrupted"
    assert audit["status"] == "incomplete" and audit["durable_steps"] == result.completed_steps
    assert 0 < result.completed_steps < 12


def test_writer_failure_preserves_prefix_and_never_retries_same_snapshot(tmp_path, monkeypatch):
    original = journal._new_file
    failed_writes = []
    def disk_full(path, writer):
        if path.name == "journal-000001.npz":
            failed_writes.append(path)
            raise OSError("synthetic disk full")
        return original(path, writer)
    monkeypatch.setattr(journal, "_new_file", disk_full)
    result, audit = recorded(tmp_path / "run")
    assert result.status == "failed" and audit["status"] == "incomplete"
    assert audit["durable_steps"] == 2 and result.completed_steps == 4 and len(failed_writes) == 1
    assert result.failure["attempted_step"] == 4 and result.failure["phase"] == "journal"


def test_orphan_npz_cannot_be_promoted_to_completed(tmp_path):
    recorded(tmp_path / "run")
    (tmp_path / "run/journal-999999.npz").write_bytes(b"partial")
    with pytest.raises(ValueError, match="completion"):
        journal.audit_journal(tmp_path / "run")


def test_hard_killed_child_leaves_a_readable_fsynced_prefix(tmp_path):
    output = tmp_path / "killed"
    code = '''
import os, signal, sys, numpy as np
from butterfly.paired_journal import PairedJournal
from butterfly.paired_sections import CaptureSection, collect_paired_sections
from butterfly.poincare import PoincareSection
initial=np.array([[0.,0,0]])
sections={str(n):CaptureSection(PoincareSection((1,0,0),n,1),np.array([[float(n),0,0]]),(1,2),(1.,1.),.01,1) for n in (1,2)}
config=dict(dt=.25,horizon=3.,checkpoint_times=[3.],state_scales=[1.,1.,1.],gate_margin=1e-4,angle_margin=1e-4,escape_radius=100.,maximum_events=100,maximum_steps=20)
writer=PairedJournal(sys.argv[1],initial,[77],sections,config,binding={'kind':'synthetic'},journal_interval_steps=2)
def sink(snapshot):
 writer.append(snapshot)
 os.kill(os.getpid(),signal.SIGKILL)
collect_paired_sections(lambda x:np.tile([1.,0,0],(len(x),1)),initial,sections,**config,progress=sink,journal_interval_steps=2)
'''
    process = subprocess.run([sys.executable, "-c", code, str(output)], timeout=15, capture_output=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "python")})
    assert process.returncode == -signal.SIGKILL, process.stderr.decode()
    audit = journal.audit_journal(output)
    assert audit["status"] == "incomplete" and audit["durable_steps"] == 2 and audit["records"] == 1
    assert not (output / "terminal.json").exists()


def test_callback_cannot_mutate_integrator_arrays():
    initial, _, sections, config = setup()
    plain = collect_paired_sections(field, initial, sections, **config)
    def mutate(snapshot):
        snapshot.final_states[:] = 999
        snapshot.capture_times[:] = 999
        for event in snapshot.events.values():
            event["states"][:] = 999
    observed = collect_paired_sections(field, initial, sections, **config, progress=mutate, journal_interval_steps=2)
    np.testing.assert_array_equal(observed.final_states, plain.final_states)
    np.testing.assert_allclose(observed.capture_times, plain.capture_times)


@pytest.mark.parametrize("kind", ["captured", "time", "extra"])
def test_rehashed_checkpoint_corruption_is_rejected(tmp_path, kind):
    recorded(tmp_path / "run")
    root = tmp_path / "run"
    path = root / "journal-000001.npz"
    with np.load(path, allow_pickle=False) as raw:
        arrays = {k: raw[k] for k in raw.files}
    if kind == "captured":
        arrays["checkpoint_0__captured"][1, 1] = True
    elif kind == "time":
        arrays["checkpoint_0__time"] = np.array(999.)
    else:
        arrays["checkpoint_99__step"] = np.array(999)
    with path.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    metadata = path.with_suffix(".json")
    row = json.loads(metadata.read_bytes())
    row["raw"].update(bytes=path.stat().st_size, sha256=journal.sha256(path))
    metadata.write_text(json.dumps(row))
    with pytest.raises(ValueError, match="checkpoint|unexpected snapshot"):
        journal.audit_journal(root)
