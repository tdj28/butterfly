# EXP-519: testing whether the recovered fold can meet the orbit

## Current status

Pre-outcome implementation and validation in progress. No new target numerical
result is asserted here. EXP-518 is merged through PR84 after all four final-head
Python 3.12/3.13 push/PR checks passed. Main advanced to `1895bfd`; the successor
branch is `codex/exp519-fixed-c-fold-response`.

The next scientific test is not another figure of the same result: it computes
fresh a-derivatives for the recovered four/seven-return fold constructions,
recomputes the periodic orbit at four nearby parameter points, and permits one
bounded correction only after the fresh response qualifies. Both endpoints in
all three state coordinates must pass in every solver/construction/window
variant. The old x-only success remains an explicitly failed full-state
baseline. No paid Pro request, GPU rental or raw upload is involved.

## Local design audit before targets

This is a same-agent adversarial pass with separately coded scalar arithmetic,
not an independent team review.

| Objection | Resolution fixed before outcomes |
| --- | --- |
| Old h8 derivatives do not describe recovered h7 curves. | New h4/h7 family identities; four fresh points; no reused Jacobian. |
| Projected x can meet while z misses. | Six-component input/output residual and all-variant full-state radius; projection-only negative control. |
| Moving folds against a stale orbit can mimic contact. | New qualified periodic shooting and complete two-window observation at every point. |
| A multiple traversal can impersonate a primitive cycle. | Existing primitive geometry and six/eight event-count gates remain; retained analytic circle controls are replayed. |
| History/window changes can create a derivative by relabeling. | Fixed ordered sixteen-key matrix plus original/anchor index correspondence and complete fold prefixes. |
| A convenient stencil outcome can be cherry-picked. | All four stencil points run; only the prescribed single correction can supply the corrected endpoint. |
| A converged Newton equation can sit on a collapsed input. | Unchanged gain, projection, angle, curvature, region and complete-prefix gates. |
| A positive x derivative is assumed from old data. | Both common orientations are accepted; unresolved or inconsistent fresh slopes block correction. |
| A small x residual does not validate linear response. | Separate full-state prediction-error test; contact and prediction statuses reported separately. |
| Repeated recursive ancestry checks can dominate startup. | Hash-sensitive local input cache; actual isolated production startup is tested, not replaced by a fake receipt. |

The protocol is [EXP-519](../experiments/EXP-519-fixed-c-fold-response.md).
Implementation, tests, machine plan and raw auditor will be sealed and pushed
before the one-shot target run. Target outcomes and any failure will be recorded
below after the frozen audit, not inferred from unit-test success.

## Pre-outcome incident and repair

The first complete preflight (`artifacts/EXP-519/preflight-full-01.xml`)
finished with 37 passes and one failed source-identity check in 188.28 seconds.
The isolated child successfully validated the plan, but source/test edits made
while it ran meant its copied tree no longer matched the working tree. This is
an operational sequencing error, not a numerical failure. No target IVPs or
target attempt marker existed. The failed copied-source tree and test receipt
are retained. The final rehearsal must run without concurrent source changes;
the failed receipt is not used to authorize execution.

The local audit also added a sticky resource-abort guard before outcomes:
if a numerical producer catches a resource exception, the next budget check
still aborts the entire run rather than misclassifying the interruption as an
ordinary failed point. Synthetic IVP, clock and disk interruptions verify this
behavior without spending or generating a target outcome.

## Final preflight

With source held fixed, `preflight-final-02.xml` records **84 passed** in
188.63 seconds (EXP-519 plus EXP-518 transport and EXP-502 response tests).
The real isolated startup validates all 159 deployed files without ambient
raw artifacts or bytecode; its successful temporary public-file copy is
discarded only after hash comparison. `preflight-numerics-01.xml` records
**63 passed** in 3.74 seconds for periodic transport/minimal periods,
fold/cycle localization and bounded JSON/compressed products.

The machine plan binds 142 source paths and 24 input bindings (159 unique
deployed files). The fixed source is ready for the live public Git barrier and
one local execution. These are validation results, not target outcomes. All
control receipts, the failed first rehearsal, raw-upload restrictions and old
experiment failures remain preserved.
