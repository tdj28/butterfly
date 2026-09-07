"""Fixed numerical phase composition; execution authority belongs to the controller.

These explicit-input primitives never authenticate their own source/review or
launch a process. The sealed controller must supply authenticated inputs and
supervise each phase. Synthetic controls use the same journal/replay path.
"""
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re

import numpy as np

from . import paired_journal as journal
from ._paired_startup import inventory
from .models import RosslerParameters, rossler_rhs
from .paired_adaptive import compare_event_profiles, validate_adaptive
from .paired_adaptive_journal import audit_adaptive_journal, record_adaptive
from .paired_campaign import analyze_campaign, planned_seeds, trial_grid, validate_analysis_plan
from .paired_input_io import checked_input
from .paired_replay import BatchExpectation, assemble_profile, read_batch, replay_batch
from .paired_sampling import SECTIONS
from .paired_sections import CaptureSection
from .paired_supervisor import StageLimits
from .poincare import barrio_rossler_section, legacy_rossler_section


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True, allow_nan=False))


def utc():
    return datetime.now(timezone.utc).isoformat()


def descriptor(path):
    return dict(path=path.name, bytes=path.stat().st_size, sha256=journal.sha256(path))


def phase_limits(plan, stage):
    key = {"qualification": "maximum_qualification_seconds", "collection": "maximum_wall_seconds",
           "analysis": "maximum_analysis_seconds"}[stage]
    r = plan["resources"]
    result = StageLimits(r[key], r["maximum_process_rss_bytes"], r["maximum_collection_disk_bytes"],
        r["minimum_start_free_bytes"], r["supervisor_poll_seconds"], r["supervisor_termination_grace_seconds"])
    result.validate()
    return result


