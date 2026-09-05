#!/usr/bin/env python3
"""Single-create, exact-owned EXP-477 RunPod lifecycle and launchd watchdog.

This module does not select scientific inputs or execute a workload by itself.
The controller supplies a frozen staging/qualification/collection callback to
run_owned_worker(). The callback receives only the owned provider record and
a progress reporter, and must retrieve verified raw evidence before returning.

The launchd watchdog survives controller/app exit, not loss of power, network,
or the local host. It is a local safeguard, not a provider-side billing TTL.
No control-plane credential is copied to a worker or placed in a record.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import uuid

try:
    from scripts import runpodctl
except ModuleNotFoundError:  # Frozen local watchdog copy contains these two files.
    import runpodctl


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "butterfly.runpod-symbolic-worker.v1"
NAME_PREFIX = "butterfly-exp477-"
CONTROLLER_LOCK_PATH = Path(f"/private/tmp/butterfly-exp477-controller-{os.getuid()}.lock")
POD_ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
CANDIDATE_HASH = "71aab52016abc8163887b2bdfd4e8124bde0e436be2239751f19d29bed490012"
CANDIDATE_BYTES = 867378


class LifecycleError(RuntimeError):
    pass


class OwnershipError(LifecycleError):
    pass


@contextmanager
def single_controller_lock(path=None):
    """One EXP-477 controller across state directories and local checkouts.

    The empty, same-user 0600 lock file is retained intentionally: unlinking a
    held flock file lets a later process create a different inode and bypass
    exclusion. No provider call occurs here. Existing links, nonempty files,
    foreign owners, or unsafe permissions are rejected rather than modified.
    """
    path = CONTROLLER_LOCK_PATH if path is None else Path(path)
    try:
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    except OSError:
        raise LifecycleError("cannot open the task-wide controller lock safely") from None
    try:
        metadata = os.fstat(descriptor)
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid()
                or metadata.st_nlink != 1 or metadata.st_size != 0 or metadata.st_mode & 0o077):
            raise LifecycleError("task-wide lock is not an empty private same-user regular file")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise LifecycleError("another EXP-477 controller holds the task-wide lock") from None
        current = path.lstat()
        if (current.st_dev, current.st_ino) != (metadata.st_dev, metadata.st_ino):
            raise LifecycleError("task-wide controller lock path changed during acquisition")
        try:
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def atomic_json(path: Path, value: dict):
    payload = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    descriptor, temporary = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Store:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / "lifecycle.json"

    def read(self):
        return json.loads(self.path.read_bytes())

    @contextmanager
    def locked(self):
        with (self.directory / "state.lock").open("a+b") as stream:
            os.chmod(stream.name, 0o600)
            fcntl.flock(stream, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)

    def update(self, **changes):
        with self.locked():
            record = self.read()
            record.update(changes)
            atomic_json(self.path, record)
        return record


def controller_registry_path():
    return CONTROLLER_LOCK_PATH.with_suffix(".active.json")


def require_no_unresolved_controller():
    """Keep an ambiguous create blocked after a crash releases its flock.

    A previous controller may have died between POST and receiving the ID.
    Inventory alone cannot prove such an in-flight request was rejected.
    Only that record's verified termination permits a new state directory.
    """
    path = controller_registry_path()
    if not os.path.lexists(path):
        return
    metadata = path.lstat()
    if (not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid()
            or metadata.st_nlink != 1 or metadata.st_size > 8192 or metadata.st_mode & 0o077):
        raise LifecycleError("active-controller registry is not a private same-user regular file")
    try:
        registry = json.loads(path.read_bytes())
        if (registry.get("schema") != "butterfly.exp477-controller-registry.v1"
                or not isinstance(registry.get("state_directory"), str)
                or not Path(registry["state_directory"]).is_absolute()):
            raise ValueError("invalid registry")
        previous = Store(registry["state_directory"]).read()
        if previous.get("schema") != SCHEMA or previous.get("nonce") != registry.get("nonce"):
            raise ValueError("registry identity mismatch")
    except (OSError, ValueError, TypeError, KeyError):
        raise LifecycleError("previous controller record cannot be verified; no new worker may launch") from None
    if previous.get("termination_verified") is not True:
        raise LifecycleError("an earlier EXP-477 controller has unverified termination; no new create is permitted")


def register_controller(store):
    # The task-wide flock remains held across this check, registration, and run.
    require_no_unresolved_controller()
    record = store.read()
    atomic_json(controller_registry_path(), {
        "schema": "butterfly.exp477-controller-registry.v1", "nonce": record["nonce"],
        "state_directory": str(store.directory.resolve()),
    })


def finite_number(value, name, *, minimum=0.0, maximum=None):
    if isinstance(value, bool):
        raise LifecycleError(f"{name} must be finite and within its declared bounds")
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        raise LifecycleError(f"{name} must be finite and within its declared bounds") from None
    if not math.isfinite(number) or number < minimum or (maximum is not None and number > maximum):
        raise LifecycleError(f"{name} must be finite and within its declared bounds")
    return number


def validate_plan(plan):
    numeric = ("maximum_hourly_usd", "maximum_spend_usd", "maximum_lifetime_seconds",
               "maximum_no_progress_seconds", "heartbeat_timeout_seconds", "storage_transfer_reserve_usd")
    if not isinstance(plan, dict) or any(type(plan.get(name)) not in (int, float) for name in numeric):
        raise LifecycleError("plan requires finite numeric lifecycle limits")
    if plan.get("experiment_id") != "EXP-477":
        raise LifecycleError("this lifecycle is limited to EXP-477 raw collection")
    for name in ("image", "gpu_type"):
        if not isinstance(plan.get(name), str) or not plan[name] or "\n" in plan[name]:
            raise LifecycleError(f"a frozen {name} is required")
    if not re.fullmatch(r"[0-9a-f]{40}", plan.get("source_commit", "")):
        raise LifecycleError("a full frozen source commit is required")
    finite_number(plan["maximum_hourly_usd"], "maximum_hourly_usd", minimum=0.001, maximum=0.50)
    finite_number(plan["maximum_spend_usd"], "maximum_spend_usd", minimum=0.01, maximum=3.0)
    finite_number(plan["maximum_lifetime_seconds"], "maximum_lifetime_seconds", minimum=1, maximum=10800)
    finite_number(plan["maximum_no_progress_seconds"], "maximum_no_progress_seconds", minimum=1, maximum=1800)
    finite_number(plan["heartbeat_timeout_seconds"], "heartbeat_timeout_seconds", minimum=10, maximum=120)
    reserve = finite_number(plan["storage_transfer_reserve_usd"], "storage_transfer_reserve_usd", minimum=0.01)
    exposure = plan["maximum_hourly_usd"] * plan["maximum_lifetime_seconds"] / 3600 + reserve
    if exposure > plan["maximum_spend_usd"]:
        raise LifecycleError("worst-case compute plus declared storage/transfer reserve exceeds spend cap")
    return plan


def process_start(pid):
    """Bind a PID to ps start time; kill(pid,0) alone cannot detect PID reuse."""
    if type(pid) is not int or pid <= 1:
        return None
    try:
        os.kill(pid, 0)
        result = subprocess.run(["/bin/ps", "-p", str(pid), "-o", "lstart="],
                                capture_output=True, text=True, check=False, timeout=5,
                                env={**os.environ, "LC_ALL": "C"})
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def identity_alive(identity, lookup=process_start):
    return (isinstance(identity, dict) and type(identity.get("pid")) is int
            and isinstance(identity.get("ps_start"), str) and bool(identity["ps_start"])
            and lookup(identity["pid"]) == identity["ps_start"])


def write_heartbeat(store, *, role="controller", now=None):
    record = store.read()
    pid = os.getpid()
    start = process_start(pid)
    if start is None:
        raise LifecycleError("cannot establish process start identity")
    value = {"nonce": record["nonce"], "pid": pid, "ps_start": start,
             "time": time.time() if now is None else now}
    atomic_json(store.directory / f"{role}-heartbeat.json", value)
    return value


def heartbeat_record(store, role):
    try:
        return json.loads((store.directory / f"{role}-heartbeat.json").read_bytes())
    except (OSError, ValueError):
        return None


def fresh_identity(heartbeat, record, now, *, maximum_age, lookup=process_start):
    if not heartbeat or heartbeat.get("nonce") != record["nonce"]:
        return False
    try:
        age = now - finite_number(heartbeat.get("time"), "heartbeat time")
    except LifecycleError:
        return False
    return -5 <= age <= maximum_age and identity_alive(heartbeat, lookup)


def watchdog_reason(record, heartbeat, now, *, lookup=process_start):
    """Pure policy decision: None means healthy, not permission to create."""
    if record.get("termination_verified"):
        return "already-terminated"
    if record.get("controller_finished"):
        return "controller-finished"
    if not fresh_identity(heartbeat, record, now,
                          maximum_age=record["plan"]["heartbeat_timeout_seconds"], lookup=lookup):
        return "controller-missing-stale-or-pid-reused"
    if heartbeat.get("pid") != record["controller"]["pid"] or heartbeat.get("ps_start") != record["controller"]["ps_start"]:
        return "controller-identity-mismatch"
    origin = record.get("create_attempted_at", record["prepared_at"])
    if now < origin - 5 or now - origin >= record["plan"]["maximum_lifetime_seconds"]:
        return "lifetime-limit-or-clock-regression"
    if now - record["last_progress_at"] >= record["plan"]["maximum_no_progress_seconds"]:
        return "no-progress-limit"
    rate = record.get("actual_hourly_usd")
    if rate is not None:
        cost = max(0, now - origin) * rate / 3600 + record["plan"]["storage_transfer_reserve_usd"]
        if cost >= record["plan"]["maximum_spend_usd"]:
            return "spend-limit"
    return None


def prepare_store(directory, plan, *, now=None):
    validate_plan(plan)
    directory = Path(directory)
    directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    os.chmod(directory, 0o700)
    nonce = uuid.uuid4().hex
    controller = {"pid": os.getpid(), "ps_start": process_start(os.getpid())}
    if controller["ps_start"] is None:
        raise LifecycleError("cannot establish controller process identity")
    timestamp = time.time() if now is None else now
    store = Store(directory)
    atomic_json(store.path, {
        "schema": SCHEMA, "nonce": nonce, "name": NAME_PREFIX + nonce,
        "plan": plan, "controller": controller, "prepared_at": timestamp,
        "last_progress_at": timestamp, "create_attempted": False,
        "pod_id": None, "termination_verified": False,
        "controller_finished": False, "preexisting_ids": [],
    })
    key = directory / "task_ed25519"
    subprocess.run(["/usr/bin/ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C",
                    NAME_PREFIX + nonce, "-f", str(key)], check=True, timeout=10,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.chmod(key, 0o600)
    public_key = key.with_suffix(".pub").read_text().strip()
    if not re.fullmatch(r"ssh-ed25519 [A-Za-z0-9+/=]+ [A-Za-z0-9_-]+", public_key):
        raise LifecycleError("generated task public key has unexpected format")
    store.update(public_key=public_key, public_key_sha256=hashlib.sha256(public_key.encode()).hexdigest())
    write_heartbeat(store)
    return store


def provider_id(value):
    if not isinstance(value, str) or not POD_ID.fullmatch(value):
        raise OwnershipError("provider returned an invalid resource ID")
    return value


def inventory(request=runpodctl.request_json):
    rows = request("GET", f"{runpodctl.REST_BASE}/pods?includeMachine=true")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise LifecycleError("provider inventory has an unexpected shape")
    identifiers = [provider_id(row.get("id")) for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise LifecycleError("provider inventory contains duplicate IDs")
    return rows


def direct_lookup(pod_id, request=runpodctl.request_json):
    identifier = provider_id(pod_id)
    try:
        row = request("GET", f"{runpodctl.REST_BASE}/pods/{urllib.parse.quote(identifier, safe='')}")
    except SystemExit as error:
        if str(error).startswith("Runpod API returned HTTP 404:"):
            return None
        raise
    if not isinstance(row, dict) or row.get("id") != identifier:
        raise OwnershipError("direct provider lookup did not return the exact requested ID")
    return row


def assert_owned(record, pod):
    if (not record.get("create_attempted") or record.get("pod_id") in record["preexisting_ids"]
            or pod.get("id") != record.get("pod_id") or pod.get("name") != record["name"]):
        raise OwnershipError("ID/name/prelaunch ownership mismatch; refusing resource mutation")
    provider_id(record["pod_id"])


def bind_ownership(store, identifier, basis):
    """Preserve immutable creation identity separately from mutable liveness."""
    record = store.read()
    identifier = provider_id(identifier)
    if identifier in record["preexisting_ids"]:
        raise OwnershipError("cannot bind a pre-existing resource as newly created")
    binding = {"schema": "butterfly.runpod-ownership.v1", "nonce": record["nonce"],
               "pod_id": identifier, "name": record["name"],
               "preexisting_ids": record["preexisting_ids"], "basis": basis}
    path = store.directory / "ownership.json"
    try:
        with path.open("x", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump(binding, stream, sort_keys=True, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        existing = json.loads(path.read_bytes())
        if any(existing.get(key) != binding[key] for key in ("schema", "nonce", "pod_id", "name", "preexisting_ids")):
            raise OwnershipError("immutable ownership receipt conflicts with this identity") from None
    store.update(pod_id=identifier, ownership_basis=basis)


def owned_record(store):
    record = store.read()
    try:
        binding = json.loads((store.directory / "ownership.json").read_bytes())
    except (OSError, ValueError):
        raise OwnershipError("immutable ownership receipt is unavailable") from None
    if (binding.get("schema") != "butterfly.runpod-ownership.v1"
            or any(binding.get(key) != record.get(key) for key in ("nonce", "pod_id", "name", "preexisting_ids"))):
        raise OwnershipError("mutable ledger differs from immutable creation identity")
    return record


def actual_contract(record, pod):
    assert_owned(record, pod)
    rate = pod.get("adjustedCostPerHr", pod.get("costPerHr"))
    rate = finite_number(rate, "actual hourly rate", maximum=record["plan"]["maximum_hourly_usd"])
    if (pod.get("interruptible") is not False or pod.get("containerDiskInGb") != 20
            or pod.get("volumeInGb") != 0 or pod.get("networkVolumeId")
            or pod.get("networkVolume") or pod.get("ports") != ["22/tcp"]):
        raise LifecycleError("received pod violates on-demand/disk/no-volume/SSH-only contract")
    if not (pod.get("cloudType") == "SECURE" or (pod.get("machine") or {}).get("secureCloud") is True):
        raise LifecycleError("provider did not confirm secure-cloud placement")
    if (pod.get("gpu") or {}).get("count", pod.get("gpuCount")) != 1:
        raise LifecycleError("provider did not confirm exactly one GPU")
    if pod.get("image", pod.get("imageName")) != record["plan"]["image"]:
        raise LifecycleError("provider returned a different or unidentified container image")
    if (pod.get("machine") or {}).get("gpuTypeId", (pod.get("gpu") or {}).get("id")) != record["plan"]["gpu_type"]:
        raise LifecycleError("provider returned a different or unidentified GPU type")
    return rate


def create_payload(record):
    return {"name": record["name"], "imageName": record["plan"]["image"],
            "cloudType": "SECURE", "computeType": "GPU", "gpuCount": 1,
            "gpuTypeIds": [record["plan"]["gpu_type"]], "gpuTypePriority": "custom",
            "interruptible": False, "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["22/tcp"], "supportPublicIp": True, "minVCPUPerGPU": 2,
            "minRAMPerGPU": 8, "env": {"PUBLIC_KEY": record["public_key"]}}


def require_watchdog(store, *, now=None, lookup=process_start):
    record = store.read()
    stamp = time.time() if now is None else now
    heartbeat = heartbeat_record(store, "watchdog")
    if not fresh_identity(heartbeat, record, stamp, maximum_age=15, lookup=lookup):
        raise LifecycleError("durable watchdog has no fresh, live PID/start-time acknowledgement")
    if heartbeat["pid"] == record["controller"]["pid"]:
        raise LifecycleError("watchdog must be a process independent of the controller")


def reconcile_ambiguous_create(store, request=runpodctl.request_json):
    """Never retry POST; recover only a new exact-name AND public-key match."""
    record = store.read()
    if not record.get("create_attempted") or record.get("pod_id"):
        return record.get("pod_id")
    matches = []
    for row in inventory(request):
        if row["id"] in record["preexisting_ids"] or row.get("name") != record["name"]:
            continue
        candidate = direct_lookup(row["id"], request)
        if candidate is not None and (candidate.get("env") or {}).get("PUBLIC_KEY") == record["public_key"]:
            matches.append(candidate)
    if len(matches) > 1:
        raise OwnershipError("multiple exact create identities found; no automatic mutation is safe")
    if not matches:
        store.update(ambiguous_create_reconciliation="no fully bound match yet")
        return None
    identifier = provider_id(matches[0]["id"])
    bind_ownership(store, identifier, "new inventory ID plus exact create name and public key")
    store.update(ambiguous_create_reconciliation="recovered")
    return identifier


def provision_once(store, request=runpodctl.request_json, *, lookup=process_start, now=None):
    timestamp = lambda: time.time() if now is None else now
    stamp = timestamp()
    require_watchdog(store, now=stamp, lookup=lookup)
    rows = inventory(request)
    stamp = timestamp()
    with store.locked():
        record = store.read()
        if record["create_attempted"]:
            raise LifecycleError("create already attempted; this record never permits another POST")
        if any(isinstance(row.get("name"), str) and row["name"].startswith(NAME_PREFIX) for row in rows):
            raise LifecycleError("an EXP-477 worker name already exists; refusing another worker without mutating it")
        if watchdog_reason(record, heartbeat_record(store, "controller"), stamp, lookup=lookup):
            raise LifecycleError("controller policy is not healthy before create")
        record.update(preexisting_ids=[row["id"] for row in rows], create_attempted=True,
                      create_attempted_at=stamp, last_progress_at=stamp)
        atomic_json(store.path, record)  # Durable BEFORE the one and only POST.
    # Recheck actual watchdog liveness immediately before the create request.
    try:
        require_watchdog(store, now=timestamp(), lookup=lookup)
    except LifecycleError:
        store.update(create_aborted_before_post=True)
        raise
    try:
        response = request("POST", f"{runpodctl.REST_BASE}/pods", payload=create_payload(record))
        if not isinstance(response, dict):
            raise OwnershipError("create response did not contain an ownership record")
        identifier = provider_id(response.get("id"))
        if identifier in record["preexisting_ids"] or response.get("name") != record["name"]:
            raise OwnershipError("create response ID/name does not establish a new task-owned resource")
        bind_ownership(store, identifier, "ID and exact name returned by sole create request")
        current = direct_lookup(identifier, request)
        if current is None:
            raise LifecycleError("created pod vanished before contract qualification")
        rate = actual_contract(owned_record(store), current)
        store.update(actual_hourly_usd=rate, contract_qualified=True)
        return current
    except (Exception, SystemExit):
        store.update(create_or_contract_failed=True)
        if store.read().get("pod_id") is None:
            reconcile_ambiguous_create(store, request)
        raise


def terminate_owned(store, request=runpodctl.request_json, *, attempts=6, pause=time.sleep):
    record = store.read()
    identifier = record.get("pod_id")
    if identifier is None:
        identifier = reconcile_ambiguous_create(store, request)
    if identifier is None:
        if not record.get("create_attempted") or record.get("create_aborted_before_post"):
            store.update(termination_verified=True, termination_reason="no create request was issued")
            return True
        store.update(termination_verified=False, teardown_error="create outcome remains unresolved")
        return False
    record = owned_record(store)
    pod = direct_lookup(identifier, request)
    if pod is not None:
        assert_owned(record, pod)
        try:
            request("DELETE", f"{runpodctl.REST_BASE}/pods/{urllib.parse.quote(identifier, safe='')}")
            # request_json does not expose HTTP status; do not fabricate a 204 field.
            store.update(delete_request_completed=True)
        except (Exception, SystemExit):
            # Another owned teardown may have raced us, or a timed-out DELETE
            # may have succeeded. Neither is proof: perform both absence checks.
            store.update(delete_request_completed=False, delete_response="failed or uncertain; checking exact-ID absence")
    for index in range(attempts):
        current = direct_lookup(identifier, request)
        rows = inventory(request)
        if current is None and identifier not in {row["id"] for row in rows}:
            store.update(termination_verified=True, terminated_at=time.time(),
                         post_delete_direct_lookup="HTTP 404", post_delete_inventory_ids=[row["id"] for row in rows],
                         unrelated_resources_mutated=False, persistent_volume_requested=False)
            return True
        if current is not None:
            assert_owned(owned_record(store), current)
        if index + 1 < attempts:
            pause(5)
    store.update(termination_verified=False, teardown_error="direct lookup and inventory did not both confirm absence")
    return False


def launchd_watchdog(store, *, root=ROOT, timeout=25):
    if sys.platform != "darwin":
        raise LifecycleError("durable watchdog requires macOS launchd; no detached-process substitute")
    runtime = store.directory / "watchdog-runtime"
    runtime.mkdir(mode=0o700)
    for source, leaf in ((Path(__file__), "runpod_symbolic_worker.py"),
                         (Path(runpodctl.__file__), "runpodctl.py")):
        shutil.copyfile(source, runtime / leaf)
        os.chmod(runtime / leaf, 0o600)
    record = store.read()
    label = "io.butterfly.exp477." + record["nonce"]
    document = {
        "Label": label,
        "ProgramArguments": ["/usr/bin/caffeinate", "-i", "-s", sys.executable, "-B",
                             str(runtime / "runpod_symbolic_worker.py"), "watchdog", "--state-dir", str(store.directory)],
        "WorkingDirectory": str(root), "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False}, "ThrottleInterval": 10,
        "StandardOutPath": str(store.directory / "watchdog.stdout"),
        "StandardErrorPath": str(store.directory / "watchdog.stderr"),
    }
    plist = store.directory / "watchdog.plist"
    with plist.open("xb") as stream:
        stream.write(plistlib.dumps(document))
    os.chmod(plist, 0o600)
    for leaf in ("watchdog.stdout", "watchdog.stderr"):
        with (store.directory / leaf).open("xb"):
            pass
        os.chmod(store.directory / leaf, 0o600)
    store.update(launchd_label=label, launchd_service=f"gui/{os.getuid()}/{label}")
    subprocess.run(["/bin/launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist)],
                   check=True, capture_output=True, timeout=10)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            require_watchdog(store)
            return
        except LifecycleError:
            time.sleep(0.2)
    raise LifecycleError("launchd watchdog did not establish independent liveness before the deadline")


def retire_watchdog(store):
    record = store.read()
    if not record.get("termination_verified"):
        raise LifecycleError("cannot retire watchdog while cloud termination is unconfirmed")
    service = record.get("launchd_service")
    if service:
        expected = f"gui/{os.getuid()}/io.butterfly.exp477.{record['nonce']}"
        if service != expected:
            raise OwnershipError("launchd service does not match this task's unique record")
        subprocess.run(["/bin/launchctl", "bootout", service], check=False, capture_output=True, timeout=10)
    # The task key is local and has no authority outside this terminated worker.
    # Retain it in the private record directory for explicit operator retirement;
    # it is never included in a transfer/retrieval or public receipt allowlist.


def watchdog_loop(store):
    while True:
        write_heartbeat(store, role="watchdog")
        record = store.read()
        if record.get("termination_verified"):
            return 0
        reason = watchdog_reason(record, heartbeat_record(store, "controller"), time.time())
        if reason is None and record.get("pod_id"):
            try:
                pod = direct_lookup(record["pod_id"])
                if pod is None:
                    reason = "owned-pod-no-longer-present"
                else:
                    actual_contract(owned_record(store), pod)
            except LifecycleError:
                reason = "actual-contract-or-ownership-check-failed"
        if reason is not None:
            store.update(watchdog_teardown_reason=reason)
            try:
                if terminate_owned(store):
                    return 0
            except (Exception, SystemExit):
                store.update(watchdog_last_error="teardown unconfirmed; only recorded resource may be retried")
        time.sleep(5)


def _run_owned_worker_locked(plan, state_directory, workload, *, request,
                             start_watchdog, stop_watchdog):
    """Execute one supplied raw-collection callback, always attempting teardown.

    workload(pod, store, progress) must stage only prevalidated inputs, require
    GPU qualification success, collect without CPU fitting, and retrieve/hash
    check raw files. progress(label) must represent actual progress, not a timer.
    Controller heartbeats are separate from that no-progress signal.
    """
    store = prepare_store(state_directory, plan)
    register_controller(store)
    stop = threading.Event()

    def pulse():
        while not stop.wait(3):
            write_heartbeat(store)

    thread = threading.Thread(target=pulse, name="exp477-controller-heartbeat", daemon=True)
    thread.start()

    def progress(label):
        if not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", label):
            raise LifecycleError("progress label must be a short non-sensitive token")
        store.update(last_progress_at=time.time(), progress_label=label)

    try:
        start_watchdog(store)
        pod = provision_once(store, request)
        result = workload(pod, store, progress)
        store.update(workload_returned=True)
        return result
    finally:
        store.update(controller_finished=True)
        try:
            terminated = terminate_owned(store, request)
        except (Exception, SystemExit):
            store.update(teardown_error="controller teardown unconfirmed; watchdog retained")
            terminated = False
        stop.set()
        thread.join(timeout=5)
        if terminated:
            stop_watchdog(store)
        else:
            raise LifecycleError("owned worker termination is unconfirmed; durable watchdog remains active")


def run_owned_worker(plan, state_directory, workload, *, request=runpodctl.request_json,
                     start_watchdog=launchd_watchdog, stop_watchdog=retire_watchdog):
    """Hold task-wide exclusion before any preparation/readiness/provisioning.

    See _run_owned_worker_locked for the callback's raw-retrieval contract.
    A new state directory does not grant permission for a simultaneous worker.
    """
    with single_controller_lock():
        require_no_unresolved_controller()
        return _run_owned_worker_locked(plan, state_directory, workload, request=request,
                                         start_watchdog=start_watchdog, stop_watchdog=stop_watchdog)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("watchdog",))
    parser.add_argument("--state-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        return watchdog_loop(Store(args.state_dir))
    except (Exception, SystemExit):
        # launchd restarts a failing watchdog; no provider response/key is logged.
        print("watchdog failed; launchd restart required", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
