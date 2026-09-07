#!/usr/bin/env python3
"""Preserve EXP-482's failed feasibility gate and report a post-observation option.

Read-only: no integration, benchmark retry, target release or file modification.
The one-second polling scenario is a calculation, not a measured target run.
"""
import json
import math
from pathlib import Path

from butterfly._paired_startup import inventory, sha256

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/"artifacts/EXP-482/full-workload-01"
RECEIPT_SHA = "b8ae5599f85409ee6cd07ae9a3e20fa2083c0a1adbe1fd763dfc873434d78e3d"
SUPERVISOR_SHA = "de7e572dd40f2e6a52fafc97ae40468ffda763e164568d8ff5ea8a6b103e1910"
SOURCE = "bdce7efeeda18ce1537a55a42af8be1490b831ec"


def polling_scenario(receipt, poll_seconds):
    if not math.isfinite(poll_seconds) or not 0 < poll_seconds <= 1:
        raise ValueError("polling interval outside the existing supervisor range")
    base = 2*(2*8192//512)*sum(r["seconds"] for r in receipt["collection"])
    occupancy = 2*receipt["estimates"]["projected_full_tree_scan_seconds"]/poll_seconds
    projected = dict(receipt["estimates"])
    projected.update(collection_seconds=base/(1-occupancy) if occupancy < 1 else None,
        scan_cpu_fraction_with_headroom=occupancy)
    projected["fits_limits"] = all(projected[k] is not None and projected[k] < v
        for k,v in receipt["protocol"]["limits"].items())
    return dict(poll_seconds=poll_seconds,estimates=projected,
        measured_at_this_polling_interval=False,
        scope="post-observation resource-design calculation; not a replacement for the failed original gate")


def summarize():
    path, supervisor = RUN/"workload/receipt.json", RUN/"supervised-result.json"
    if sha256(path) != RECEIPT_SHA or sha256(supervisor) != SUPERVISOR_SHA:
        raise ValueError("original workload anchors changed")
    receipt, observed = json.loads(path.read_bytes()), json.loads(supervisor.read_bytes())
    if (inventory(RUN/"workload",omit=("receipt.json",)) != receipt["files"]
            or observed["binding"]["source_commit"] != SOURCE
            or observed["status"] != "incomplete" or observed["returncode"] != 2
            or not observed["owned_group_cleanup_verified"]
            or receipt["estimates"]["fits_limits"] is not False
            or polling_scenario(receipt,.25)["estimates"] != receipt["estimates"]):
        raise ValueError("original outcome or evidence inventory differs")
    return dict(experiment_id="EXP-482",source_commit=SOURCE,
        receipt_sha256=RECEIPT_SHA,supervisor_sha256=SUPERVISOR_SHA,
        original={k:v for k,v in receipt.items() if k != "files"},
        supervisor={k:v for k,v in observed.items() if k != "binding"},
        full_workload_inventory_verified=True,proposed_polling_scenario=polling_scenario(receipt,1.),
        target_trajectories_generated=0,historical_symbols_verified=False,
        recommendation="prospectively review one-second resource polling with unchanged numerical and scientific gates")


if __name__ == "__main__":
    print(json.dumps(summarize(),sort_keys=True,indent=2,allow_nan=False))
