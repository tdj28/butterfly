# EXP-077 — Precision-consistent period-160 flip

Status: executed; passed

Refine the directly measured tighter-solver bracket
`[0.17971388325058413,0.17971388330058413]` using the unchanged EXP-076
solver and acceptance settings. Require width `<=2e-14`, multiplier residual
`<=5e-9`, real multiplier, closure `<=1e-9`, and half-period closure
`>=5e-4`.

Passing supplies the precision-consistent 160→320 candidate and spacing ratio.
Period-320 existence and asymptotic universality remain open.

The clean run at `c9982621e6e649b689076b80f093af1f23c428f7` passed.
It locates the period-160 `-1` event at `b=0.17971388330053228` in a
`6.08e-15` bracket. The best multiplier residual is `-1.47e-9`, closure is
`2.35e-12`, and half-period closure is `0.00180322`. Receipt SHA-256:
`ae759656734b635ee08b9a33d7fabb14aac0b17839045b73f267a2d4bfc86761`.

Accept the 160→320 event candidate. The new spacing `6.48555e-6` gives ratio
`4.6646030`, within `0.0985%` of the frozen reference. This strengthens the
scaling evidence but still does not establish the period-320 child or an
asymptotic theorem.
