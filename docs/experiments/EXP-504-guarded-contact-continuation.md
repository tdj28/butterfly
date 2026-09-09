# EXP-504: eight bounded steps along the measured contact direction

Status: prospective, outcome-informed continuation pilot; no new target data.

## Question and scope

Can a short lower-c path reduce the limiting-boundary gap while retaining the
right-fold proximity, all representations, and the same primitive cycle?
EXP-503's sole measured correction is the starting point. Its result and
the original finite-difference response informed this design. No Jones word
is used to select a parameter, root, event index or stopping point.

The primary endpoint is simultaneous all-representation full-state proximity
at 1e-4 under the EXP-502 indices (fold input/successor index 3; limiting
predecessor index 1). The secondary endpoint is at least 20% reduction in
the infinity norm of the mean two-residual vector relative to the EXP-503
proposal, with every preceding path step accepted. Failed terminal points
cannot be replaced by the best earlier point. Neither endpoint identifies
C/D, proves an invariant quotient, verifies an arrow, or refutes Jones.

## Exact continuation rule

Keep all 256 correlated residual variants and their original order. Start
with their EXP-503 fine-scale 2x2 Jacobians in normalized (0.0001,0.002)
parameter coordinates. Apply one good-Broyden rank-one update using the
already observed original-anchor-to-EXP-503-proposal displacement and
residual change. This is explicitly an outcome-informed initialization.

At each of at most eight steps, solve the mean model against minus the mean
current residual. Radially clip the normalized step to infinity norm 10;
do not enlarge it, backtrack, retry, or select a different proposal. Require
strictly decreasing c, unchanged b=0.2, a within 0.002 of the original
anchor, and c within [original c - 0.2, original c]. Use the realized
binary64 displacement, not the requested displacement, for every check.

Every model matrix must remain finite, nonsingular, with condition number at
most 1e4 and determinant sign matching its original matrix. The mean model
must also pass those checks. Check the mean solve through a separately coded
scalar 2x2 inverse. Model conditioning is **not** measurement of the true
two-axis derivative away from the original stencil.

Measure the proposal with all four fold representations/two ODE methods,
all eight boundary representations/two decimal configurations, and both
primitive-cycle solvers/windows from EXP-502. Numerical tolerances, complete
event census, raw retention and full-state distance definitions are unchanged.
All 26 parent candidates remain in the ledger, including old failures.

Use warm numerical seeds from the immediately preceding accepted point:
the first cycle solver's corrected orbit (as in the original seed convention),
the mean paired fold u/time roots per representation, and the mean decimal
boundary u/time roots per representation. Keep root boxes u +/-0.02 and
time +/-1, fold horizon seed time +3, and the same upstream affine curves
and directions; update only their section y offset with parameters. This
seed change reduces redundant Newton iterations; it is not an independent
cold-start replication. Compare cycle index identity against both the previous
point and the original EXP-497 cycle using the unchanged 0.1 distance and
1e-4 margin limits. Do not rotate a failed row into agreement.

Accept a step only when all original point qualifications, both correspondence
checks, and fold-pair proximity pass; the mean residual norm strictly decreases;
and, for every variant, the Euclidean norm of observed minus predicted residual
change is at most 10% of max(predicted-change norm, 1e-12). Then update every
model by J' = J + ((deltaF - J s) s^T)/(s^T s). A scalar implementation
independently checks that update and the secant identity. All updated models
must pass conditioning/orientation checks before another step.

This renews a **directional secant model**, not a full independent Jacobian
stencil at each point. Report the frozen old linear baseline, realized step,
predicted and observed changes, model errors, and all failures. Stop at the
first failed rule, first qualified joint proximity, or eighth accepted point.
Retain an eight-slot ledger with explicit reasons for all unrun slots. No
restart of EXP-502/503, no second proposal for a failed slot.

## Execution and audit

CPU only; no cloud rental, model API, raw upload, package change or deletion.
One new marker under artifacts/EXP-504. Limits: 3072 target integrations,
7200 seconds, 10 GiB additional output, 19 GiB initial free and an 8 GiB
free-space floor. Reserve 64 MiB at the output boundary. Resource failure
preserves the complete partial inventory and consumes this attempt.

Before targets: validate exact public inputs; replay the original analytic
controls from their hash-bound local archive; pass synthetic linear, clipped,
nonlinear-rejection, singular, wrong-orientation, missing-variant, warm-seed,
step-ledger and startup controls; pass an isolated copied-source consumer;
complete local design audit and tests; commit and push all numerical sources,
protocol, plan and auditor. A paid Pro review is not requested under AGENTS.md.

After execution, hash the complete output before interpretation. Reconstruct
each warm plan, step, correspondence, model update and decision from its exact
predecessor, then use the frozen EXP-502 full raw point auditor on every
completed point. Preserve partial evidence separately. Publish a compact
receipt with public replay scope distinguished from the complete raw audit.
No favorable subset, best-step replacement or global contact claim is allowed.

Human escalation remains required for new paid review requests, exhausted
spending authority, disputed ownership, raw-upload boundaries or expansion
beyond the authorized Rössler research. A routine failed numerical gate leads
to a documented result and a separately frozen next design, not paid review.
