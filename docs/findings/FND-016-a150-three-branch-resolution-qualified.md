# FND-016 — `a=0.150` is a qualified chaotic three-branch set at adequate resolution

Status: passed prospective resolution-convergence and tighter-Lyapunov gate

## Result

EXP-119 prospectively reproduces the resolution model diagnosed by EXP-118 on
five new 2400-return datasets. All 30 coarse 20-bin control cells return two
branches. All 120 declared adequate-resolution cells (30, 40, 60, and 80 bins;
both coordinates; five initial states; three smoothings) return three. Every
dataset remains nonperiodic and supplies 2399 pairs per coordinate.

The critical geometry also converges. Maximum within-dataset span is
`0.01184`; maximum combined span across the new cells and frozen EXP-118
intervals is `0.01807`, both comfortably inside their `0.03` and `0.04` gates.
The new adequate-resolution intervals do not expand the frozen predecessor
envelope.

## Independent chaos qualification

With DOP853 tightened to `rtol=1e-11`, `atol=1e-13`, and `max_step=0.025`, both
initial states classify chaotic. Variational largest exponents are `0.05943`
and `0.05902`; independent two-trajectory estimates differ by at most
`0.00519`. The divergence-trace errors fall to `1.25e-7`, passing the unchanged
`1e-6` gate that EXP-118 narrowly missed.

## Implications

The apparent topology reversal from the qualified three-branch saddle at
`a=0.149` to EXP-109's nominal two-branch `a=0.150` candidate was numerical.
Twenty bins merge the shallow added extremum; converged 30--80-bin analyses
recover it. The local saddle-to-chaotic-set continuity is therefore supported,
not contradicted, across these adjacent samples.

This is good news for the Jones/Barrio branch-addition substrate and a direct
answer to a reviewer-type concern about demonstrating the extra extremum. It
also narrows the detector rule: branch-opening work must use a resolution
model and local uncertainty, never one global prominence cutoff.

## Claim boundary

EXP-119 qualifies one chaotic cell, not the TBA curve. It does not label the
support-poor `a=0.145` saddle, locate the boundary inside `[0.140,0.149]`, prove
template equivalence, or establish the global plane. The immediate next gate
is a larger, prospectively scaled `a=0.145` survivor ensemble using this
resolution model.

Raw receipt SHA-256:
`7206a97e5059ae60a32118645eaf12ec37ec514aaf9914fc60618e4fc5f9e37c`.
