# EXP-224 — Returning-child strip endpoint localization

Status: complete — administrative failure before receipt

EXP-223's full-range claim stops inside
`c=[7.6251864206,7.6254156527]` when the lower-offset parent becomes stable and
the nominal period-12 child collapses onto that parent traversed twice. EXP-224
tests the implied one-dimensional boundary directly.

On EXP-223's exact constant event-relative offset
`a-a_event=-5.7302368e-7`, the parent real-`-1` residual is solved independently
with DOP853 and Radau inside the frozen bracket. The two roots must agree within
`2e-7` in `c`. At `c_root-5e-5`, the period-12 child must remain primitive and
stable under full DOP853/Radau qualification. At `c_root+5e-5`, both solvers
must instead recover a stable parent and its double cover, tested by
half-period closure, parent/child state coincidence, period ratio two, and the
Floquet multiplier-square identity.

A pass establishes a second period-6 flip crossing bounding this sampled
one-dimensional child strip. It does not establish a global child-sheet
endpoint, continue a second flip curve in the plane, pair the broad arms as
shrimp boundaries, identify the TBA, or locate a double-critical center.

Manifest:
[`../../experiments/manifests/EXP-224-returning-child-strip-endpoint.json`](../../experiments/manifests/EXP-224-returning-child-strip-endpoint.json).

## Result

The scalar root stage completes, but the run stops before its atomic receipt
when the independent Radau child correction only `5e-5` below the root reports
`xtol` termination without satisfying the frozen corrector success condition.
No scientific pass/fail decision is available from EXP-224.

EXP-225 changes only the bilateral diagnostic distance to `1.5e-4`, retaining
both independently solved roots and every scientific threshold. The runner now
also serializes qualification exceptions as failed controls so a successor
cannot again terminate without an audit receipt.
