# EXP-050 — Identity-constrained period-5 continuation

Status: executed; passed

Restart from the independently verified EXP-022 period-5 orbit at
`(a,b,c)=(0.245,0.2,5.1)`. Continue at fixed `(a,c)` with a secant predictor,
but accept a corrected orbit only when one closed traversal has exactly five
legacy-section intersections. Wrong-family roots force step halving and remain
in the receipt.

Pass requires ten accepted points, at least two in each direction, closures
below `1e-8`, identity 5 everywhere, and at least one recorded rejected
wrong-family trial. Reaching either wide parameter guard is not required;
identity-safe termination is evidence about the branch's accessible extent.

## Result and decision

The clean run at commit `9fa0e76a162e72b71e0bedc63daebdf4947fcb98`
passed. Nineteen accepted rows all close below `9.30e-12` and have exactly five
section intersections. The accessible fixed-`(a,c)` branch spans
`b=0.17366943..0.20480835`. On both ends, repeated corrections converge to
six-crossing roots even after step reduction below `5e-5`; none are accepted.

A genuine real multiplier crosses `-1` in the bracket `[0.1825,0.185]`, with
linear estimate `b=0.18346567`. The period-5 parent is unstable below and
stable above that boundary. Receipt SHA-256:
`df83f5136762207d6a1f9385f55e946b33f0dd6015d1d86e71e92920a73de9fb`.

Accept the first identity-safe period-5 branch. Reject the spurious EXP-023
extensions outside this range. Refine the real `-1` crossing next, enforcing
five crossings at every bisection midpoint.
