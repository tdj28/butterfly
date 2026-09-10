# EXP-513: test the five recovered candidate intervals

## Completed result

**All five midpoint pairs are regular, but none of the ten bounded Newton
searches qualifies a fold.** Every first Newton proposal leaves its original
u interval, in agreement between DOP853 and Radau. The controller correctly
rejects those proposals before integrating outside the box and continues all
five candidates. This is not a failed ODE integration or a detected loss of
input regularity at the midpoints.

All **30 new IVPs** pass the full local raw audit: twenty midpoint guard/main
integrations and ten nine-dimensional shooting integrations. No root converges,
so no root-offset qualification censuses run, and reference correspondence
cannot be measured. `reference_restored=false` here means **not established**,
not a measured nonzero distance to a qualified root.

| Direction | Original interval nodes | First DOP853 proposed u (rounded) | Rejection |
| --- | --- | ---: | --- |
| 0 | [1,2] | -0.0189092093 | Beyond right endpoint |
| 0 | [15,16] | 0.0032474437 | Beyond left endpoint |
| 0 | [16,17] | 0.0127999897 | Beyond right endpoint |
| 1 | [17,18] | 0.0028878889 | Beyond left endpoint |
| 1 | [18,19] | 0.0037755897 | Beyond left endpoint |

These are **unintegrated Newton proposals**, not observed roots. They are
re-derived as `trace[0].u - trace[0].newton_step[0]` from each published fold
profile. The raw audit verifies the underlying nine-dimensional mesh and
separately coded Newton algebra. A full step leaving a box does not prove
the box contains no root. Neither a grazing boundary nor a missing physical
fold has been established by these failures.

## Evidence and release

Execution source: `dcf9d2bdb437960498d461b6e03a9dc69d38112f`, live-verified
before execution and preserved remotely as `codex/exp513-local-execution`.
The controller completed in 207.7216 seconds, retaining 84 files including
summary, totaling 310,915,345 bytes. No paid review, new worker or raw upload
was used. Old raw data, failures, markers and source closures remain unchanged.

Summary SHA-256: `d22a65aa4f44df98da97b297b8d0bf6da35f613c525e7ee8e214bb9d21b2b3cb`.
The [public result](../experiments/receipts/EXP-513-candidate-fold-qualification-result.json)
is an exact 595,188-byte copy of the full local audit, SHA-256
`64e60c557edf02ce0fabe17305e6049a6a043e3088812039e1dd07a9c2452741`.

```sh
PYTHONPATH=.:python .venv/bin/python -B scripts/verify_exp513_public_folds.py \
  --result docs/experiments/receipts/EXP-513-candidate-fold-qualification-result.json \
  --expected-sha256 64e60c557edf02ce0fabe17305e6049a6a043e3088812039e1dd07a9c2452741
```

The public verifier replays compact midpoint/event/qualification and reference
decisions and reconciles reported call counts. It does not repeat shooting
mesh/algebra, dense raw-data, control-bundle or disk-byte audits. Those new
raw products were audited locally and are not yet remotely released.

One first-draft public tamper test failed because it altered the first
reconstructed crossing, which was upward and excluded from the accepted
return sequence. The compact verifier does not check event-time/trajectory
consistency against private dense polynomials. The intended earlier-prefix
test now explicitly mutates the first **accepted** return. The draft and
interrupted release suite are preserved locally; neither frozen target source,
raw evidence nor scientific threshold changed. This correction does not expand
the public verifier's stated scope.

The corrected public suite passes all 17 integration/tamper tests in 63.59
seconds. A fresh 138-file public consumer passes under isolated Python with
no raw-artifact directory; every project import resolves inside the copied
source tree. The complete release regression suite passes **2,688 tests,
one Linux-only skip**, in 440.78 seconds (`release-suite-02.xml`). Its
predecessor's interrupted receipt is retained, not counted as a full-suite pass.

## Next substantive action

Prospectively replace full-step Newton seeding with **bracket-preserving,
event-aware refinement across all five original intervals**. Preserve the
endpoint and midpoint evidence from EXP-512/513. Before treating a narrowed
sign change as a fold, determine whether its event prefix remains on a smooth
return branch or approaches a grazing/domain cut. A candidate that converges
in u but retains a nonzero derivative, loses transversality or changes event
ordinal is not a qualified fold. Keep the original accuracy and curvature
gates; never turn this failed search into an absence claim or reset its attempt.

Post-result diagnostic from the saved profiles: all five midpoint slopes are
positive under both solvers. The opposite-sign endpoint is on the left for
direction 0 [1,2] and [16,17], and direction 1 [18,19]; it is on the right for
direction 0 [15,16] and direction 1 [17,18]. These remaining half-intervals
can seed a prospectively frozen refinement without repeating the midpoint
integrations. They are still numerical sign brackets, not continuity
certificates. Use the complete EXP-512 endpoints and EXP-513 midpoints with
explicit provenance, not an unlabeled merger of old experiments.

Only recovered full-state fold representations can support renewed joint-contact
continuation. Jones's flow-level symbolic chains remain unresolved.

## Preserved pre-target validation record

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

The source was subsequently pushed and executed as recorded above. This
pre-target design audit is retained, not rewritten to predict the failures.
