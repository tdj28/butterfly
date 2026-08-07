# EXP-035 — Full unit-event pseudo-arclength below a=0.235

Status: executed; passed
Manifest: `experiments/manifests/EXP-035-event-pseudo-arclength.json`
Claim target: lower-`a` continuation boundary in EXP-034

## Hypothesis and method

The period-5 nontrivial-unit event continues past the fixed-`a` corrector
failure near `a=0.2325`. Treat state, period, `a`, `b`, and the event
eigenvector as nine unknowns. Couple flow closure, phase, `(M-I)q=0`, vector
normalization, flow orthogonality, and a secant pseudo-arclength condition in
one overdetermined corrector.

Use only the accepted EXP-034 events at `a=0.2375` and `0.235` as seeds, with
consistent eigenvector sign. Freeze a constant step equal to one half of their
nine-dimensional secant norm and attempt thirty downward-oriented steps. The
corrector may pass through an `a` turn; neither `a` nor `b` is fixed.

## Acceptance and limits

At least twelve new corrected points are required, with at least one reaching
`a <= 0.232`. Closure, eigen, flow-orthogonality, and arclength residuals must
each stay below `1e-8`, inside the declared `a` and `b` guards.

Passing demonstrates that the natural-continuation failure was a projection or
seeding problem and resolves the curve beyond it. It does not prove global
continuation, establish the same pitchfork normal form along the curve, or
construct the two-dimensional event surface under changes in `c`.

## Result

The first invocation returned control without a receipt and is operationally
void. The unchanged frozen command was repeated from clean commit
`3a7bbbe42fc046b25a10118f0aca1dd9f8282ee5`; the final receipt SHA-256 is
`ad7d09afa45068dbb41252ebaa7de93259302d3aff8d1824a908e7e62c9ad555`.

All thirty requested corrector steps passed. Maximum closure was `1.86e-12`,
maximum eigen residual `2.64e-13`, maximum flow-orthogonality residual
`1.66e-18`, and maximum arclength residual `3.15e-15`. The trace reached
`a=0.21432`, well beyond the frozen `a <= 0.232` gate.

The event curve contains one reversal in each coordinate projection. Its
minimum `b=0.2031697977` occurs near `(a,b)=(0.2185131,0.2031698)`. It then
continues toward smaller `a` and larger `b` before reaching minimum
`a=0.2143195988` near `b=0.2316951`, after which `a` also reverses. The final
point is `(a,b)=(0.2144529,0.2414185)`.

The provenance-bound figure is
`artifacts/EXP-035/EXP-035-event-pseudo-arclength.png` (SHA-256
`49fbe50d1ccfe7a6a9fd3e7fcab2c0faf14e7d0afebc58b45abbea2198f7f589`).

## Decision

Accept that EXP-034's lower boundary was a projection/seeding failure, not a
termination of the event set. At fixed `c=5.1`, the coupled period-5 `+1` event
curve folds in both its `a` and `b` projections. Consequently, a fixed `a` or
fixed `b` slice can encounter multiple events on this one curve. This supplies
a concrete mechanism by which the larger parameter-plane superstructure can
contain repeated stability exchanges and nested windows.

Do not yet call every point a pitchfork: EXP-031 established that normal form
only near the source event. Next continue the fold-safe event set as `c` varies
and repeat local branch-identity/scaling tests at spatially separated points.
