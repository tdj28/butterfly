# EXP-108 — Direct qualification of the published unimodal/bimodal controls

Status: preregistered; not yet executed

The transition search must not conflate two different Poincare sections.
EXP-106/107 qualified the section recovered from the Jones code: a plane
through the small equilibrium's `y` coordinate, gated to its negative-oriented
half. Barrio, Blesa, and Serrano instead declare
`x=x_minus`, `dx/dt>0`, where `x_minus` is the small equilibrium's `x`
coordinate. Figure 2 reports a unimodal/two-branch chaotic attractor at
`(a,b,c)=(0.11,0.2,20)` and a bimodal/three-branch chaotic attractor at
`(0.2,0.2,20)`.

Implement the published section directly and freeze those two controls before
searching for a boundary. The figure does not label its scalar axis, so `y` is
the prospective primary coordinate and `z` is a separately reported
cross-check; a primary failure may not be relabeled after seeing `z`.

At each control, use the exact published plane and offsets `-0.001,0,+0.001`.
Cross those with the seven EXP-107 binning/smoothing/prominence settings and
100 deterministic bootstraps, for six DOP853 integrations and 84 oracle cells.

The primary gate passes only if all 42 `y` cells have at least 1000 crossings,
resolve, and return the published branch count: two at `a=0.11` and three at
`a=0.2`. The `z` result is a strong coordinate cross-check, not a substitute
for the primary gate. Failure is retained. Passing authorizes a prospectively
frozen `a`-path boundary search at `b=0.2,c=20`; it does not yet continue the
TBA through regular windows, which requires a chaotic-saddle method.
