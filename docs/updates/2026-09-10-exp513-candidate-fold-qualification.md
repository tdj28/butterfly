# EXP-513: test the five recovered candidate intervals

## Current checkpoint

EXP-512 is merged to main at `d97b054c4c63c2e6088d6c39ccd8ee12b639f6da`
through PR #78 after all four final-head push/PR Python checks passed.
Its 130-file isolated public consumer also passes without raw artifacts.
The successor's pre-target validation is complete on a fresh branch. This
record is committed with the execution sources before any EXP-513 target
integration; no new scientific outcome is claimed at this checkpoint.

All 16 new target-free controls pass (32.63 seconds). The authentic isolated
136-file source/input consumer and both inherited analytic-control replays pass.
The complete regression suite passes **2,671 tests, one Linux-only skip**, in
381.96 seconds (`artifacts/EXP-513/preflight-suite-01.xml`). The frozen source
closure contains 124 paths. Startup and control receipts are retained beside
the test receipt.

Manifest SHA-256: `86b8e0fc1cd91a2d9a0e2675f00614d54cac7c69d14996cb3947a921690f2530`.

## What this test decides

The five endpoint sign changes are not five established folds. In the saved
data, adjacent event times sometimes differ by roughly one revolution.
Those finite endpoint differences motivate an event-consistent search but
do not themselves prove a discontinuity.

For every interval, independently observe its midpoint with both solvers.
Only a regular midpoint pair supplies a seed, using the observed ninth-return
time rather than averaging times from potentially different endpoint branches.
The unchanged projected-fold equations and qualification tests then decide
whether that bounded search found a locally regular numerical fold.
Compare the complete nine-return prefix under both solvers at all three
qualification offsets and compare qualified input/output states with all four
depth-four references. A root in the wrong physical location does not restore
the required representation.

All five intervals remain in the denominator. Midpoint failure, search-box
exit, nonconvergence, collapsed input, wrong ordinal, solver disagreement and
reference mismatch remain distinct outcomes. None proves global absence.
No parameter continuation, C/D assignment or Jones arrow is established here.

See the [prospective protocol](../experiments/EXP-513-candidate-fold-qualification.md).
The maximum is 160 local target integrations, 3,600 seconds and 2 GiB of new
raw products including summary, with an 8 GiB continuing free-space floor.
Existing analytic controls are replayed. No paid review, GPU worker or raw
upload is requested.

## Local design audit before freezing

- Selection covers every EXP-512 candidate, including the intervals with
  suspicious endpoint time differences; no favorable subset is selected.
- Midpoint observations seed the search but do not constitute a connected-domain
  proof. Failure of this particular seed or eight-step Newton procedure leaves
  the entire interval's root count unresolved.
- Newton changes the unknown initial coordinate and event time; DOP853/Radau
  still integrate the ODE, first variation and second variation.
- Full-state reference matching is stricter than matching x alone. The 1e-6
  cross-history threshold is unchanged, and the original x-region gate is
  reported separately from local fold qualification.
- Earlier event disagreements cannot hide behind agreement of just the final
  input/output pair. All nine returns are compared at all three offsets.
- The new wrapper retains failed census solver meshes before the inherited
  collector can raise. Unexpected or resource failures terminate the attempt
  with preserved evidence, not a regenerated success.
- Reused analytic controls, same-code raw replay and a separately coded scalar
  distance calculation are not independent-team replication or exact-flow proof.

Next: push and live-verify this exact source freeze, execute all five, audit
every new product, and publish the complete result before choosing a follow-up.
