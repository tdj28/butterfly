"""One-use local parent channel, loaded by hash before scientific imports.

This authenticates an ordinary invocation of the frozen controller on a trusted
host, not a hostile same-user debugger, modified interpreter, or forged provider.
Saved JSON, a matching checksum, and a socket supplied by another program do
not by themselves authorize the numerical worker.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import struct
import subprocess
import sys
import time


MAXIMUM_MESSAGE_BYTES = 65536
HANDSHAKE_SECONDS = 10.
STAGES = ("qualification", "collection", "analysis")
# Independent anchor in frozen worker source, not chosen by the received JSON.
# The controller computes runtime hashes dynamically, so this is not a cycle.
CONTROLLER_SOURCE_SHA256 = "0ec482d73867e91c314e2c3ef9318c64a88300bda164967ffd755ce22f8b42ac"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def receive(channel):
    deadline = time.monotonic()+HANDSHAKE_SECONDS
    def exact(n):
        parts = bytearray()
        while len(parts) < n:
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise TimeoutError("authorization message deadline exceeded")
            channel.settimeout(remaining)
            block = channel.recv(n-len(parts))
            if not block:
                raise ValueError("authorization channel closed before complete message")
            parts.extend(block)
        return bytes(parts)
    length = struct.unpack("!I", exact(4))[0]
    if not 0 < length <= MAXIMUM_MESSAGE_BYTES:
        raise ValueError("authorization message exceeds bound")
    raw = exact(length)
    value = json.loads(raw)
    if canonical(value) != raw:
        raise ValueError("authorization message is not canonical finite JSON")
    return value


def send(channel, value):
    raw = canonical(value)
    if not 0 < len(raw) <= MAXIMUM_MESSAGE_BYTES:
        raise ValueError("authorization message exceeds bound")
    channel.sendall(struct.pack("!I", len(raw))+raw)


def peer_pid(channel):
    if channel.family != socket.AF_UNIX or channel.type != socket.SOCK_STREAM:
        raise ValueError("local stream socketpair required")
    if sys.platform == "darwin":
        # XNU sys/un.h: SOL_LOCAL=0, LOCAL_PEERPID=2; observed on target Mac.
        return struct.unpack("i", channel.getsockopt(0, 2, struct.calcsize("i")))[0]
    if sys.platform.startswith("linux"):
        # unix(7): credentials are captured at socketpair creation, before spawn.
        return struct.unpack("3i", channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))[0]
    raise ValueError("parent authorization requires qualified macOS or Linux")


def process_executable(pid):
    """Actual OS image path, not the caller-controlled argv[0] string."""
    if sys.platform.startswith("linux"):
        return Path(f"/proc/{pid}/exe").resolve(strict=True)
    if sys.platform == "darwin":
        import ctypes
        lib = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        lib.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        lib.proc_pidpath.restype = ctypes.c_int
        output = ctypes.create_string_buffer(4096)
        if lib.proc_pidpath(pid, output, len(output)) <= 0:
            raise ValueError("actual parent executable identity unavailable")
        return Path(os.fsdecode(output.value)).resolve(strict=True)
    raise ValueError("unsupported process identity platform")


def verify_parent(pid, argv, contract, kind):
    """Anchor parent PID in the kernel, argv in ps, script bytes in the bundle."""
    controller = contract["controller"]
    if controller["sha256"] != CONTROLLER_SOURCE_SHA256:
        raise ValueError("controller differs from independently frozen worker authority")
    if (pid != os.getppid() or type(pid) is not int or pid <= 1 or not isinstance(argv, list)
            or len(argv) < 5 or any(type(a) is not str or not a or any(c.isspace() for c in a) for a in argv)
            or argv[1] != "-B" or argv[2] != controller["path"]
            or Path(argv[0]).resolve(strict=True) != Path(contract["interpreter"]["path"])
            or argv.count("--mode") != 1 or argv.index("--mode")+1 >= len(argv)
            or argv[argv.index("--mode")+1] != ("execute" if kind == "target" else "control")):
        raise ValueError("authorization peer is not the declared ordinary controller invocation")
    path = Path(controller["path"])
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != controller["sha256"]:
        raise ValueError("controller source differs from runtime binding")
    if process_executable(pid) != Path(contract["interpreter"]["path"]):
        raise ValueError("actual parent executable differs from the bound interpreter")
    actual = subprocess.run(["/bin/ps", "-ww", "-p", str(pid), "-o", "command="],
        check=True, capture_output=True, text=True, timeout=5).stdout.strip()
    if actual != " ".join(argv) or os.getppid() != pid:
        raise ValueError("actual parent argv differs from bound controller invocation")


def validate_grant(grant, phase, runtime_sha256):
    if (grant.get("schema") != "butterfly.paired-phase-grant.v1" or grant.get("phase") != phase
            or phase not in STAGES or grant.get("kind") not in ("target", "analytic-circle")
            or grant.get("runtime_contract_sha256") != runtime_sha256):
        raise ValueError("phase authorization binding mismatch")
    for name in ("plan_sha256", "design_sha256", "campaign_slot_sha256"):
        if re.fullmatch("[0-9a-f]{64}", grant.get(name, "")) is None:
            raise ValueError("full phase grant hashes required")
    if re.fullmatch("[0-9a-f]{40}", grant.get("source_commit", "")) is None:
        raise ValueError("full phase source binding required")
    wall = grant["limits"]["wall_seconds"]
    remaining = grant["deadline_monotonic"]-time.monotonic()
    if type(wall) not in (int, float) or not 0 < remaining <= wall <= 14400:
        raise ValueError("phase grant deadline is expired or exceeds bounded policy")
    if grant["kind"] == "target":
        for name in ("review_sha256", "preflight_sha256", "input_contract_sha256"):
            if re.fullmatch("[0-9a-f]{64}", grant.get(name, "")) is None:
                raise ValueError("target grant needs review, setup and input bindings")
        if type(grant.get("input_root")) is not str:
            raise ValueError("target input root required")
    elif (grant.get("review_sha256") is not None or grant.get("input_root") is not None
            or grant.get("input_contract_sha256") is not None or grant["source_commit"] != "0"*40):
        raise ValueError("analytic control cannot accept research inputs or review authority")
    prior = grant["previous"]
    if (phase == "qualification") != (prior is None):
        raise ValueError("phase predecessor policy mismatch")
    return remaining


def consume(fd, expected_sha256, contract, runtime_sha256, phase):
    """Fresh worker challenge; close the inherited endpoint after this one grant."""
    if type(fd) is not int or fd < 3:
        raise ValueError("separate inherited authorization descriptor required")
    with socket.socket(fileno=fd) as channel:
        channel.settimeout(HANDSHAKE_SECONDS)
        parent = peer_pid(channel)
        if parent != os.getppid():
            raise ValueError("authorization socket was not created by the actual parent")
        nonce = secrets.token_hex(32)
        send(channel, dict(pid=os.getpid(), challenge=nonce, grant_sha256=expected_sha256))
        reply = receive(channel)
        if (reply.get("challenge") != nonce or reply.get("child_pid") != os.getpid()
                or reply.get("parent_pid") != parent or digest(reply["grant"]) != expected_sha256):
            raise ValueError("one-use authorization challenge mismatch")
        grant = reply["grant"]
        validate_grant(grant, phase, runtime_sha256)
        verify_parent(parent, reply["controller_argv"], contract, grant["kind"])
        if channel.recv(1) != b"":
            raise ValueError("authorization channel contains more than one grant")
        return grant


def issuer(channel, grant, controller_argv):
    """A one-shot callback for the actual Popen child, never a receipt loader."""
    used = False
    def authorize(process):
        nonlocal used
        if used:
            raise ValueError("phase grant already consumed")
        used = True  # failed handshakes also consume the attempt
        channel.settimeout(HANDSHAKE_SECONDS)
        request = receive(channel)
        if (request.get("pid") != process.pid or request.get("grant_sha256") != digest(grant)
                or re.fullmatch("[0-9a-f]{64}", request.get("challenge", "")) is None):
            raise ValueError("request differs from actual launched worker")
        send(channel, dict(challenge=request["challenge"], child_pid=process.pid, parent_pid=os.getpid(),
            controller_argv=controller_argv, grant=grant))
        channel.shutdown(socket.SHUT_WR)
    return authorize
