#!/usr/bin/env python3
"""Exercise the real independent watchdog without any paid resource creation.

Only authenticated read-only provider inventory is permitted by this control.
The local launchd service and task key are scoped to a fresh private record.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import threading

from scripts import execute_symbolic_center_cloud as cloud
from scripts import runpod_symbolic_worker as worker
from scripts import run_symbolic_center_pilot as pilot


def read_only_request(method, url, **kwargs):
    if method != "GET":
        raise worker.LifecycleError("watchdog smoke forbids provider mutations")
    return worker.runpodctl.request_json(method, url, **kwargs)


def run_control(plan, state_dir, output, *, start_watchdog=None, stop_watchdog=None):
    start_watchdog = worker.launchd_watchdog if start_watchdog is None else start_watchdog
    stop_watchdog = worker.retire_watchdog if stop_watchdog is None else stop_watchdog
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError("smoke output must be new")
    receipt = {"schema": "butterfly.symbolic-watchdog-smoke.v1", "source_commit": plan["source_commit"],
               "started_utc": pilot.utc_now(), "passed": False, "target_computation_performed": False,
               "provider_create_called": False, "provider_mutations_performed": False}
    stop = threading.Event()
    with worker.single_controller_lock():
        worker.require_no_unresolved_controller()
        store = worker.prepare_store(state_dir, plan)
        worker.register_controller(store)

        def pulse():
            while not stop.wait(3):
                worker.write_heartbeat(store)

        thread = threading.Thread(target=pulse, daemon=True)
        thread.start()
        try:
            start_watchdog(store)
            worker.require_watchdog(store)
            record = store.read()
            if record.get("create_attempted") or record.get("pod_id"):
                raise worker.LifecycleError("unexpected create state during read-only smoke")
            receipt["independent_authenticated_watchdog_ready"] = True
            receipt["watchdog_heartbeat"] = worker.heartbeat_record(store, "watchdog")
        except (Exception, SystemExit, KeyboardInterrupt) as error:
            receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
        finally:
            store.update(controller_finished=True)
            try:
                terminated = worker.terminate_owned(store, request=read_only_request)
                receipt["termination_verified"] = terminated
                if terminated:
                    stop_watchdog(store)
                    receipt["local_watchdog_retired"] = True
            except (Exception, SystemExit, KeyboardInterrupt) as error:
                receipt["cleanup_failure"] = {"type": type(error).__name__, "message": str(error)}
            stop.set()
            thread.join(timeout=5)
            record = store.read()
            receipt["create_attempted"] = record.get("create_attempted")
            receipt["termination_reason"] = record.get("termination_reason")
            receipt["passed"] = bool(receipt.get("independent_authenticated_watchdog_ready")
                                     and receipt.get("termination_verified")
                                     and receipt.get("local_watchdog_retired")
                                     and not record.get("create_attempted")
                                     and "failure" not in receipt and "cleanup_failure" not in receipt)
            receipt["finished_utc"] = pilot.utc_now()
            pilot.write_new_json(output, receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    _, plan = cloud.runtime_plan(args.source_commit)
    receipt = run_control(plan, args.state_dir, args.output)
    print(pilot.encoded_json({"passed": receipt["passed"], "provider_create_called": False,
                              "output": str(args.output)}).decode(), end="")
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
