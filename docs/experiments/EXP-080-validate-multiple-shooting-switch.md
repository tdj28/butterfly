# EXP-080 — Validate the multiple-shooting branch switch

Status: preregistered after EXP-079; pending clean execution

At the already verified 40→80 event, build an eight-segment analytic matching
Jacobian and split its two-dimensional event nullspace into parent and
secondary tangents. Attempt both signs at frozen step lengths `0.0002`,
`0.0005`, and `0.001`.

Pass only if at least one corrected candidate has matching residual `<=1e-8`,
half-period closure `>=0.001`, full single-shooting closure `<=1e-8`, and
phase-aligned RMS `<=1e-5` to the independently established EXP-069 period-80
child at the same `b`. Passing validates the corrector and branch-direction
logic before applying it to period 320.
