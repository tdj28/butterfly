# EXP-482: a separately reviewed finer-step successor

Status: implementation and outcome-free qualification; **not yet reviewed or
authorized for target execution**. The numeric design is
`experiments/manifests/EXP-482-paired-design.json`. It contains no fabricated
approval. Selecting a new experiment name does not authorize its execution.

## What changes, and why

EXP-481 completed its numerical qualification but failed the prespecified
scaled-state bound: 92 of 192 comparisons passed. DOP853 and Radau agreed on all
32 case/seed comparisons. The full failed run and its consumed attempt remain
intact; this is an outcome-informed redesign, not an unchanged retry.

| Choice | EXP-481 | EXP-482 |
| --- | --- | --- |
| RK4 steps | .01 / .005 | .0025 / .00125 |
| Fixed batch | 64 | 512 |
| Maximum steps/batch | 60,000 | 240,000 |
| Maximum raw events/batch | 32,768 | 262,144 (same 512 events/seed) |
| Resource polling interval | .25 s | 1 s |
| Initial-state random seed | PCG64 481001 | PCG64 482001 |
| Calibration bootstrap seed | 481002 | 482002 |

Everything else in the numeric design is unchanged, including both parameter
cases and their raw six/eight-event references, 8,192 seeds/case, the 4,096/4,096
calibration/holdout split, integration to 300, both time windows, common-cohort
selection, reference-conditioned capture, all five map variants, 200 whole-seed
bootstrap draws, complete critical-proximity matrix and every acceptance limit.
The tests check this exact difference set, not a hand-selected subset.

The fresh seed-table commitment is
`35efa7ac23f569382938dddd4643a7b0b379c4b22f51d5d09eadabdd8362efdf`.
No exact sampled x/z row overlaps the original draw. Logical qualification IDs
remain 0, 512, ..., 7680, but now identify **new initial states**. The diagnostic
and full collection configurations are all declared before observing any new
trajectory. Fresh draws do not erase outcome-informed numerical choices,
historical nomination selection or reference conditioning.

## Feasibility and stopping

The [full synthetic workload](../updates/2026-09-07-exp482-full-workload.md)
measured actual full-horizon journals, raw replay and full-population analysis.
Its original .25-second resource-polling estimate failed and stays failed.
The separately labeled one-second polling projection fits the unchanged
1,800/14,400/7,200-second phase limits and 2 GiB RSS/8 GiB disk limits, including
the same conservative headroom. This is not a measured Rössler runtime.

One-second resource polling increases the possible delay before an RSS/disk
overshoot is detected. It does not change the integration timestep, event
journal cadence, process-parent/deadline watchdog, cleanup procedure or
per-snapshot bound. Resource limits remain sampled stop thresholds, not strict
kernel quotas. Preserve cap failures; do not retry or enlarge the budget after
seeing a scientific outcome.

The complete trial grid has 128 early qualification trials and 64 collection
batches. Qualification still compares all six solver pairs under the same
1e-4 state/time bounds; collection starts only if the entire qualification
passes. Early agreement is not long-time shadowing or all-root verification.

## Release and source roles

Only EXP-481 and EXP-482 are recognized by the existing controller. The default
remains EXP-481. The explicit successor option is `--experiment-id EXP-482`;
there is no arbitrary experiment-name, attempt, retry or resume option.
The new fixed attempt is `artifacts/EXP-482/target-once.json`; the old marker
must never be removed. Setup, review, final plan and dispatch must agree on the
experiment identity before any new slot can be consumed.

The full source/test closure includes **both numeric designs** because the
regression tests compare them, as well as the original fixture manifests and
all previously required source paths. The worker's independent controller-byte
anchor changes with the controller and is regression-tested. Historical frozen
releases continue to refer to their original Git objects, not these new bytes.

Reserve these roles before the prospective review:

- `docs/reviews/EXP-482-review-brief.md` — compact director brief;
- `docs/reviews/EXP-482-decision-context.md` — mechanically reconstructed complete
  numeric design and source/design inventory hash;
- `docs/reviews/EXP-482-evidence-context.md` — prior substantive review,
  structured finding dispositions, numerical failure and bounded workload facts;
- `docs/reviews/EXP-482-review-01/` — exact canonical request/response bundle;
- `docs/reviews/EXP-482-adjudication.json` and `.md` — every finding and authorized
  before/after change;
- `experiments/manifests/EXP-482-reviewed-release.json` — actual release only
  after review, adjudication and source-qualified tests.

Do not create placeholder approvals. Review the construct as well as the
procedure: finite-resolution historical-x adequacy on a supported,
reference-conditioned finite-time population is not an invariant symbolic
partition. A positive result cannot establish Jones' alphabet, arrows, exact
criticality, homoclinic existence or the entire parameter plane.

## Verification ledger

| Surface | Current evidence |
| --- | --- |
| Both release identities, Git/provider tamper controls, isolated setup | 132 focused tests passed before final closure/control additions |
| Actual successor controller and source-qualified full configuration | Verified live at ba85d90: 426 tests/no skips, both raw audits, all 192 configurations; source preflight receipt retained |
| Prospective review and target numerical qualification | Not performed; no new target trajectories |

The real `--mode source --experiment-id EXP-482` preflight on pushed source has
now passed. It ran all bound tests and reconstructed inputs and every
configuration without integrating a target trajectory. Next is the compact
cumulative review; no completed historical review is rerun or relabeled.
