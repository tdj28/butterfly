# EXP-108 — Direct qualification of the published unimodal/bimodal controls

Status: executed; primary and coordinate-cross-check gates passed

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

The clean run at `aecadd631f83506f1353250de24f3a01ff9fcb8f` passed every
gate. All 21 `y` cells at `a=0.11` resolve as two branches, and all 21 at
`a=0.2` resolve as three. The 42 `z` cross-check cells return the same counts.
All 84 bootstrap consensuses equal `1.0`; coverage is at least `0.98`, and the
conditional-spread ratio is at most `0.02389`.

On the exact published plane with the baseline oracle, the unimodal `y` map
has one critical point at `-21.81693144`. The bimodal map has two at
`-29.49133356` and `-20.22314045`. The corresponding `z` maps independently
have one and two critical points. This is a direct computational reproduction
of both chaotic-attractor sides shown in Barrio et al. Figure 2, with frozen
uncertainty and section-perturbation gates. It does not reproduce the chaotic
saddles or locate the intervening TBA curve. Full receipt SHA-256:
`ca4c46ae06adc50528d7ea5828bd77ba60d0a9aac771de76cb0153e9101386f8`.
