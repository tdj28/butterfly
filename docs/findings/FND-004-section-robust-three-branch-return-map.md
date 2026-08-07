# FND-004 — A section-offset-robust three-branch scalar return relation

Date: 2026-08-07
Status: new local evidence; sensitivity audit pending

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

The next experiment must bind the full EXP-106 receipt and vary scalar
coordinate, crossing orientation, binning/smoothing/prominence thresholds, and
nearby parameters. Only after those gates pass may branch count be continued
as a parameter-space boundary and used to define reinjection.
