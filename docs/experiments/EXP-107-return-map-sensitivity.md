# EXP-107 — Adversarial sensitivity audit of the three-branch return relation

Status: preregistered; not yet executed

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
