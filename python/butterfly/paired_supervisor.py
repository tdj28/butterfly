"""POSIX local-stage supervisor with sampled resource bounds and owned cleanup.

Runs only the caller's explicit argv/environment, never a shell. The session
leader is not reaped until cleanup, keeping its process-group ID reserved.
This is operational containment of trusted research code, not a sandbox for
hostile children that escape their process session. No scientific authority.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import time

from . import paired_journal as io
from ._process_guard import install_parent_guard


@dataclass(frozen=True)
class StageLimits:
    wall_seconds: float
    maximum_rss_bytes: int
    maximum_disk_bytes: int
    minimum_start_free_bytes: int
    poll_seconds: float = .25
    terminate_grace_seconds: float = 5.

    def validate(self):
        if (any(type(x) not in (int, float) or not 0 < x < float("inf") for x in
                (self.wall_seconds, self.poll_seconds, self.terminate_grace_seconds))
                or self.poll_seconds > 1 or self.terminate_grace_seconds > 10
                or any(type(x) is not int or x < 1 for x in
                       (self.maximum_rss_bytes, self.maximum_disk_bytes))
                or type(self.minimum_start_free_bytes) is not int or self.minimum_start_free_bytes < 0):
            raise ValueError("invalid local-stage limits")


def process_table():
    """Read only process identity/group, RSS and state; never argv or env."""
    result = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,pgid=,rss=,stat="], check=True,
                            capture_output=True, text=True, timeout=5)
    rows = {}
    for line in result.stdout.splitlines():
        pid, parent, group, rss, state = line.split()
        rows[int(pid)] = {"pid": int(pid), "parent": int(parent), "group": int(group),
                          "rss_bytes": int(rss)*1024, "state": state}
    return rows


def directory_bytes(directory):
    total = 0
    for base, dirs, files in os.walk(directory, followlinks=False):
        for name in (*dirs, *files):
            path = Path(base)/name
            try:
                info = path.lstat()
            except FileNotFoundError:
                continue  # a bounded transient temporary file may disappear
            if stat.S_ISLNK(info.st_mode) or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise ValueError("nonregular/symlink evidence entry")
            if stat.S_ISREG(info.st_mode):
                total += info.st_size
    return total


def _group_rows(rows, pid):
    return [r for r in rows.values() if r["group"] == pid]


def supervise(argv, *, cwd, evidence_directory, state_directory, environment, binding, limits):
    """Run one explicit local child; append logs, preserve every failure.

    RSS and disk are sampled stop thresholds, not kernel-enforced peak quotas.
    Limits may be exceeded between samples or while a filesystem query runs.
    Source-bound bounded writes and the production startup gate remain caller
    responsibilities. The child may spawn same-session children; all live
    members are cleaned up before reaping the reserved session leader.
    """
    limits.validate()
    if os.name != "posix" or signal.getsignal(signal.SIGCHLD) != signal.SIG_DFL:
        raise ValueError("POSIX with normal child reaping required")
    if (not argv or any(type(x) is not str or not x or "\0" in x for x in argv)
            or not isinstance(environment, dict) or any(type(k) is not str or type(v) is not str
                or not k or "=" in k or "\0" in k+v for k, v in environment.items())):
        raise ValueError("explicit argv and clean environment required")
    work, output, state_dir = (io._safe_path(p) for p in (cwd, evidence_directory, state_directory))
    if not work.is_dir() or not output.is_dir() or state_dir == output:
        raise ValueError("existing work/output directories and a fresh state subdirectory required")
    state_dir.relative_to(output)
    initial_bytes = directory_bytes(output)
    if initial_bytes >= limits.maximum_disk_bytes or shutil.disk_usage(output).free < limits.minimum_start_free_bytes:
        raise ValueError("insufficient stage disk reserve")
    metadata = {"schema": "butterfly.local-stage.v1", "argv": argv, "binding": binding, "limits": asdict(limits),
        "environment_keys": sorted(environment),
        "environment_sha256": hashlib.sha256(json.dumps(environment, sort_keys=True).encode()).hexdigest(),
        "automatic_retry": False, "started_unix": time.time(),
        "scope": "sampled resource supervision, not scientific qualification or hostile-process confinement"}
    json.dumps(metadata, allow_nan=False)
    state_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    io._sync_directory(state_dir.parent)
    io._json(state_dir/"started.json", metadata)
    process = None
    status, reason, cleanup = "failed", None, False
    started = time.monotonic()
    maximum_rss, maximum_disk, samples = 0, initial_bytes, 0
    returncode = None
    def terminate_owned():
        # Do not call Popen.poll here: it can reap the leader and make its
        # numeric PID/group available for reuse before child cleanup finishes.
        rows = process_table()
        leader = rows.get(process.pid)
        if leader is None or leader["group"] != process.pid:
            raise RuntimeError("owned unreaped session leader unavailable; cleanup not verified")
        if any(not r["state"].startswith("Z") for r in _group_rows(rows, process.pid)):
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            deadline = time.monotonic()+limits.terminate_grace_seconds
            while time.monotonic() < deadline:
                if not any(not r["state"].startswith("Z") for r in _group_rows(process_table(), process.pid)):
                    return True
                time.sleep(min(.05, limits.poll_seconds))
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            deadline = time.monotonic()+5
            while time.monotonic() < deadline:
                if not any(not r["state"].startswith("Z") for r in _group_rows(process_table(), process.pid)):
                    return True
                time.sleep(.05)
            return False
        return True
    with (state_dir/"stdout.log").open("xb") as stdout, (state_dir/"stderr.log").open("xb") as stderr, \
            (state_dir/"samples.jsonl").open("xb") as sample_log:
        for path in ("stdout.log", "stderr.log", "samples.jsonl"):
            (state_dir/path).chmod(0o600)
        try:
            process = subprocess.Popen(argv, cwd=work, env=environment, stdin=subprocess.PIPE,
                stdout=stdout, stderr=stderr, start_new_session=True)
            io._json(state_dir/"ownership.json", {"pid": process.pid, "process_group": process.pid,
                "leader_reaped_only_after_cleanup": True})
            while True:
                rows = process_table()
                if process.pid not in rows or rows[process.pid]["group"] != process.pid:
                    raise RuntimeError("lost owned session leader")
                group = _group_rows(rows, process.pid)
                rss, disk = sum(r["rss_bytes"] for r in group), directory_bytes(output)
                elapsed = time.monotonic()-started
                maximum_rss, maximum_disk = max(maximum_rss, rss), max(maximum_disk, disk)
                samples += 1
                sample_log.write((json.dumps({"elapsed_seconds": elapsed, "rss_bytes": rss, "disk_bytes": disk,
                    "group_members": len(group), "leader_state": rows[process.pid]["state"]})+"\n").encode())
                sample_log.flush()
                os.fsync(sample_log.fileno())
                if elapsed > limits.wall_seconds:
                    reason = "wall-limit"
                    break
                if rss > limits.maximum_rss_bytes:
                    reason = "rss-limit"
                    break
                if disk > limits.maximum_disk_bytes:
                    reason = "disk-limit"
                    break
                if rows[process.pid]["state"].startswith("Z"):
                    if any(r["pid"] != process.pid and not r["state"].startswith("Z") for r in group):
                        reason = "live-descendants-after-leader-exit"
                    else:
                        status = "exited"
                    break
                time.sleep(limits.poll_seconds)
        except (Exception, KeyboardInterrupt) as error:
            reason = {"type": type(error).__name__, "message": str(error)}
            status = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        finally:
            if process is not None:
                try:
                    cleanup = terminate_owned()
                    if cleanup:
                        returncode = process.wait(timeout=5)
                        process.stdin.close()
                except (Exception, KeyboardInterrupt) as error:
                    cleanup = False
                    reason = {"prior": reason, "cleanup_error": type(error).__name__, "message": str(error)}
                finally:
                    if process.stdin is not None:
                        process.stdin.close()
            for stream in (stdout, stderr, sample_log):
                stream.flush()
                os.fsync(stream.fileno())
    complete = status == "exited" and returncode == 0 and cleanup
    if status == "exited" and returncode != 0 and reason is None:
        reason = "nonzero-exit"
    receipt = {"status": "completed" if complete else "incomplete", "reason": reason,
        "returncode": returncode, "owned_group_cleanup_verified": cleanup,
        "elapsed_seconds": time.monotonic()-started, "maximum_sampled_rss_bytes": maximum_rss,
        "maximum_sampled_disk_bytes": maximum_disk, "samples": samples, "binding": binding,
        "scientific_qualification": False, "automatic_retry": False}
    io._json(state_dir/"terminal.json", receipt)
    return receipt
