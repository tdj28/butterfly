"""Durable adaptive recording, tampering and actual process-loss controls."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pytest

from butterfly import paired_journal as io
from butterfly.paired_adaptive import collect_adaptive_sections
from butterfly.paired_adaptive_journal import AdaptiveJournal, audit_adaptive_journal, record_adaptive, validate_snapshot
from butterfly.paired_sections import CaptureSection
from butterfly.poincare import PoincareSection
from butterfly.paired_sampling import SECTIONS


def fixture():
    field = lambda x: np.column_stack((-x[:, 1], x[:, 0], np.zeros(len(x))))
    sections = {SECTIONS[0]: CaptureSection(PoincareSection((0, 1, 0), 0, -1),
        np.array([[-1., 0, 0]]), (0, 2), (1., 1.), .01, 1),
        SECTIONS[1]: CaptureSection(PoincareSection((1, 0, 0), 0, 1),
        np.array([[0, -1., 0]]), (1, 2), (1., 1.), .01, 1)}
    config = dict(method="DOP853", horizon=7., rtol=1e-10, atol=1e-12, max_step=.05,
        state_scales=[1., 1., 1.], gate_margin=1e-5, angle_margin=1e-6, escape_radius=1000.,
        maximum_steps=10000, maximum_field_evaluations=100000, maximum_events=1000, recording_interval=40)
    return field, sections, config


def record(path, **changes):
    field, sections, config = fixture()
    config.update(changes)
    return record_adaptive(field, [1., 0, 0], 901, sections, config, directory=path,
                           binding={"trial_id": "synthetic-a", "source": "synthetic-source"})


def test_roundtrip_preserves_all_arrays_and_final_completed_status(tmp_path):
    result, audit = record(tmp_path/"run")
    assert audit["status"] == "completed" and audit["durable_time"] == 7.
    for k, v in result.items():
        if isinstance(v, np.ndarray):
            np.testing.assert_array_equal(v, audit["snapshot"][k])
    for name in SECTIONS:
        for key, value in result["events"][name].items():
            np.testing.assert_array_equal(value, audit["snapshot"]["events"][name][key])
    assert len(list((tmp_path/"run").glob("journal-*.json"))) >= 4


def test_missing_terminal_never_qualifies_even_at_full_horizon(tmp_path):
    field, sections, config = fixture()
    sink = AdaptiveJournal(tmp_path/"run", [1., 0, 0], 901, sections, config, binding={})
    result = collect_adaptive_sections(field, [1., 0, 0], 901, sections, **config, progress=sink.append)
    audit = audit_adaptive_journal(tmp_path/"run")
    assert result["completed"] and audit["durable_time"] == 7 and audit["status"] == "incomplete"


def test_numerical_cap_is_preserved_as_incomplete(tmp_path):
    result, audit = record(tmp_path/"run", maximum_events=1)
    assert result["status"] == "failed" and audit["status"] == "incomplete"
    assert audit["durable_time"] == result["observed_until"] < 7
    assert audit["last_snapshot_status"] == "failed"


def test_existing_directory_and_external_binding_substitution_rejected(tmp_path):
    record(tmp_path/"run")
    with pytest.raises(FileExistsError):
        record(tmp_path/"run")
    with pytest.raises(ValueError, match="binding"):
        audit_adaptive_journal(tmp_path/"run", expected_binding={"source": "wrong"})
    with pytest.raises(ValueError, match="bound"):
        audit_adaptive_journal(tmp_path/"run", expected_started_sha256="0"*64)


@pytest.mark.parametrize("kind", ["seed", "trace", "event", "capture", "time", "status", "extra"])
def test_snapshot_semantics_reject_inconsistent_records(kind):
    field, sections, config = fixture()
    result = collect_adaptive_sections(field, [1., 0, 0], 901, sections, **config)
    bad = copy.deepcopy(result)
    if kind == "seed":
        bad["global_seed_ids"][0] += 1
    elif kind == "trace":
        bad["integration_states"][-1, 0] += .1
    elif kind == "event":
        bad["events"][SECTIONS[0]]["times"][0] = 0
    elif kind == "capture":
        bad["capture_times"][0, 0] = .1
    elif kind == "time":
        bad["observed_until"] += .1
    elif kind == "status":
        bad["completed"] = False
    else:
        bad["events"][SECTIONS[0]]["extra"] = np.zeros(1)
    with pytest.raises(ValueError):
        validate_snapshot(bad, np.array([1., 0, 0]), 901, sections, config)


def test_changed_committed_prefix_is_rejected(tmp_path):
    field, sections, config = fixture()
    snapshots = []
    collect_adaptive_sections(field, [1., 0, 0], 901, sections, **config, progress=snapshots.append)
    bad = copy.deepcopy(snapshots[1])
    bad["integration_states"][5, 0] += .1
    with pytest.raises(ValueError, match="trace"):
        validate_snapshot(bad, np.array([1., 0, 0]), 901, sections, config, snapshots[0])


def test_terminal_cannot_substitute_a_different_collector_result(tmp_path):
    field, sections, config = fixture()
    sink = AdaptiveJournal(tmp_path/"run", [1., 0, 0], 901, sections, config, binding={})
    result = collect_adaptive_sections(field, [1., 0, 0], 901, sections, **config, progress=sink.append)
    result["field_evaluations"] += 1
    with pytest.raises(ValueError, match="differs"):
        sink.finish(result)
    assert not (tmp_path/"run/terminal.json").exists()


def test_orphan_or_changed_raw_cannot_be_completed(tmp_path):
    record(tmp_path/"run")
    (tmp_path/"run/orphan.npz").write_bytes(b"incomplete")
    with pytest.raises(ValueError, match="completion"):
        audit_adaptive_journal(tmp_path/"run")
    record(tmp_path/"other")
    (tmp_path/"other/journal-000000.npz").write_bytes(b"bad raw")
    with pytest.raises(ValueError, match="hash/size"):
        audit_adaptive_journal(tmp_path/"other")


@pytest.mark.skipif(os.name != "posix", reason="SIGKILL control requires POSIX")
def test_sigkill_preserves_real_fsynced_prefix_without_completion(tmp_path):
    # Same production record_adaptive -> AdaptiveJournal path, with a test-only
    # pause immediately after the first successful durable callback.
    code = '''
import sys,time
from test_paired_adaptive_journal import fixture
from butterfly.paired_adaptive_journal import AdaptiveJournal,record_adaptive
field,sections,config=fixture()
original=AdaptiveJournal.append
def pause(self,result):
    original(self,result)
    time.sleep(30)
AdaptiveJournal.append=pause
record_adaptive(field,[1.,0,0],901,sections,config,directory=sys.argv[1],binding={})
'''
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(Path(__file__).parent), "python", "."]))
    process = subprocess.Popen([sys.executable, "-c", code, str(tmp_path/"run")], env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic()+15
        while not (tmp_path/"run/journal-000000.json").exists():
            if process.poll() is not None or time.monotonic() >= deadline:
                pytest.fail("child did not persist first snapshot")
            time.sleep(.02)
        process.kill()
        process.communicate(timeout=5)
        audit = audit_adaptive_journal(tmp_path/"run")
        assert audit["status"] == "incomplete" and audit["records"] == 1 and 0 < audit["durable_time"] < 7
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
