# EXP-482 decision context

The following is the complete machine design. The source/test inventory is verified locally, not inspected by the reviewer.

Source/design inventory SHA-256: `9c29baff1625297d022add54330fbd33d50dfb2f65e9167ce7e55d5a69396bca`

```json
{
  "adaptive_qualification": {
    "adaptive_recording_interval_steps": 1000,
    "compare_all_six_profile_pairs": true,
    "global_seed_ids": [
      0,
      512,
      1024,
      1536,
      2048,
      2560,
      3072,
      3584,
      4096,
      4608,
      5120,
      5632,
      6144,
      6656,
      7168,
      7680
    ],
    "horizon": 20,
    "maximum_adaptive_snapshot_bytes": 8388608,
    "maximum_capture_time_difference": 0.0001,
    "maximum_event_time_difference": 0.0001,
    "maximum_field_evaluations_per_adaptive_seed": 1000000,
    "maximum_raw_events_per_seed": 2048,
    "maximum_scaled_event_state_difference": 0.0001,
    "maximum_steps_per_seed": 60000,
    "profiles": [
      {
        "atol": 1e-12,
        "max_step": 0.01,
        "method": "DOP853",
        "rtol": 1e-10
      },
      {
        "atol": 1e-12,
        "max_step": 0.01,
        "method": "Radau",
        "rtol": 1e-10
      }
    ],
    "require_capture_membership_agreement": true,
    "require_ordered_accepted_counts_and_membership": true,
    "require_ordered_raw_counts_and_membership": true,
    "scope": "early transient event-detection/numerical diagnostic only; no long-time shadowing or all-root guarantee"
  },
  "analysis": {
    "across_cases": "report both cases separately; do not pool or select the better case; overall support requires both",
    "baseline": "calibration-only least-squares affine map; report heldout q90 error beside spline on identical supported rows; no additional gate",
    "diagnostics": [
      {
        "axis": 2,
        "name": "z",
        "section": "historical-negative"
      },
      {
        "axis": 2,
        "name": "z",
        "section": "barrio-positive"
      }
    ],
    "fit_each_window_separately": true,
    "historical_z_or_barrio_z_can_rescue_primary": false,
    "joint_primary_gate": "all five variants, both windows and both step profiles resolve in each case; branch count agrees; ordered critical regions must be disjoint within and across maps, and matched intervals across windows/profiles span at most 0.04 of their combined calibration domain",
    "normalization": "min and max of all calibration pair endpoints only, same affine transform for source and target; no holdout refit",
    "options": {
      "bootstrap_samples": 200,
      "grid_size": 4097,
      "maximum_critical_span": 0.04,
      "maximum_empty_run": 2,
      "maximum_heldout_q90_error": 0.08,
      "maximum_heldout_unsupported_fraction": 0.05,
      "minimum_bin_seeds": 8,
      "minimum_bootstrap_consensus": 0.8,
      "minimum_coverage": 0.7,
      "minimum_prominence": 0.03,
      "minimum_seeds": 256,
      "random_seed": 482002
    },
    "primary": {
      "axis": 0,
      "name": "x",
      "section": "historical-negative"
    },
    "uncertainty": "whole calibration-seed bootstrap; failed replicates retained; envelope over nominal and count-matched bootstrap extrema and all variants; descriptive, not a simultaneous confidence interval",
    "variants": [
      [
        40,
        1e-05
      ],
      [
        30,
        1e-05
      ],
      [
        50,
        1e-05
      ],
      [
        40,
        1e-06
      ],
      [
        40,
        0.0001
      ]
    ]
  },
  "candidate_ids": [
    "local-a025-c083",
    "local-a027-c083"
  ],
  "capture": {
    "barrio-positive": {
      "axes": [
        1,
        2
      ],
      "scales": [
        15,
        0.01
      ]
    },
    "historical-negative": {
      "axes": [
        0,
        2
      ],
      "scales": [
        15,
        0.01
      ]
    },
    "initial_on_plane": "flag t=0, exclude its root only, do not exclude seed",
    "integration_continues_after_capture": true,
    "radius": 0.0002,
    "reference": "each section's windows[0].states from the hash-bound EXP-480 dop853-refined result",
    "required_crossings": 5
  },
  "collection": {
    "angle_margin": 1e-06,
    "automatic_retry": false,
    "batch_size": 512,
    "checkpoint_times": [
      50,
      100,
      150,
      200,
      250,
      300
    ],
    "escape_radius": 1000000,
    "gate_margin": 1e-05,
    "horizon": 300,
    "journal_interval_steps": 1000,
    "maximum_events_per_batch": 262144,
    "maximum_snapshot_bytes": 8388608,
    "maximum_steps_per_batch": 240000,
    "profiles": [
      {
        "dt": 0.0025,
        "name": "rk4-00025"
      },
      {
        "dt": 0.00125,
        "name": "rk4-000125"
      }
    ],
    "resume": false,
    "state_scales": [
      15,
      15,
      0.01
    ]
  },
  "critical_membership": {
    "enabled_only_after_joint_primary_gate": true,
    "forbidden_claims": [
      "exact zero derivative",
      "homoclinic existence",
      "Jones alphabet verified",
      "symbolic arrows verified",
      "whole parameter-plane explanation"
    ],
    "maximum_absolute_normalized_spline_slope": 0.02,
    "normalized_interval_padding": 0.01,
    "permitted_claim": "finite-resolution proximity to independently estimated turning regions, conditional on nominated cases and retained finite-time population",
    "reference_orbit": "all six historical events from the same hash-bound EXP-480 window; no chosen phase",
    "report": "full orbit-event by ordered critical-region distance/slope matrix; zero, one or multiple near-critical events; no rounding to criticality",
    "require_every_primary_window_profile_variant": true
  },
  "experiment_id": "EXP-482",
  "inputs": {
    "candidates": {
      "path": "artifacts/EXP-204/candidates.json",
      "sha256": "71aab52016abc8163887b2bdfd4e8124bde0e436be2239751f19d29bed490012"
    },
    "capture_local-a025-c083": {
      "path": "artifacts/EXP-480/run-5b584f4/local-a025-c083-dop853-refined-result.json",
      "sha256": "7d0236db6a6f2138873a1c41b2b78c3a59ea1a378c4a6df2d2125d792d102535"
    },
    "capture_local-a027-c083": {
      "path": "artifacts/EXP-480/run-5b584f4/local-a027-c083-dop853-refined-result.json",
      "sha256": "a957b04d77655b3b644d05b95bad23ddbe3c783585d14b351e20a97c5c3e29ca"
    },
    "capture_source_receipt": {
      "path": "artifacts/EXP-480/run-5b584f4/receipt.json",
      "sha256": "aa4556cdfbca2fa277c8e77daec00f01190e0a8bfde33d9977e5a594c58127b9"
    },
    "event_qualification": {
      "path": "docs/experiments/receipts/EXP-480.json",
      "sha256": "05454ac4ed6a7c7618809303bf99aca6fd73e94a6575ecf2ee9bdb3cae55a557"
    },
    "nominations": {
      "path": "artifacts/EXP-479/analysis-30f6c5b/receipt.json",
      "sha256": "4147ff20adefb6adf536137cb0a92809446ce66d40c20b6c00f909fa6235755f"
    }
  },
  "resources": {
    "backend": "local CPU Float64, serial fixed batches",
    "compute_cost_usd": 0,
    "failure_policy": "retain raw and partial evidence, stop campaign on technical invalidity or cap; do not retry or analyze an incomplete campaign as completed",
    "maximum_analysis_seconds": 7200,
    "maximum_collection_disk_bytes": 8589934592,
    "maximum_process_rss_bytes": 2147483648,
    "maximum_qualification_seconds": 1800,
    "maximum_wall_seconds": 14400,
    "minimum_start_free_bytes": 17179869184,
    "resource_bound_semantics": "RSS and disk are sampled operational stop thresholds, not kernel-enforced peak quotas; queries and writes may overshoot between samples. Per-snapshot and per-batch bounds also apply. Worker parent-loss/deadline guard must be installed and attested before scientific imports.",
    "supervisor_poll_seconds": 1,
    "supervisor_termination_grace_seconds": 5
  },
  "sample": {
    "all_original_ids_reported": true,
    "maximum_profile_retention_disagreement_fraction": 0.03,
    "minimum_seeds_per_split": 256,
    "observation_windows": [
      [
        80,
        140
      ],
      [
        180,
        240
      ]
    ],
    "pair_rule": "first true consecutive accepted-return pair whose source is in each half-open physical-time stratum and target is at or before the window end",
    "population": "valid and unambiguous through t=300, uncaptured on both sections, sufficient pairs in every section/window/stratum, then intersect retained global IDs across both RK4 profiles",
    "strata_per_window": 4,
    "unresolved_rule": "exclude seed with any unresolved root or sliding-plane ambiguity; never bridge unresolved events",
    "weights": "exactly four pairs per seed per window per section; equal seed weights; no interpolation, duplication or refill"
  },
  "schema": "butterfly.paired-design.v1",
  "seeds": {
    "count_per_case": 8192,
    "generator": "PCG64",
    "global_seed_ids": [
      0,
      8191
    ],
    "holdout_ids": [
      4096,
      8191
    ],
    "ordered_table_sha256": "35efa7ac23f569382938dddd4643a7b0b379c4b22f51d5d09eadabdd8362efdf",
    "random_seed": 482001,
    "same_xz_across_cases_and_profiles": true,
    "xz_ranges": [
      [
        -14,
        -0.2
      ],
      [
        0.008,
        0.55
      ]
    ],
    "y_rule": "candidate historical-section offset"
  }
}
```
