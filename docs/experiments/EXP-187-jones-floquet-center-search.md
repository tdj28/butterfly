# EXP-187 — Target-word-blind period-6 Floquet-center search

Status: preregistered; not yet executed

## Question

Does the period-6 branch continued from EXP-186 contain a nearby, solver-
reproducible stationary saddle-zero of its signed dominant transverse Floquet
multiplier, as expected where two superstability curves intersect?

## Why this does not fit a Figure 6 word

For a scalar return-map reduction, a periodic orbit has zero longitudinal
multiplier whenever it contains a critical point. The two critical points of a
bimodal map therefore generate two zero-multiplier curves in the `(a,c)`
plane. Their transverse intersection should be locally modeled by a product
of two signed distances: the multiplier is zero, its gradient vanishes, its
quadratic Hessian is indefinite, and an enclosing ring has four sign changes.

EXP-187 searches for that geometry without opening the Figure 6 word table.
It uses only the exact landmark's independently qualified period-6 seed and
period. Expected symbols, alphabet labels, landmark-to-word associations, and
orbit-point critical membership are excluded from selection.

## Frozen search

At fixed `b=0.2`, DOP853 continues the period-6 orbit on a `21 x 21` grid
centered at `(a,c)=(0.21564,6.124)`, with steps `0.0005` and `0.025`. These
bounds equal four coarse EXP-021 a cells and 2.5 c cells on each side. Every
accepted cell must close below `1e-8`, have six negative-section returns, a
neutral multiplier within `5e-7` of one, a real dominant transverse
multiplier, and continuous whole-orbit identity to its predecessor.

Every complete `3 x 3` stencil is fitted by a normalized quadratic. A candidate
must have an interior stationary point, an indefinite Hessian, and at least
four cyclic multiplier-sign changes around the stencil. The immutable ranking
minimizes `|fitted stationary multiplier| + fit RMS`. Three `5 x 5`
refinements shrink both grid steps by factors `0.5`, `0.25`, and `0.125`.

Finally, DOP853 and Radau independently correct the selected center and its
eight-point ring. Both must preserve the four-sign-change topology; every
orbit pair must agree within scaled error `1e-6`, and signed multipliers within
`1e-5`. The fitted stationary multiplier and RMS must each be at most `0.005`,
and both directly evaluated center multipliers at most `0.01` in magnitude.

Manifest:
[`../../experiments/manifests/EXP-187-jones-floquet-center-search.json`](../../experiments/manifests/EXP-187-jones-floquet-center-search.json).

## Claim boundary

A pass nominates a dynamically located period-6 center candidate. It does not
yet prove that both independently reconstructed critical points lie on the
orbit. Survivor-derived critical-orbit membership under step and solver
controls is the mandatory successor before any Figure 6 word is encoded.
