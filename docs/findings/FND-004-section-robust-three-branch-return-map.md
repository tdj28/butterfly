# FND-004 — A section-offset-robust three-branch scalar return relation

Date: 2026-08-07
Status: qualified local evidence; transition and two-dimensional mechanism pending

EXP-106 prospectively expected the published chaotic Rössler control
`(a,b,c)=(0.2,0.2,20)` to produce a two-branch scalar return relation on the
historical section. It did not. On the nominal section and plane offsets
`±0.005`, the `x_n -> x_{n+1}` relation resolves as three branches.

The result is unusually consistent:

- 1200 interpolated crossings per section;
- full populated-bin domain coverage;
- conditional robust spread ratio `0.01832027`;
- 100 of 100 bootstrap resamples returning three branches for every section;
- critical points near `x=-25.43355` and `x=-17.43792`; and
- maximum critical-point drift about `2.2e-6` across the offset perturbations.

This is good local evidence for the existence of the three-branch return-map
object emphasized by Jones. It does not establish Jones's stronger claims.
Specifically, EXP-106 does not locate a two-to-three transition, show rotation
of a reinjection observable, connect the third branch to `p -> p+1` windows, or
prove robustness under coordinate and crossing-orientation changes.

EXP-107 prospectively performed the required audit. All 105 combinations of
five nearby `(a,c)` points, three section offsets, and seven oracle settings
retain three branches for the negative-oriented `x` map. The independent `z`
coordinate also returns three in all 105 cells. Every bootstrap consensus is
`1.0`, and the graph-likeness and coverage gates pass.

The result does not extend indiscriminately to the opposite oriented half of
the full plane. There, 102/105 `x` cases are bootstrap-unstable, the other
three resolve as five branches, and all 105 `z` cases lack invariant-domain
coverage. This is not evidence against the qualified historical-half-plane
result. It is evidence that scalar branch count is representation-dependent
and cannot itself carry the full topological claim.

The next experiment may now search prospectively for a two/three boundary for
the qualified negative-oriented map. In parallel, the full two-dimensional
Poincare relation must be retained so that reinjection and topology are not
defined by a convenient scalar projection alone.
