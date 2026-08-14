# FND-101 — High-precision orbit correction reopens the seventh-event claim

Status: qualified negative result and claim retraction

EXP-286/287 establish exceptionally close agreement between two 50-digit
multiplier integrations of the frozen EXP-281 period-768 representation. That
agreement is real, but it is conditional on the stored Float64 nodes and
period. EXP-289/291 then show that node RMS differences of only `1.18e-12` and
period differences of `2.30e-10` can move the deep-cascade multiplier across
the remaining `1e-7` side signal.

EXP-292 addresses that dependency by correcting the orbit itself at three
classical-RK4 discretizations in 50-digit arithmetic. Cyclic block elimination
reduces all 1,024 matching equations to an exact phase-fixed 4-by-4 Newton
system. The residuals fall as low as `1.18e-16` to `1.85e-15` after four
updates, but all profiles fail the frozen `1e-25` completion gate and leave the
`1e-6` source neighborhood by `7.32e-5` to `9.32e-5`. Their tracked `-1` root
converges toward zero, consistent with attraction to a nearby lower-period
double-cover representation. Raw convergence and source-neighborhood gates
therefore fail.

This does not prove that the seventh event is absent. It proves that accurate
multiplier integration on the frozen Float64 representation does not establish
an exact primitive event when unconstrained high-precision orbit correction
leaves that representation. FND-100's seventh-event promotion is retracted.
The qualified cascade remains six exact supercritical births through a stable
primitive period-768 child. The seventh event is again a candidate requiring a
high-precision augmented orbit-plus-antiperiodic-tangent solve; that tangent
constraint is designed to exclude the lower-period double cover.

The first six event coordinates, the stable period-768 child, and their
non-monotone finite spacing ratios are unaffected. No conclusion about a
seventh criticality direction, period-1536 attraction, limiting scaling,
universality, paired shrimp boundaries, TBA membership, double-criticality, or
global parameter-plane topology follows.

Evidence:
[`../experiments/EXP-291-period768-decimal-parent-side.md`](../experiments/EXP-291-period768-decimal-parent-side.md)
and
[`../experiments/EXP-292-period768-decimal-parent-correction.md`](../experiments/EXP-292-period768-decimal-parent-correction.md).