@dataclass
class PhaseDesign:
    """Numerical inputs, not an authorization token. Validate before any field call."""
    plan: dict
    initial: dict
    sections: dict
    source_commit: str
    plan_sha256: str

    def binding(self, trial):
        return dict(candidate_id=trial.candidate_id, profile=trial.profile, trial_id=trial.trial_id,
                    source_commit=self.source_commit, plan_sha256=self.plan_sha256)

    def section_config(self, case):
        return canonical({n: {**asdict(s), "cycle_states": np.asarray(s.cycle_states).tolist()}
                          for n, s in self.sections[case].items()})

    def config(self, trial):
        c, q = self.plan["collection"], self.plan["adaptive_qualification"]
        common = {k: c[k] for k in ("state_scales", "gate_margin", "angle_margin", "escape_radius")}
        profiles = {p["name"]: p for p in c["profiles"]}
        if trial.stage == "collection":
            return dict(**common, dt=profiles[trial.profile]["dt"], horizon=c["horizon"],
                checkpoint_times=c["checkpoint_times"], maximum_steps=c["maximum_steps_per_batch"],
                maximum_events=c["maximum_events_per_batch"])
        common.update(horizon=q["horizon"], maximum_steps=q["maximum_steps_per_seed"],
                      maximum_events=q["maximum_raw_events_per_seed"])
        if trial.profile in profiles:
            return dict(**common, dt=profiles[trial.profile]["dt"], checkpoint_times=[q["horizon"]])
        adaptive = {p["method"]: p for p in q["profiles"]}
        return dict(**common, **adaptive[trial.profile],
            maximum_field_evaluations=q["maximum_field_evaluations_per_adaptive_seed"],
            recording_interval=q["adaptive_recording_interval_steps"])

    def recording(self, trial):
        c, q = self.plan["collection"], self.plan["adaptive_qualification"]
        if trial.profile in ("DOP853", "Radau"):
            return dict(maximum_snapshot_bytes=q["maximum_adaptive_snapshot_bytes"])
        return {k: c[k] for k in ("journal_interval_steps", "maximum_snapshot_bytes")}

    def validate(self):
        if (re.fullmatch(r"[0-9a-f]{40}", self.source_commit) is None
                or re.fullmatch(r"[0-9a-f]{64}", self.plan_sha256) is None):
            raise ValueError("full source/plan bindings required")
        table, grid = planned_seeds(self.plan), trial_grid(self.plan)
        cases = self.plan["candidate_ids"]
        if set(self.initial) != set(cases) or set(self.sections) != set(cases):
            raise ValueError("exact both-case design required")
        c, q = self.plan["collection"], self.plan["adaptive_qualification"]
        if c["automatic_retry"] is not False or c["resume"] is not False:
            raise ValueError("automatic retry/resume forbidden")
        # The comparator currently has one time tolerance. Refuse a divergent
        # capture tolerance rather than silently ignoring either declaration.
        if (q["maximum_capture_time_difference"] != q["maximum_event_time_difference"]
                or any(q[k] is not True for k in ("require_ordered_accepted_counts_and_membership",
                    "require_ordered_raw_counts_and_membership", "compare_all_six_profile_pairs",
                    "require_capture_membership_agreement"))):
            raise ValueError("all ordered profile/capture comparisons with equal declared time tolerances required")
        if not all(np.isfinite(q[k]) and q[k] > 0 for k in
                   ("maximum_scaled_event_state_difference", "maximum_event_time_difference")):
            raise ValueError("positive finite comparison tolerances required")
        for stage in ("qualification", "collection", "analysis"):
            phase_limits(self.plan, stage)
        validate_analysis_plan(self.plan)
        for case in cases:
            x = np.asarray(self.initial[case])
            if (x.shape != (len(table["global_seed_ids"]), 3) or not np.isfinite(x).all()
                    or not np.array_equal(x[:, [0, 2]], table["xz"])
                    or not np.all(x[:, 1] == x[0, 1]) or list(self.sections[case]) != list(SECTIONS)
                    or any(len(self.sections[case][n].cycle_states) != count
                           for n, count in zip(SECTIONS, (6, 8), strict=True))):
                raise ValueError("fixed seed table and all six/eight ordered reference rows required")
        # Validate every declared configuration, including the last case, before
        # the first field evaluation. No surviving-trial-driven configuration.
        for trial in grid:
            x = self.initial[trial.candidate_id][list(trial.global_seed_ids)]
            specs, config = self.sections[trial.candidate_id], self.config(trial)
            if trial.profile in ("DOP853", "Radau"):
                validate_adaptive(x[0], trial.global_seed_ids[0], specs, **config)
                bound = self.recording(trial)["maximum_snapshot_bytes"]
                if type(bound) is not int or not 32768 <= bound <= 64*1024**2:
                    raise ValueError("invalid adaptive snapshot bound")
            else:
                journal.preflight(x, np.asarray(trial.global_seed_ids), specs, config, **self.recording(trial))
        return grid

    def identity(self):
        payload = dict(plan=self.plan, initial={k: v.tolist() for k, v in self.initial.items()},
            sections={k: self.section_config(k) for k in self.sections},
            source_commit=self.source_commit, plan_sha256=self.plan_sha256)
        return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def from_reference_audit(plan, audit, *, source_commit, plan_sha256):
    """Construct the Rössler design without integrating; caller authenticates audit."""
    p = canonical(plan)
    if (audit["passed"] is not True or audit["target_trajectories_generated"] != 0
            or audit["plan_input_hashes"] != {k: v["sha256"] for k, v in p["inputs"].items()}
            or [r["candidate_id"] for r in audit["cases"]] != p["candidate_ids"]
            or p["capture"]["integration_continues_after_capture"] is not True
            or p["capture"]["initial_on_plane"] != "flag t=0, exclude its root only, do not exclude seed"):
        raise ValueError("reference audit/design mismatch")
    initial, sections, fields = {}, {}, {}
    table = planned_seeds(p)
    for row in audit["cases"]:
        case, parameters = row["candidate_id"], RosslerParameters(**row["parameters"])
        geometry = dict(zip(SECTIONS, (replace(legacy_rossler_section(parameters), direction=-1),
                                     barrio_rossler_section(parameters)), strict=True))
        initial[case] = np.column_stack((table["xz"][:, 0],
            np.full(len(table["xz"]), geometry[SECTIONS[0]].offset), table["xz"][:, 1]))
        sections[case] = {}
        for name, section in geometry.items():
            ref = row["references"][name]
            if ref["section"] != canonical(asdict(section)) or ref["count"] != len(ref["states"]):
                raise ValueError("reference section differs from candidate geometry")
            sections[case][name] = CaptureSection(section, np.asarray(ref["states"], float),
                **p["capture"][name], radius=p["capture"]["radius"], required_crossings=p["capture"]["required_crossings"])
        fields[case] = lambda x, parameters=parameters: rossler_rhs(0., x.T, parameters).T
    design = PhaseDesign(p, initial, sections, source_commit, plan_sha256)
    design.validate()
    return design, fields


def _expectation(design, trial, row):
    return BatchExpectation(row["started"]["sha256"], row["terminal"]["sha256"],
        np.asarray(trial.global_seed_ids), design.initial[trial.candidate_id][list(trial.global_seed_ids)],
        design.config(trial), design.section_config(trial.candidate_id), design.binding(trial), design.recording(trial))


