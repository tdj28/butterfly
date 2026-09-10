# EXP-523 is executing on prax

Operational checkpoint, 2026-09-10 22:22 UTC. **No new scientific result yet.**

The two-step refreshed contact-path calculation is running on the existing
prax host. Its worker was observed alive after launch, the one-shot marker
is consumed, and new raw files are being retained. Do not launch it again.
The same frozen worker will run the complete raw-data audit after target
collection. Scientific outcomes have not been inspected at this checkpoint.

- Source commit: `eae6745d124c2fa59efc4eff337929e9ff71607d`.
- Immutable execution ref: `refs/heads/codex/exp523-prax-execution`.
- Manifest SHA-256: `e4c5b399f77dc8a23d069419866ff4a9787c9c7970b1e5336d6a19e3510ce4aa`.
- Review branch: `codex/exp523-refreshed-contact-path`, [PR 89](https://github.com/tdj28/butterfly/pull/89).
- Remote task directory: `/home/ubuntu/butterfly-research/exp523-refreshed-eae6745d124c`.
- Frozen checkout: that directory's `source/` subdirectory.
- Raw run: `source/artifacts/EXP-523/target-eae6745d124c/`.
- Marker: `source/artifacts/EXP-523/target-once.json` — consumed.
- Expected successful audit: `source/artifacts/EXP-523/primary-audit-01.json`.
- Worker PID at launch: `132437`; identify it by its exact command/task path
  before future process operations. Do not assume a stale PID remains owned.
- Operational log: `operational.log` in the remote task directory.

Both local sparse-checkout rehearsal and remote sealed startup passed: 202
bound source paths, 206 physically verified files, 27,647,289 source/input
bytes. The local rehearsal receipt is retained at
`artifacts/EXP-523/local-sparse-rehearsal.json`. The remote preparation records
`startup.json`, `preparation.json` and `launch.json` are retained outside the
raw run. Prax had 23,546,470,400 bytes free after preparation. Its managed
runtime is CPython 3.13.13, NumPy 2.5.1 and SciPy 1.18.0 from the locked
dependencies. Exact run binding is recorded before target outcomes.

Only already-public frozen source and compact inputs were fetched from
GitHub; no historical raw archive was uploaded. No paid Pro request or new
GPU rental occurred. Mac raw evidence remains untouched. Newly generated
EXP-523 raw evidence resides on prax; a second raw backup or public raw release
has **not** been established.

The target run and complete audit each have a separate six-hour deadline.
There are no automatic numerical retries. A failure or timeout preserves the
consumed attempt and its evidence. Read the
[frozen protocol](../experiments/EXP-523-refreshed-contact-path.md) and
[design review](2026-09-10-exp523-refreshed-path-design.md) for scientific gates
and the pre-execution root-identity fix.

Next: observe operational completion, inspect and independently replay the
compact decision only after the complete raw audit, then publish the result,
data-derived figures and manuscript update. Preserve failed predictors and
any accepted prefix. Continue toward actual grazing and the independently
identified symbolic partition; a sampled path alone will not verify Jones's
flow-level symbolic chain.

## Outcome-independent work while the worker runs

The result renderer `scripts/render_exp523_path.py` is implemented outside the
frozen numerical closure. Fifteen controls cover audited receipt identity,
complete measurement selection, deterministic output, failed stencils and
receipt/output hashes. It replays both the compact controller and separate
scalar checks before drawing. Synthetic success and failed-predictor/refinement
figures were rendered and visually inspected; they are explicitly labeled
synthetic and are **not** EXP-523 results or manuscript figures.

The actual figure will retain all calibration samples and unaccepted trials,
distinguish the accepted prefix, and show every available full-state/gap
variant range for the initial point, predictors and refinements. Calibration
samples appear in parameter panel A; their values remain in the receipt but
are not plotted in panels B/C. Both maximum heights are compared with
zero-height grazing. A zero-step or
partially accepted run remains publishable as a failure or accepted prefix;
it is not silently excluded. All 206 frozen source/input files still match
the rehearsed source snapshot. The plot preparation has not changed the
running worker or consumed a second attempt.

At 22:35 UTC the same task-owned worker remained alive (808 seconds elapsed),
with about 127 MiB of new raw run files retained. No point-completion or
scientific verdict was available in the operational log at that check.

Release housekeeping: EXP-521 (PR 87) and EXP-522 (PR 88) were normally merged
to main after all four checks on their final heads passed. EXP-520 (PR 86)
has passing checks but still needs its overlapping release documentation
reconciled with current main. No numerical source was altered to merge them.

## 23:21 UTC operational and release checkpoint

The task-owned worker was still alive after 58 minutes 50 seconds. The first
calibration point (`step-0-a-0`) had completed, bringing the operational count
to 104 IVPs and 83,598 periodic census segments. The host had 22,482,000 KiB
free; no successful full-audit receipt existed yet. These are operational
counts, not a scientific verdict. The frozen run and automatic audit continue
without a restart or a deadline change.

EXP-520's overlapping release documentation has now been reconciled and pushed
as `15b9639` on its existing PR 86. The reconciliation preserves the earlier
census, EXP-521's failed predictor and EXP-522's refinement, with no frozen
source changes. Focused tests passed (64 passed, one unchanged empirical
redraw deselected), all four frozen source sets matched their execution
commits, and the three real plan loaders passed. Its new CI checks still have
to finish before normal merge. PR 89's original checks were also still running.

The prospective EXP-523 figure receipt now explicitly records the title,
description, exact input artifact/hash and schema fields, numerical transforms,
generator/runtime/output provenance, non-color visual distinctions, missing-data
semantics, and hard guards. All 15 synthetic figure controls pass. This follows
the research-integrity figure contract and changes no numerical source or
target measurement. No empirical figure or new Jones claim is published here.

The separate local review caught an overbroad caption: panels B/C do not show
calibration ranges, only the initial point, predictors and refinements. The
footer, alt text, receipt's explicit per-panel selection, and this note now
state that distinction, with a regression assertion. All 206 physical frozen
source/input files still match the execution commit. This review is not an
independent replication of the numerical experiment.

Final focused verification: 41 tests pass across the renderer, controller and
runner suites. The corrected synthetic PDF was rendered and visually checked
locally (`artifacts/EXP-523/figure-control-07`); it is not research evidence.
This coherent figure-contract correction is pushed on PR 89, whose new final
head must earn fresh CI results before merge. No target process is affected.
