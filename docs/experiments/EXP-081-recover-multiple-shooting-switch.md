# EXP-081 — Recover the multiple-shooting switch at an overlapping scale

Status: executed; passed

Repeat the independently checkable period-40→80 multiple-shooting switch with
eight segments and frozen steps `0.005`, `0.01`, `0.02`, and `0.03` in both
secondary-tangent directions. These scales are motivated by EXP-080's measured
linear growth in half-period closure and quadratic parameter displacement: a
step near `0.02` should overlap the existing period-80 continuation.

The scientific gates are unchanged. Pass only if at least one candidate has
matching residual `<=1e-8`, half-period closure `>=0.001`, full
single-shooting closure `<=1e-8`, and phase-aligned RMS `<=1e-5` to the
independently established EXP-069 period-80 child at the same `b`. Both signs
remain mandatory, and every attempted result is retained.

The clean run at `98d6d2eb17688e322741aa5f2336a21be7b94047` passed.
All eight segmented corrections converged with matching residual at most
`6.15e-13`. Three prospectively accepted candidates recover the independent
period-80 child. Their half-period closures range from `0.00422` to `0.00661`,
their full single-shooting closures range from `6.05e-14` to `1.37e-12`, and
their phase-aligned identity RMS values range from `2.57e-8` to `3.43e-6`.
Full receipt SHA-256:
`0092fe285d5320e534f1f2b1a1ad8ea5ebe7fbe4256baa490867bba32df4217d`.

The multiple-shooting formulation and branch-direction construction are now
validated against a previously established child. Proceed to a prospectively
frozen 32-segment switch at the precision-consistent 160→320 event.
