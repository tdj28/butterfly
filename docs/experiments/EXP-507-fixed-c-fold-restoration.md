# EXP-507: one fixed-c fold restoration

## Question and timing

This is an outcome-informed corrective pilot, designed after inspecting the
complete EXP-504 rejection and EXP-506 output-quota deviation. At the rejected
EXP-504 point, can one bounded change to a restore the same full-state fold
proximity while retaining the primitive cycle and qualified boundary? It does
not resume EXP-504, erase its rejection, or independently verify a Jones chain.

EXP-504's first step missed fold proximity by 1.19%, despite a decreasing
dominant boundary residual and passing combined prediction error. The combined
norm concealed the wrong direction of its fold prediction. Accordingly this
new test isolates a correction of the fold residual; c and b do not move.

## Exact design

Use the uniquely rejected, numerically qualified EXP-504 point, preserving its
binary64 parameters exactly. From all 256 ordered representations, compute the
mean signed fold residual F and the mean normalized a derivative J from the
**original fine EXP-502/503 stencil**, not the rejected Broyden prediction.
Require every derivative positive and greater than 1e-8. Set the normalized
step to clip(-F/J, -.1, .1), then a_new = a_old + 1e-4 * step. Hold b and c
bit-identical. Require a nonzero realized step and the inherited original-a
distance bound .002. Save every variant's predicted two-component change.
This stale derivative is a proposed correction model, not a newly qualified
local derivative. No audience expectation or surprise claim is made.

Execute **one** point, one attempt, no fallback, line search or replacement.
Warm seeds, boxes and horizons use EXP-504 through the unchanged EXP-504
warm-plan constructor. Recompute all four fold representations with both ODE
methods, eight boundaries with both Decimal configurations, and both cycle
methods/windows. Keep every Newton trajectory, guard, mesh, coefficient stream,
prefix certificate, failure and all 26 parent candidates. The original and
adjacent cycle-index correspondence checks must both pass. All inherited
numerical, primitive six/eight count, event and full-state thresholds remain
unchanged. The upstream sources and all consumed attempts stay immutable.

Primary success: full point qualification plus both correspondence checks and
worst fold input/successor state distance <= 1e-4. Failure remains failure even
if the mean signed residual improves. Secondary descriptive endpoint: at least
50% reduction in absolute mean signed fold residual. Joint contact is reported
separately under the original all-variant 1e-4 rule; it is not required for a
fold-restoration result. An unqualified point cannot supply residual-change
interpretation. Report every predicted and observed variant, not a favorable
subset. These correlated representations are not independent samples.

## Resources and execution gate

Local CPU only; no new paid review, GPU rental, SSH computation or raw upload.
Maximum 512 IVPs, 3,600 seconds, 3 GiB of complete run output, 12 GiB initial
free disk and 8 GiB continuing floor. Reserve 1 MiB within the output cap for
a failure receipt. The separate exclusive attempt marker has a 1 MiB cap.
The budget is conservative relative to EXP-504's 200 IVPs, 668 seconds and
about 1.36 GB at one point; a different Newton iteration count is still bounded.

All uncompressed JSON uses bounded_json's complete serialization admission.
The two inherited JSON producer bindings are scoped to that writer; NPZ saves
are buffered one product at a time and admitted before bytes reach disk.
The unchanged Decimal JSON-lines serializer uses a quota-admitting compressed
sink. Each chunk is admitted before writing, including compression trailers.
No concurrent writers are supported. Empty/partial binary files after an
exception remain retained and invalidate completion. Summary references the
point file instead of duplicating its data. The auditor counts the complete
directory **including summary.json**, and rejects an overrun independently.

Before targets: analytic controller controls, serialization/quota regressions,
full source closure, authentic isolated copied-source startup, and a replay of
all 34 original analytic-control files must pass. Live-verify the clean pushed
source SHA. The one-shot marker is created only after startup and analytic
replay, immediately before new target evaluation. New code has no default
scientific side effects; execution requires --execute and exact source/ref.

The local design audit checks that primary acceptance uses full-state distances
rather than the scalar model, rejects a missing representation, preserves both
cycle identities, exposes the stale derivative and old rejection, includes
all data in accounting, and retains every new failure. This same-agent audit
and inherited raw replay are not independent-team validation. Paid review is
not requested under the human-directed major-milestone policy.

## Audit and claim boundary

Authenticate the entire raw inventory before interpreting values. Replay the
unchanged EXP-502 full-point auditor, original controls and new decision logic.
The new audit additionally checks total output bytes, compact summary linkage,
exclusive marker, exact source inventory, timings and integration counts.
Public code and compact comparison evidence may be released; full raw evidence
stays local and must not be described as remotely backed up or publicly
reproducible from compact values alone.

A success supports only this conditional numerical restoration at one measured
point. It does not prove an exact critical contact, identify C/D, establish a
generating partition, verify/refute a Jones p-to-p+1 arrow, prove global
continuity, or explain the whole parameter plane. A failure diagnoses this
specific correction proposal. Further constrained continuation requires a new
prospective design; no unmeasured path point is authorized here. A need for
new spending, restricted raw publication or relaxed scientific thresholds is
an escalation boundary, not permission to change this plan.