def _record_trial(design, trial, fields, root):
    path = root/"trials"/trial.trial_id
    initial = design.initial[trial.candidate_id][list(trial.global_seed_ids)]
    spec, config, binding = design.sections[trial.candidate_id], design.config(trial), design.binding(trial)
    if trial.profile in ("DOP853", "Radau"):
        _, audit = record_adaptive(fields[trial.candidate_id], initial[0], trial.global_seed_ids[0], spec, config,
            directory=path, binding=binding, **design.recording(trial))
    else:
        _, audit = journal.record_collection(fields[trial.candidate_id], initial, np.asarray(trial.global_seed_ids),
            spec, config, directory=path, binding=binding, **design.recording(trial))
    row = dict(trial_id=trial.trial_id, binding=binding, status=audit["status"],
        started=descriptor(path/"started.json"), terminal=descriptor(path/"terminal.json"), finished_at=utc())
    journal._json(root/"receipts"/(trial.trial_id+".json"), row)
    if audit["status"] != "completed" or audit["orphan_files"]:
        raise ValueError("incomplete trial; campaign stopped without retry")
    return row


def _qualification_record(design, trial, row, root):
    path = root/"trials"/trial.trial_id
    if trial.profile in ("DOP853", "Radau"):
        meta = journal._read_json(path/"started.json")
        if (meta["config"] != canonical(design.config(trial))
                or meta["sections"] != design.section_config(trial.candidate_id)
                or meta["initial_state"] != design.initial[trial.candidate_id][trial.global_seed_ids[0]].tolist()
                or meta["global_seed_id"] != trial.global_seed_ids[0]
                or meta["maximum_snapshot_bytes"] != design.recording(trial)["maximum_snapshot_bytes"]):
            raise ValueError("adaptive journal differs from fixed numerical design")
        audit = audit_adaptive_journal(path, expected_binding=design.binding(trial),
            expected_started_sha256=row["started"]["sha256"], expected_terminal_sha256=row["terminal"]["sha256"])
        if audit["status"] != "completed" or audit["orphan_files"]:
            raise ValueError("incomplete adaptive qualification evidence")
        return audit["snapshot"]
    raw = read_batch(path, _expectation(design, trial, row))
    return dict(status="failed" if raw["state"]["failed"].any() else "completed",
        global_seed_ids=raw["global_seed_ids"], initial_states=raw["initial_states"],
        horizon=raw["horizon"], observed_until=raw["horizon"], events=raw["events"],
        **{k: raw["state"][k] for k in ("capture_times", "initial_on_plane", "ambiguous")})


def _compare_qualification(design, trials, rows, root):
    q, comparisons = design.plan["adaptive_qualification"], []
    for case in design.plan["candidate_ids"]:
        for seed in q["global_seed_ids"]:
            selected = [t for t in trials if t.candidate_id == case and t.global_seed_ids == (seed,)]
            records = {t.profile: _qualification_record(design, t, rows[t.trial_id], root) for t in selected}
            for left, right in combinations(records, 2):
                comparisons.append(dict(candidate_id=case, global_seed_id=seed, left=left, right=right,
                    **compare_event_profiles(records[left], records[right],
                        state_scales=design.plan["collection"]["state_scales"],
                        maximum_state_difference=q["maximum_scaled_event_state_difference"],
                        maximum_time_difference=q["maximum_event_time_difference"])))
    return comparisons


def require_phase(design, directory, expected, stage):
    """Consume an externally bound completed phase; hashes alone are not authority."""
    root = journal._safe_path(Path(directory))
    if expected["path"] != "terminal.json":
        raise ValueError("expected phase terminal required")
    terminal = json.loads(checked_input(root, expected))
    trials = [t for t in trial_grid(design.plan) if t.stage == stage]
    if (terminal["stage"] != stage or terminal["status"] != "completed"
            or terminal["design_sha256"] != design.identity()
            or terminal["trial_ids"] != [t.trial_id for t in trials]
            or inventory(root, omit=("terminal.json",)) != terminal["files"]):
        raise ValueError("previous phase differs from complete fixed-grid evidence")
    if stage == "qualification" and terminal["passed"] is not True:
        raise ValueError("numerical qualification failed; collection forbidden")
    return terminal


def _save_profile(root, case, name, profile):
    # All IDs, failure/capture masks and raw pair indices survive aggregation.
    arrays = {k: profile[k] for k in ("global_seed_ids", "initial_states", "retained", "seed_batch_index")}
    arrays.update({"state__"+k: v for k, v in profile["state"].items()})
    arrays.update({f"section_{i}__{k}": profile[k][n] for i, n in enumerate(SECTIONS)
        for k in ("pair_states", "pair_times", "section_pair_indices", "section_eligible_counts")})
    journal._new_file(root/f"{case}--{name}-pairs.npz", lambda stream: np.savez_compressed(stream, **arrays))
    journal._json(root/f"{case}--{name}-provenance.json", dict(batch_ids=profile["batch_ids"],
        sources=profile["sources"], binding=profile["binding"], counts=profile["counts"],
        windows=profile["windows"].tolist(), horizon=profile["horizon"]))


