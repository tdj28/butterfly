"""Fixed analytic-circle plumbing control. No target inputs or Rössler field calls."""
from dataclasses import asdict
import hashlib
import json

import numpy as np

from .paired_phases import PhaseDesign
from .paired_sampling import SECTIONS, seed_commitment, seed_table
from .paired_sections import CaptureSection
from .poincare import PoincareSection
from .seed_return_map import MapOptions


def make_control():
    table = seed_table(2048)
    plan = dict(kind="analytic-circle-phase-control", target_trajectories_generated=0,
        execution_authorized=False, candidate_ids=["synthetic-first", "synthetic-second"],
        seeds=dict(count_per_case=2048, random_seed=481001, generator="PCG64",
            xz_ranges=[[-14., -.2], [.008, .55]], y_rule="candidate historical-section offset",
            same_xz_across_cases_and_profiles=True, global_seed_ids=[0, 2047], holdout_ids=[1024, 2047],
            ordered_table_sha256=seed_commitment(table)),
        collection=dict(profiles=[dict(name="rk4-005", dt=.05), dict(name="rk4-0025", dt=.025)],
            horizon=20., checkpoint_times=[9., 18., 20.], state_scales=[15., 15., .01],
            gate_margin=1e-5, angle_margin=1e-6, escape_radius=1e6, batch_size=512,
            maximum_events_per_batch=32768, maximum_steps_per_batch=1000,
            journal_interval_steps=100, maximum_snapshot_bytes=1024**2, automatic_retry=False, resume=False),
        adaptive_qualification=dict(global_seed_ids=[0, 1024], horizon=5.5,
            profiles=[dict(method=m, rtol=1e-10, atol=1e-12, max_step=.05) for m in ("DOP853", "Radau")],
            maximum_scaled_event_state_difference=1e-4, maximum_event_time_difference=1e-4,
            require_ordered_accepted_counts_and_membership=True, require_ordered_raw_counts_and_membership=True,
            compare_all_six_profile_pairs=True, require_capture_membership_agreement=True,
            maximum_capture_time_difference=1e-4, maximum_steps_per_seed=1000,
            maximum_field_evaluations_per_adaptive_seed=100000,
            maximum_raw_events_per_seed=128, adaptive_recording_interval_steps=100,
            maximum_adaptive_snapshot_bytes=1024**2),
        sample=dict(observation_windows=[[0., 9.], [9., 18.]], strata_per_window=1,
            minimum_seeds_per_split=256, maximum_profile_retention_disagreement_fraction=.03),
        analysis=dict(primary=dict(section=SECTIONS[0], axis=0, name="x"),
            diagnostics=[dict(section=n, axis=2, name="z") for n in SECTIONS],
            fit_each_window_separately=True, historical_z_or_barrio_z_can_rescue_primary=False,
            variants=[[40, 1e-5], [30, 1e-5], [50, 1e-5], [40, 1e-6], [40, 1e-4]],
            options=asdict(MapOptions(bootstrap_samples=8))),
        critical_membership=dict(enabled_only_after_joint_primary_gate=True,
            require_every_primary_window_profile_variant=True, normalized_interval_padding=.01,
            maximum_absolute_normalized_spline_slope=.02),
        resources=dict(maximum_qualification_seconds=60., maximum_wall_seconds=60., maximum_analysis_seconds=60.,
            maximum_process_rss_bytes=512*1024**2, maximum_collection_disk_bytes=128*1024**2,
            minimum_start_free_bytes=0, supervisor_poll_seconds=.05, supervisor_termination_grace_seconds=.3))
    initial = np.column_stack((table["xz"][:, 0], np.zeros(2048), table["xz"][:, 1]))
    # Distant, deliberately unattainable references: all seeds remain uncaptured.
    # Six/eight distinct rows exercise the complete reference layout, not a flow cycle.
    specs = {SECTIONS[0]: CaptureSection(PoincareSection((0., 1., 0.), 0., -1),
        np.column_stack((-1000.-np.arange(6), np.zeros(6), np.full(6, .01))), (0, 2), (15., .01), .0002, 5),
        SECTIONS[1]: CaptureSection(PoincareSection((1., 0., 0.), 0., 1),
        np.column_stack((np.zeros(8), -1000.-np.arange(8), np.full(8, .01))), (1, 2), (15., .01), .0002, 5)}
    digest = hashlib.sha256(json.dumps(plan, sort_keys=True, allow_nan=False).encode()).hexdigest()
    design = PhaseDesign(plan, {c: initial.copy() for c in plan["candidate_ids"]},
        {c: dict(specs) for c in plan["candidate_ids"]}, "0"*40, digest)
    field = lambda x: np.column_stack((-np.pi/2*x[:, 1], np.pi/2*x[:, 0], np.zeros(len(x))))
    return design, {c: field for c in plan["candidate_ids"]}
