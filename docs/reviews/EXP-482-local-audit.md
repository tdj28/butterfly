# EXP-482 prospective local audit under the human review policy

Paid review: not_run
Local audit disposition: release-ready
Experiment: EXP-482
Code freeze: e81466a0a18227e91682c68dc63bcf29ce76d688
Source inventory SHA-256: 137bf0feca227f33a71392318ec96f9de10a41f93248fec2cce6285743b7fa5d
Plan SHA-256: 92c989f734afb36cb539f35c0ba0242e5459202b4142ba462e12c223dcce5d8a

This is the implementing agent's local source/design audit, not an independent
human referee report, provider response, numerical result or proof. The human
explicitly replaced routine paid reviews with local audits. No new paid request
is approved by an API refill. EXP-482's failed `review-01` remains failed, with
no generated response. EXP-481's review remains prior context, not a verdict
about this successor. The disposition above permits preparing the release;
fresh production setup, numerical qualification and the one-shot gate must
still succeed independently before downstream phases can run.

## Scientific design and previous findings

EXP-481's 128 trials produced 192 comparisons, of which 92 passed. All 32
DOP853/Radau comparisons agreed within the frozen criterion; the coarser RK4
steps did not. That failure motivates, but does not validate, smaller steps.
The stopped evidence and old consumed attempt remain untouched. This is a
disclosed outcome-informed numerical successor, not a clean confirmatory repeat.

The unchanged EXP-482 plan uses RK4 .0025/.00125, batch 512, 240,000 maximum
steps, 262,144 maximum batch events and one-second resource polling. It retains
both nominations, every six/eight-event raw reference, 8,192 seeds/case, the
4,096/4,096 holdout split, both time windows, all five spline variants and 200
whole-seed bootstrap draws. Tests enforce the complete permitted difference
set from EXP-481; no accuracy/support/retention threshold changed in this gate
amendment. Qualification requires all 192 comparisons to pass the same 1e-4
state/time criteria before any full collection. No sample refill or retry exists.

The new PCG64 draws 482001/482002 were already frozen at the earlier EXP-482
code freeze. They are not selected using a new target outcome. Qualification
IDs name new states, despite reusing logical indices. The full inferential
cohort is not independent of historical nomination selection, reference
conditioning or the outcome-informed method choice; no claim of such
independence is made.

Prior B01 (resource feasibility): accept the disclosed finer-step workaround.
The complete synthetic workload's original .25-second polling projection failed
and remains failed. The separate one-second projection is about 7,064 seconds
for collection under the unchanged 14,400-second phase limit; it is a model
using measured synthetic work, not an observed Rössler runtime or guarantee.
The original hashes and full workload inventory were reverified read-only at
this checkpoint. One-second polling increases possible RSS/disk overshoot
duration; those are sampled stop thresholds, not kernel quotas. Phase deadlines,
parent-loss checks, evidence limits and verified cleanup remain enforced.

Prior B02 (positive and adverse analysis paths): retain the real full-population
200-draw synthetic cubic and two-sheet controls already completed, plus current
regression tests of every reference row, both cases and all required variants.
They test the analysis machinery, not target retention, chaos or symbolic truth.

Prior I01/I03 (conditioning, support and interpretation): retain the narrow
reference-conditioned finite-time cohort, supported-row metrics and complete
casewise outcomes. Inadequate sample/support is inconclusive, not a refutation;
excess operational error is a failure of this test's adequacy criterion, not
nonexistence of a return map. Neither the better case nor diagnostic coordinates
can rescue a failed primary. No support-gap extrapolation is permitted.

Prior I02 (legacy critical-point dependency): the historical helper's stationary
inflection defect remains relevant to nomination/interpretation. The target
reference inputs instead use re-corrected periodic cycles and independently
recomputed raw geometric section events; the production setup reaudits them.
This does not settle the broader historical partition audit. Preserve the
separate stashed manuscript/audit work; do not silently revise old receipts.

## Administrative amendment and checks

The new `local-audited` path is scoped to EXP-482 and pins the exact numerical
plan and human policy independently of release-provided hashes. It binds the
complete 374-file source/test closure, this audit and prior evidence to pushed
Git objects. The host authenticates the release before and after fresh setup.
The worker still verifies its actual parent and independently pinned controller
bytes. Source-only receipts, missing context, changed numeric plans, wrong
experiment identities and fake review fields are rejected. New grants record
`release_sha256` and `release_mode`, not a fictional review-response hash.
Historic grants and frozen branches are not modified or consumed as new grants.

Verification observed before any new target trajectories:

- 89 focused release/successor tests passed, including real temporary Git
  objects and local-audit tamper tests with provider access forbidden.
- 107 numerical and actual controller/worker tests passed, including negative
  grants, predecessor tampering and parent-loss controls.
- Complete suite: 1,781 passed, one existing Linux-only skip on macOS, 110.54 s.
- Public credential-pattern scan: 2,470 staged tracked files passed.
- Live source check at the code freeze above: all 374 source roles verified;
  local receipt `artifacts/EXP-482/local-source-check-01/receipt.json`, 60,697
  bytes, SHA-256 `060fe637fdd73f8a5f06f6cae7603c63c003da7779d06c02a795c4495dee5678`.

These checks qualify the administrative change. The final release still needs
its actual fresh source-bound setup and unused EXP-482 attempt slot. The new
target has not yet run at this audit. No optional paid review is a blocker.

## Permitted result

At most, this experiment can support finite-resolution historical-x map
adequacy and cycle-event proximity on the declared retained cohort. It cannot
establish exact criticality, Jones's alphabet or chain arrows, a homoclinic
orbit, an invariant symbolic partition or a whole-parameter-plane explanation.
The flow-level chains remain an explicit downstream research objective, not
something this release or a passing solver prerequisite would verify.