def run_phase(design, stage, output, *, fields=None, previous_directory=None, previous_receipt=None):
    """Execute an entire fixed phase or preserve its failure, never resume.

    Caller MUST provide source/review authorization and an external supervisor.
    No user-facing target CLI calls this primitive until that gate is complete.
    Previous receipts must come from the controller's actual completed worker.
    """
    if stage not in ("qualification", "collection", "analysis"):
        raise ValueError("unknown fixed phase")
    grid = design.validate()
    identity = design.identity()
    trials = [t for t in grid if t.stage == stage]
    previous = None
    if stage != "qualification":
        if previous_directory is None or previous_receipt is None:
            raise ValueError("externally bound preceding phase required")
        previous = require_phase(design, previous_directory, previous_receipt,
                                 "qualification" if stage == "collection" else "collection")
    elif previous_directory is not None or previous_receipt is not None:
        raise ValueError("qualification has no previous numerical phase")
    if stage != "analysis" and (fields is None or set(fields) != set(design.plan["candidate_ids"])
                                or not all(callable(f) for f in fields.values())):
        raise ValueError("exact both-case fields required")
    if stage == "analysis" and fields is not None:
        raise ValueError("analysis does not accept a field or integrate")
    root = journal._safe_path(Path(output))
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    journal._json(root/"started.json", dict(stage=stage, design_sha256=identity, started_at=utc(),
        source_commit=design.source_commit, plan_sha256=design.plan_sha256,
        trial_ids=[t.trial_id for t in trials], previous_receipt=previous_receipt,
        limits=asdict(phase_limits(design.plan, stage)), resource_enforcement="external supervisor required"))
    try:
        rows, details = {}, {}
        if stage != "analysis":
            (root/"trials").mkdir()
            (root/"receipts").mkdir()
            for trial in trials:
                rows[trial.trial_id] = _record_trial(design, trial, fields, root)
                print(f"{stage}: {trial.trial_id} completed", flush=True)
            if stage == "qualification":
                comparisons = _compare_qualification(design, trials, rows, root)
                journal._json(root/"comparisons.json", comparisons)
                details.update(passed=all(r["passed"] for r in comparisons), comparison_count=len(comparisons))
        else:
            profiles = {}
            source = Path(previous_directory)
            for case in design.plan["candidate_ids"]:
                profiles[case] = {}
                for profile in design.plan["collection"]["profiles"]:
                    name, batches = profile["name"], {}
                    selected = [t for t in grid if t.stage == "collection" and t.candidate_id == case and t.profile == name]
                    for trial in selected:
                        row = journal._read_json(source/"receipts"/(trial.trial_id+".json"))
                        if row["trial_id"] != trial.trial_id or row["binding"] != design.binding(trial) or row["status"] != "completed":
                            raise ValueError("collection receipt differs from fixed trial")
                        batches[trial.trial_id] = replay_batch(source/"trials"/trial.trial_id,
                            _expectation(design, trial, row), design.plan["sample"]["observation_windows"],
                            strata_per_window=design.plan["sample"]["strata_per_window"])
                    joined = assemble_profile(batches, [t.trial_id for t in selected],
                        planned_seeds(design.plan)["global_seed_ids"], design.initial[case])
                    _save_profile(root, case, name, joined)
                    profiles[case][name] = joined
            references = {case: design.sections[case][SECTIONS[0]].cycle_states for case in design.plan["candidate_ids"]}
            result = analyze_campaign(profiles, design.initial, references, design.plan,
                source_commit=design.source_commit, plan_sha256=design.plan_sha256)
            journal._json(root/"analysis.json", result)
            details.update(all_cases_primary_resolved=result["all_cases_primary_resolved"], historical_symbols_verified=False)
        if identity != design.identity():
            raise ValueError("numerical design mutated during phase")
        if previous is not None:
            require_phase(design, previous_directory, previous_receipt,
                          "qualification" if stage == "collection" else "collection")
        journal._json(root/"terminal.json", dict(stage=stage, status="completed", design_sha256=identity,
            trial_ids=[t.trial_id for t in trials], finished_at=utc(), **details, files=inventory(root)))
        return descriptor(root/"terminal.json")
    except (Exception, KeyboardInterrupt) as error:
        journal._json(root/"failure.json", dict(stage=stage, status="failed", design_sha256=identity,
            failed_at=utc(), error_type=type(error).__name__, message=str(error),
            policy="retain every prefix; no retry, resume or incomplete-campaign analysis"))
        raise
