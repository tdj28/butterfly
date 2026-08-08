# EXP-107 — Adversarial sensitivity audit of the three-branch return relation

Status: executed; primary robustness passed, strong representation invariance failed

EXP-106 unexpectedly resolved three branches at the published chaotic control
instead of the prospectively expected two. Before using that observation in a
Jones-mechanism argument, audit whether it survives nearby parameters and
reasonable analysis choices.

The historical half-plane is not orientation-neutral: on its plane, its
`x<x_eq` gate forces `dy/dt<0`. Therefore this audit collects the full plane and
separates its negative and positive crossings using the vector field at each
interpolated root. This is a real comparison of opposite oriented halves, not
a relabeling of the same crossing set.

Freeze five parameter cases in the `(a,c)` plane at `b=0.2`: the published
center `(0.2,20)`, `a=0.198`, `a=0.202`, `c=19.8`, and `c=20.2`. At each case,
use the three EXP-106 section offsets `-0.005,0,+0.005`, both crossing
orientations, and both nondegenerate scalar section coordinates `x` and `z`.
The `y` coordinate is constant on this section and is excluded prospectively.

Run seven frozen oracle configurations: the EXP-106 baseline, 30 and 50 bins,
smoothing `1e-6` and `1e-4`, and prominence `0.02` and `0.05`. Every cell uses
100 deterministic bootstrap resamples. The resulting matrix contains 15
independent DOP853 integrations and 420 branch-oracle cells.

The primary claim under test is deliberately narrow: the negative-orientation
`x_n -> x_(n+1)` three-branch relation persists across all five parameters,
three offsets, and seven oracle configurations. It passes only if all 105
primary cells contain at least 1000 oriented crossings, resolve, and return
three branches. Failure is retained.

A stronger `representation_invariance_passed` diagnostic asks whether every
orientation/coordinate cell also resolves as three. This is not required for
the primary pass because critical-point counts of scalar projections are not
themselves topological invariants. A failure of that stronger diagnostic
limits the finding to its declared representation and motivates a
two-dimensional return-map or quotient construction; it may not be hidden.

The clean run at `d0259372ae139de19afd90fde37430571f7e2cfb` passed the
primary gate exactly: all 105 negative-orientation `x` cells resolved as three
branches. All 105 negative-orientation `z` cells independently resolved as
three as well. Across those 210 cells, bootstrap consensus was always `1.0`,
domain coverage stayed in `[0.94,1.0]`, and conditional-spread ratios stayed
in `[0.00722,0.02502]`. Every integration succeeded, every oriented sequence
contained 1204--1215 crossings, and no root was near the orientation cutoff.

The strong diagnostic failed informatively. On the positive-oriented half,
only three of 105 `x` cells resolved; all were the 30-bin variant at
`a=0.202`, and they returned five branches. The other 102 `x` cells failed the
bootstrap-consensus gate. All 105 positive-oriented `z` cells failed the
invariant-domain coverage gate, with coverage `0.24--0.667`; they were not
coerced into a branch count.

Therefore the qualified result is a locally parameter-robust,
section-offset-robust, coordinate-cross-checked three-branch relation on the
negative-oriented half-plane. It is not an orientation-independent scalar
topological invariant. The positive-half result supplies direct evidence for
the referee's concern that a scalar plot cannot replace the full
two-dimensional Poincare map. Full receipt SHA-256:
`3c6c6d60981c88b6fe5559a36bc7a45d1cfb11a050b5b36268588662666731b1`.
