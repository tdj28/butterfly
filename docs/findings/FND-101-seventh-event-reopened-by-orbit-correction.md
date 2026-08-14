# FND-101 — High-precision orbit correction reopens the seventh-event claim

Status: qualified negative result; event retraction superseded by FND-102

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

EXP-293 subsequently shows that the proposed augmented formulation can solve
the discrete orbit and antiperiodic-tangent equations without collapsing to
the double cover: residuals reach `2.75e-31/1.23e-30` and half-orbit RMS stays
`2.58e-5`. At 1,024 steps per segment, however, the corrected `a` lies
`4.50e-9` outside the source coordinate and beyond the frozen bracket, while
the pointwise tangent-neighborhood gate also fails. This promising pilot does
not supersede the retraction; resolution convergence remains mandatory.

EXP-294 supplies that resolution convergence under classical RK4. The
1,024/2,048/4,096-step `a` and period ratios are `15.718/15.706`; both the
finest coordinate `0.24070100821945930` and Richardson coordinate
`0.24070100823758015` lie inside the original bracket, and the primitive
augmented residuals fall below `1.32e-26`. The sole failure is persistent
pointwise disagreement with the old Float64 tangent field. Because that failure
does not shrink with resolution, independent agreement on the new orbit and
tangent line—not retroactive relaxation—is now required. FND-101 remains in
force until that test passes.

EXP-295 passes that test. FND-101 remains the reason frozen-node multiplier
agreement and unconstrained orbit correction were insufficient, but its open-
event conclusion is superseded by the independently converged augmented
orbit-plus-tangent result in FND-102.

Evidence:
[`../experiments/EXP-291-period768-decimal-parent-side.md`](../experiments/EXP-291-period768-decimal-parent-side.md)
and
[`../experiments/EXP-292-period768-decimal-parent-correction.md`](../experiments/EXP-292-period768-decimal-parent-correction.md),
with augmented follow-up in
[`../experiments/EXP-293-period768-decimal-augmented-correction.md`](../experiments/EXP-293-period768-decimal-augmented-correction.md)
and
[`../experiments/EXP-294-period768-decimal-augmented-refinement.md`](../experiments/EXP-294-period768-decimal-augmented-refinement.md),
with the superseding independent result in
[`../experiments/EXP-295-period768-decimal-augmented-independent.md`](../experiments/EXP-295-period768-decimal-augmented-independent.md).
