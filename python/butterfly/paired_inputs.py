"""Read-only EXP-481 capture-input audit against preserved EXP-480 raw events.

No ODE solver, map fit, symbolic encoder or target collection is invoked.
"""
from dataclasses import asdict, replace
import json
import math
import zipfile

import numpy as np

from .models import RosslerParameters, rossler_rhs
from .poincare import legacy_rossler_section, barrio_rossler_section
from . import paired_input_io as evidence

SOURCE = "5b584f4a0cf2fe4544e22d5288878300efd35469"
IDS = ["local-a025-c083", "local-a027-c083"]


def load_legacy_raw(path):
    """Bound the exact old producer schema, including its hyphenated names."""
    fields = ("times", "states", "normal_velocity", "angles", "accepted", "signed_scaled_gate_distance",
              "gate_unresolved", "orientation_unresolved", "extremum_times", "extremum_states",
              "extremum_plane_distance", "extremum_gate_accepted")
    expected = {"integration_times", "integration_states"} | {
        name+"_"+field for name in ("historical-negative", "barrio-positive") for field in fields}
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if (len(members) != len(expected) or {m.filename for m in members} != {n+".npy" for n in expected}
                or sum(m.file_size for m in members) > 16*1024**2):
            raise ValueError("unexpected or oversized legacy event archive")
        total = 0
        for member in members:
            with archive.open(member) as stream:
                version = np.lib.format.read_magic(stream)
                readers = {(1, 0): np.lib.format.read_array_header_1_0, (2, 0): np.lib.format.read_array_header_2_0}
                if version not in readers:
                    raise ValueError("unsupported legacy NPY version")
                shape, _, dtype = readers[version](stream)
                total += math.prod(shape)*dtype.itemsize
                if dtype.hasobject or dtype.fields or total > 16*1024**2:
                    raise ValueError("unsafe legacy event shape/dtype")
    with np.load(path, allow_pickle=False) as saved:
        return {name: saved[name] for name in saved.files}


def extract_references(raw, row, parameters):
    """Reconstruct the declared first window without trusting summary rows."""
    sections = {"historical-negative": replace(legacy_rossler_section(parameters), direction=-1),
                "barrio-positive": barrio_rossler_section(parameters)}
    period = row["correction"]["period_time"]
    if not np.isfinite(period) or period <= 0:
        raise ValueError("invalid qualified period")
    references = {}
    for name, section in sections.items():
        declaration = json.loads(json.dumps(asdict(section)))
        if row["integration"]["sections"][name]["section"] != declaration:
            raise ValueError("saved section differs from candidate geometry")
        times, states = raw[name+"_times"], raw[name+"_states"]
        if (times.ndim != 1 or states.shape != (len(times), 3) or not len(times)
                or not np.isfinite(times).all() or not np.isfinite(states).all()
                or np.any(np.diff(times) <= 0)):
            raise ValueError("invalid ordered raw reference events")
        fields = np.array([rossler_rhs(t, state, parameters) for t, state in zip(times, states, strict=True)])
        velocity = fields @ np.asarray(section.normal)
        accepted = (section.direction*velocity > 0) & np.array([section.accepts(state) for state in states])
        if (not np.array_equal(velocity, raw[name+"_normal_velocity"])
                or not np.array_equal(accepted, raw[name+"_accepted"])):
            raise ValueError("raw normal velocity or membership differs from vector field/geometry")
        indices = np.flatnonzero(accepted & (times/period >= .25) & (times/period < 1.25))
        window = row["sections"][name]["windows"][0]
        expected_count = 6 if name == "historical-negative" else 8
        if (len(indices) != expected_count or window["count"] != expected_count or window["passed"] is not True
                or not np.array_equal(states[indices], window["states"])
                or not np.array_equal(times[indices]/period-.25, window["phases"])):
            raise ValueError("capture reference summary differs from exact ordered raw window")
        references[name] = {"section": declaration, "raw_event_indices": indices.tolist(),
            "states": states[indices].tolist(), "times": times[indices].tolist(), "count": len(indices)}
    return references


def load_references(plan, root):
    if plan["candidate_ids"] != IDS:
        raise ValueError("exact ordered two-candidate set required")
    payloads = {key: json.loads(evidence.checked_input(root, declaration)) for key, declaration in plan["inputs"].items()}
    receipt = payloads["capture_source_receipt"]
    qualified = payloads["event_qualification"]
    if (qualified.get("experiment_id") != "EXP-480" or qualified.get("passed") is not True
            or qualified.get("source_commit") != SOURCE
            or qualified.get("raw_receipt_sha256") != plan["inputs"]["capture_source_receipt"]["sha256"]
            or qualified.get("case_outcomes") != [{"candidate_id": name, "outcome": "qualified"} for name in IDS]):
        raise ValueError("event qualification differs from bound source/case set")
    if (receipt["source"]["commit"] != SOURCE or receipt["status"] != "completed" or receipt["passed"] is not True
            or receipt["case_outcomes"] != [{"candidate_id": name, "outcome": "qualified"} for name in IDS]
            or payloads["nominations"]["nomination_result"]["direct_candidate_ids"] != IDS):
        raise ValueError("capture source or nomination set is not qualified")
    candidate_rows = payloads["candidates"]["candidates"]
    candidates = {r["id"]: r for r in candidate_rows}
    if len(candidates) != len(candidate_rows):
        raise ValueError("duplicate candidate identity")
    directory = evidence.confined_path(root, plan["inputs"]["capture_source_receipt"]["path"]).parent
    files = {r["path"]: r for r in receipt["files"]}
    if len(files) != len(receipt["files"]):
        raise ValueError("duplicate source receipt asset")
    result = []
    for name in IDS:
        row = payloads["capture_"+name]
        expected = [r for r in receipt["profiles"] if r["candidate_id"] == name and r["profile"]["name"] == "dop853-refined"]
        if (len(expected) != 1 or row != expected[0] or row["passed"] is not True
                or row["raw"] != files.get(row["raw"]["path"])):
            raise ValueError("reference row differs from bound source receipt")
        candidate = candidates[name]
        if candidate["passed"] is not True:
            raise ValueError("candidate input unqualified")
        raw_path = evidence.collection_file(directory, row["raw"])
        raw = load_legacy_raw(raw_path)
        references = extract_references(raw, row, RosslerParameters(**candidate["parameters"]))
        evidence.collection_file(directory, row["raw"])  # recheck after reading
        result.append({"candidate_id": name, "parameters": candidate["parameters"],
            "raw": row["raw"], "references": references})
    return {"passed": True, "kind": "EXP-481-capture-reference-raw-audit", "source_commit": SOURCE,
        "target_trajectories_generated": 0, "plan_input_hashes": {k: v["sha256"] for k, v in plan["inputs"].items()},
        "cases": result, "scope": "Input provenance and exact raw-row concordance only; no new partition or symbol claim"}
