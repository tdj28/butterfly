"""Real local child-process resource and parent-loss controls, no targets."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from butterfly.paired_supervisor import StageLimits, directory_bytes, process_table, supervise

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def usable_process_inventory():
    if os.name != "posix":
        pytest.skip("POSIX supervisor")
    try:
        process_table()
    except (OSError, subprocess.SubprocessError):
        pytest.skip("host blocks read-only process inventory; run live controls with required host access")


def run(tmp_path, code, **limits):
    output = tmp_path/"output"
    output.mkdir()
    return supervise([sys.executable, "-c", code], cwd=ROOT, evidence_directory=output,
        state_directory=output/"supervisor", environment={"PATH": os.defpath}, binding={"kind": "synthetic"},
        limits=StageLimits(**{**dict(wall_seconds=5., maximum_rss_bytes=256*1024**2,
            maximum_disk_bytes=8*1024**2, minimum_start_free_bytes=0, poll_seconds=.03, terminate_grace_seconds=.2), **limits}))


def test_normal_exit_retains_logs_and_cleanup_receipt(tmp_path):
    result = run(tmp_path, "print('completed',flush=True)")
    assert result["status"] == "completed" and result["returncode"] == 0 and result["owned_group_cleanup_verified"]
    assert (tmp_path/"output/supervisor/stdout.log").read_text().strip() == "completed"
    assert result["scientific_qualification"] is False


def test_nonzero_exit_is_incomplete(tmp_path):
    result = run(tmp_path, "raise SystemExit(3)")
    assert result["status"] == "incomplete" and result["returncode"] == 3 and result["reason"] == "nonzero-exit"


def test_wall_limit_does_not_touch_unrelated_session(tmp_path):
    other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
    try:
        result = run(tmp_path, "import time; time.sleep(30)", wall_seconds=.2)
        assert result["status"] == "incomplete" and result["reason"] == "wall-limit"
        assert result["owned_group_cleanup_verified"] and other.poll() is None
    finally:
        other.terminate()
        other.wait(timeout=5)


def test_rss_limit_is_observed_and_terminated(tmp_path):
    result = run(tmp_path, "import time; data=bytearray(64*1024**2); time.sleep(5)", maximum_rss_bytes=32*1024**2)
    assert result["reason"] == "rss-limit" and result["owned_group_cleanup_verified"]


def test_disk_limit_preserves_output(tmp_path):
    path = str(tmp_path/"output/payload.bin")
    result = run(tmp_path, f"import time; from pathlib import Path; Path({path!r}).write_bytes(b'x'*(2*1024**2)); time.sleep(5)",
                 maximum_disk_bytes=1024**2)
    assert result["reason"] == "disk-limit" and result["owned_group_cleanup_verified"]
    assert (tmp_path/"output/payload.bin").stat().st_size == 2*1024**2


def test_orphan_same_session_child_is_cleaned_before_leader_reap(tmp_path):
    code = "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'])"
    result = run(tmp_path, code)
    assert result["status"] == "incomplete" and result["reason"] == "live-descendants-after-leader-exit"
    assert result["owned_group_cleanup_verified"]


def test_symlink_evidence_rejected(tmp_path):
    (tmp_path/"link").symlink_to(ROOT, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        directory_bytes(tmp_path)


def test_invalid_limits_rejected_before_child_creation():
    for limits in (StageLimits(float("nan"), 1, 1, 0), StageLimits(1, -1, 1, 0), StageLimits(1, 1, 1, 0, poll_seconds=10)):
        with pytest.raises(ValueError):
            limits.validate()


def test_parent_guard_terminates_worker_when_supervisor_is_killed(tmp_path):
    output = tmp_path/"output"
    output.mkdir()
    ready = output/"guard-ready"
    worker = ("from butterfly.paired_supervisor import install_parent_guard; from pathlib import Path; import time; "
              f"guard=install_parent_guard(10); Path({str(ready)!r}).write_text('ready'); time.sleep(30)")
    controller = """
import os,sys
from butterfly.paired_supervisor import StageLimits,supervise
supervise([sys.executable,'-c',sys.argv[2]],cwd=sys.argv[3],evidence_directory=sys.argv[1],
 state_directory=sys.argv[1]+'/supervisor',environment={'PATH':os.defpath,'PYTHONPATH':sys.argv[3]+'/python'},
 binding={'kind':'synthetic-parent-loss'},limits=StageLimits(15,256*1024**2,8*1024**2,0,poll_seconds=.05))
"""
    parent = subprocess.Popen([sys.executable, "-c", controller, str(output), worker, str(ROOT)],
        env={"PATH": os.defpath, "PYTHONPATH": str(ROOT/"python")}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    child = None
    try:
        deadline = time.monotonic()+15
        while not ready.exists():
            if parent.poll() is not None or time.monotonic() > deadline:
                pytest.fail("parent-guard child did not start")
            time.sleep(.02)
        child = json.loads((output/"supervisor/ownership.json").read_bytes())["pid"]
        parent.kill()
        parent.communicate(timeout=5)
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            row = process_table().get(child)
            if row is None or row["state"].startswith("Z"):
                break
            time.sleep(.02)
        else:
            pytest.fail("worker survived parent pipe loss")
        assert not (output/"supervisor/terminal.json").exists()
    finally:
        if parent.poll() is None:
            parent.terminate()
            parent.communicate(timeout=5)


def test_worker_guard_deadline_works_even_with_live_parent(tmp_path):
    output = tmp_path/"output"
    output.mkdir()
    code = "from butterfly.paired_supervisor import install_parent_guard; import time; install_parent_guard(.2); time.sleep(30)"
    result = supervise([sys.executable, "-c", code], cwd=ROOT, evidence_directory=output,
        state_directory=output/"supervisor", environment={"PATH": os.defpath, "PYTHONPATH": str(ROOT/"python")},
        binding={"kind": "synthetic-guard-deadline"}, limits=StageLimits(5,256*1024**2,8*1024**2,0,poll_seconds=.03))
    assert result["status"] == "incomplete" and result["returncode"] == -9
    assert result["owned_group_cleanup_verified"]
