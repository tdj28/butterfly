# EXP-080 — Validate the multiple-shooting branch switch

Status: executed; failed frozen reach/identity gate

At the already verified 40→80 event, build an eight-segment analytic matching
Jacobian and split its two-dimensional event nullspace into parent and
secondary tangents. Attempt both signs at frozen step lengths `0.0002`,
`0.0005`, and `0.001`.

Pass only if at least one corrected candidate has matching residual `<=1e-8`,
half-period closure `>=0.001`, full single-shooting closure `<=1e-8`, and
phase-aligned RMS `<=1e-5` to the independently established EXP-069 period-80
child at the same `b`. Passing validates the corrector and branch-direction
logic before applying it to period 320.

The clean run at `0abfab04b4e7dcccc48c5ea09ab643a7b3bd20a1` failed the
prospective gate. All six multiple-shooting corrections converged, with
matching residuals between `2.84e-13` and `5.06e-13`, and the primary and
secondary tangents are orthogonal to `1.67e-16`. However, the largest frozen
step reached half-period closure only `2.08e-4` and moved `b` only
`2.98e-8` below the event. The independently stored child begins
`9.76e-6` below the event, so no candidate entered its comparison range and
none could pass the identity gate. Full receipt SHA-256:
`d967a4f0cfaa8cf26d54fa358b889fcd88c8fbbd09ccc4efa0581c3ffc2013a7`.

This does not reject multiple shooting or the period-80 child. The corrected
child-distinct amplitude grows approximately linearly with predictor size,
while the parameter displacement has the expected quadratic opening near a
flip. The frozen predictor scale was too local to overlap the independently
continued child. EXP-081 prospectively increases the scale and retains every
scientific acceptance gate unchanged.
