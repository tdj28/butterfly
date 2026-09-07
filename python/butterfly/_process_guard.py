"""Standard-library-only startup guard, loadable before scientific imports.

The sealed production bootstrap can load this exact file by path without
executing butterfly.__init__. Generic argv supervision does not attest use.
"""
import os
import select
import signal
import stat
import threading
import time


def install_parent_guard(maximum_seconds):
    """Kill the worker's owned session on supervisor pipe EOF or deadline.

    FD0 must be the supervisor-owned liveness pipe and the worker its session
    leader. Earlier fsynced snapshots survive; no terminal receipt is invented.
    """
    if (os.name != "posix" or os.getpid() != os.getpgrp() or os.getsid(0) != os.getpid()
            or not stat.S_ISFIFO(os.fstat(0).st_mode) or type(maximum_seconds) not in (float, int)
            or not 0 < maximum_seconds < float("inf")):
        raise ValueError("parent guard requires bounded owned session and input pipe")
    # Keep the original pipe even if a library (notably pytest's fd capture)
    # redirects FD0 later. Watching the numeric descriptor after replacement
    # can mistake /dev/null EOF for supervisor loss and kill a healthy stage.
    liveness = os.dup(0)
    os.set_inheritable(liveness, False)
    deadline = time.monotonic()+maximum_seconds
    def watch():
        try:
            while True:
                remaining = deadline-time.monotonic()
                if remaining <= 0:
                    break
                ready, _, _ = select.select([liveness], [], [], min(.1, remaining))
                if ready and os.read(liveness, 1) == b"":
                    break  # liveness only: bytes never become commands
        finally:
            try:
                os.close(liveness)
            finally:
                os.killpg(os.getpgrp(), signal.SIGKILL)
    thread = threading.Thread(target=watch, name="butterfly-parent-guard", daemon=True)
    thread.start()
    return thread
