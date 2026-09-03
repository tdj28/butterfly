# FND-075 — The period-6 flip edge continues as a dense coupled curve

Status: qualified at all 41 prospectively frozen points

EXP-206 starts from the central EXP-205 event and solves the periodic orbit,
free `a`, and anti-periodic tangent together using the exact first- and
second-variational Jacobian. Both continuation directions complete over
`c in [7.16,7.32]`, extending beyond the seven scalar-refinement slices.

All 41 points pass. The sampled curve moves monotonically from
`(a,c)=(0.2158160512164691,7.16)` to
`(0.2156835308258212,7.32)`. The maximum adjacent `a` step is `4.64e-6`.
Maximum orbit and tangent residuals are `1.10e-11` and `1.71e-12`; independent
monodromy places the real flip multiplier within `2.05e-9` of `-1`, and the
neutral multiplier within `1.82e-9` of `+1`. Every point retains six
historical-section and eight Barrio-section phases.

This replaces a stability-raster edge with a dense orbit-defined bifurcation
curve segment and is strong constructive support for Jones's period-doubling
organization. It does not equate the flip curve with the topology-transition
curve, establish global connectivity or endpoints, qualify a period-12 child
or supercriticality, or locate a doubly-superstable center.

Evidence: [`../experiments/EXP-206-lower-c-period6-flip-curve.md`](../experiments/EXP-206-lower-c-period6-flip-curve.md).
