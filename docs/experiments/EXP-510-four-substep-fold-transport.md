# EXP-510: smaller-step transport of the qualified fold branch

## Question and outcome exposure

Can four fixed substeps retain the qualified fold representations from
EXP-507 at the same endpoint where EXP-508's single predictor lost its
depth-8 input-curve regularity? EXP-509's complete raw replay exposed the
depth-8 collapse, same-sign neighboring slopes, all shorter-history successes
and the unchanged endpoint cycle/boundary comparisons before this design.
This is outcome-informed method development, not a blind confirmation.

## Fixed design

Interpolate linearly in a and c at fractions 1/4, 1/2, 3/4 and 1 between
EXP-507 and the exact saved EXP-508 predictor; b remains .2. The endpoint is
copied exactly, not rounded. This changes the warm-start path, not the final
parameter question. Every executed substep contains all four fold families,
both solvers and every prescribed shooting/census/guard archive. No fallback,
family deletion, selected successful subset or target-word optimization.

Seed each candidate with the arithmetic mean of both fully qualified
predecessor roots. Keep u +/- .02, time +/- 1 and the original horizon rule,
integrator tolerances, iteration count, displacement, event census, input gain,
opposite-slope and solver/region qualification gates unchanged. Never use the
failed depth-8 roots as warm predecessors. Stop after a failed substep only
after retaining all four families and both solvers at that substep.

Additionally require the scaled componentwise spread of all eight qualified
input states and all eight output states to be <= 1e-6 across histories and
directions, and each solver/family's scaled displacement from its predecessor
to be <= .01. Scales remain [15,15,.01]. These are finite numerical identity
checks, not a theorem of unique branch continuation. A separately coded
scalar audit cross-checks the vectorized calculations. A collapsed input
curve remains inadmissible even when its determinant equations converge.

## Controls, freeze and resources

Synthetic tests cover complete transport, failed representations, missing
families, cross-history disagreement, excessive adjacent displacement,
unchanged inputs, refusal to seed from failed roots, conditional endpoint
reporting, scalar arithmetic agreement and the real clean-interpreter entry
point. Recheck the original retained analytic controls and an isolated
copied-source startup. Run the complete local suite; commit and push the exact
source/plan/protocol closure and verify its live remote before execution.

One new attempt and output namespace; at most 512 IVPs, 1,800 seconds and
2 GiB including final summary. Start with 12 GiB free and retain an 8 GiB floor
and 1 MiB failure-record reserve. Use the existing tested bounded writers for
every raw and JSON product. No new periodic cycle, Decimal boundary, paid
review, GPU worker, remote compute or raw upload is authorized by this plan.
Preserve every old failure and marker unchanged.

## Audit and claim boundary

Authenticate the complete inventory and source/input/startup/attempt bindings.
Recompute every fold's shooting, event census, guard continuity, finite
differences and solver comparisons from retained raw arrays; reconcile every
IVP and output byte including summary. Rebuild all proposed seeds and substeps
from the original start and qualified predecessors, not from saved assertions.
Report all executed stages and explicit unrun reasons, with the full parent
ledger. Publish the compact audit as distinct from full local raw availability.

If all four substeps qualify, compare the new endpoint folds with the
unchanged, explicitly hash-bound EXP-508/509 cycle using both vector and scalar
distance calculations. The old boundary gap is context only. This is not a
new complete joint point, and no cycle at intermediate parameters is inferred.
Successful fold transport cannot establish contact, a generating partition,
an exact C/D symbol, or a Jones p-to-p+1 chain. The endpoint is expected to
still require a fold-contact correction; that correction is not part of this
experiment. If transport fails, diagnose the retained failure rather than
weakening its acceptance thresholds or resetting an attempt.
