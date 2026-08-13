# EXP-226 — Representation-safe endpoint qualification

Status: complete — passed all frozen gates

EXP-225 independently localizes the parent real-`-1` crossing and qualifies
the primitive child before it. DOP853 qualifies the parent double cover after
it, but Radau's redundant `2T` Newton correction is singular and reports only
`xtol` termination.

EXP-226 retains the exact root bracket, solvers, bilateral points, and every
threshold. The only change is representation-safe: on the right, Radau
independently corrects the stable fundamental parent and integrates it for
exactly twice its period. The resulting doubled trajectory must pass full
closure, `14/16` doubled section counts, half-period collapse, parent/child
state identity, stability, and monodromy-square gates.

A pass establishes a period-6 flip crossing bounding this sampled
one-dimensional path segment. At execution time it was interpreted as a
second crossing; EXP-229 later tests that interpretation directly.

Manifest:
[`../../experiments/manifests/EXP-226-returning-child-strip-endpoint.json`](../../experiments/manifests/EXP-226-returning-child-strip-endpoint.json).

## Result

Every gate passes. DOP853 and Radau independently localize the parent
real-`-1` crossing at `c=7.62537829761012` and `7.62537829364544`, differing by
`3.96e-9`; the corresponding DOP853 coordinate is
`a=0.240684352976565`. Root residuals are `-3.89e-10` and `1.71e-8`.

At `c_root-1.5e-4`, the primitive stable period-12 child passes full
DOP853/Radau qualification. At `c_root+1.5e-4`, both solvers recover a stable
period-6 parent and its exact double cover with `7/8` versus doubled `14/16`
section counts. DOP853/Radau parent moduli are `0.99209826/0.99209804`;
double-cover moduli are `0.98425894/0.98425852`. Their half-period closures are
`8.54e-8/1.75e-11`, and multiplier-square errors are
`2.08e-8/5.91e-9`.

Together with EXP-223, this qualifies a sampled stable period-12 strip through
45 exact returning-arm events and a period-6 flip crossing bounding that
strip on the frozen one-dimensional offset path. EXP-229 subsequently proves
that the crossing is the already-known EXP-217 returning arm: the path
recrosses the same event locus because its linearly interpolated offset drifts
by the curvature error. It does not establish a second plane curve, global
child-sheet endpoint, paired shrimp boundaries, TBA membership, or a
double-critical center.

Raw receipt: `artifacts/EXP-226/receipt.json`, 20,736 bytes, SHA-256
`59c30304622fb842f5017d86ff804a1ae5f9f966e2b2f5fac4ee9d1e80d56251`.
Compact receipt:
[`receipts/EXP-226.json`](receipts/EXP-226.json).
