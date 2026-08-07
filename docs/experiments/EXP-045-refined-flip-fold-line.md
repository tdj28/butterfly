# EXP-045 — Refined local fold line of the flip surface

Status: preregistered after EXP-044; pending clean execution
Manifest: `experiments/manifests/EXP-045-refined-flip-fold-line.json`
Claim target: smooth parameter drift of the flip surface's minimum-`b` fold

## Hypothesis and method

Combine the five EXP-043 traces with the EXP-044 extension at `c=5.3`. For
each `c`, use a frozen seven-point stencil around the sampled minimum in `b`,
parameterized by cumulative arclength in the complete nine-dimensional event
variables. Fit a local quadratic in arclength and evaluate its vertex to refine
the fold coordinate.

Fit the five refined `a_fold(c)` and `b_fold(c)` coordinates descriptively with
quadratics centered at `c=5.1`. Produce a provenance-bound three-dimensional
slice/fold-line figure and fold-drift projection.

## Acceptance and limits

All five local fits must have positive `b` curvature. Both fold coordinates
must decrease monotonically with `c`. Each descriptive quadratic must have
`R^2>=0.999` and maximum absolute residual at most `5e-4`.

Passing establishes a smooth sampled local fold line across `c in [4.9,5.3]`.
It does not establish the fold globally, identify a cusp or endpoint, or prove
that the fold line coincides with a shrimp caustic or TBA curve.
