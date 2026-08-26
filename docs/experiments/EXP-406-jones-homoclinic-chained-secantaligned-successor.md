# EXP-406 — Chained secant-aligned homoclinic successor

Status: executed; passed all prospective gates

EXP-405 passes every coordinate-free gate and adds the fourteenth qualified
curve point.  It replays a tangent computed at EXP-403, so the next decisive
test is a true chain that recomputes the tangent at the new root.

EXP-406 binds EXP-403/EXP-405 as its exact previous/current pair, recomputes
the local matching-Jacobian tangent at EXP-405, aligns it with their full-state
scaled secant, and repeats normalized step `0.0011496701841098146`.  Both `a`
and `c` remain unconstrained; positive signed full-state arclength is the only
direction gate.  The canonical unit-weight plane, wall-free bounds, 512 arcs,
analytic sensitivities, CSR/LSMR corrector, 40-evaluation budget,
manifold/Radau settings, and every numerical threshold remain unchanged.

A pass adds a fifteenth qualified curve point and shows whether the first local
turn continues away from the historical section.  It does not by itself
establish a later intersection, uniqueness, proof, or global topology.

## Result

EXP-406 passes every gate in two evaluations:

```text
(a, c) = (0.17981749430281954, 10.31708149974275)
Delta a from current = +6.275561736934776e-10
Delta c from current = -1.960616557994399e-9
signed arclength progress = 0.0011496701841669748
maximum block defect = 4.001427180559344e-9
arclength residual = 5.68764150292683e-14
minimum singular value = 1.6797417195867063e-9
local tangent residual = 1.5207059673504512e-16
```

This adds the fifteenth qualified point.  The recomputed tangent predictor and
corrected root both move toward larger `a` and smaller `c`, so the first local
`a` minimum remains above the historical section.  This is local evidence,
not a global nonintersection result; the curve can still turn again.

EXP-407 restores the fourfold-larger normalized step `0.0045986807364392585`
under the now-qualified coordinate-free protocol to measure the post-turn
trend efficiently without changing any numerical-quality gate.

Raw receipt: `artifacts/EXP-406/receipt.json`, 79,052 bytes,
SHA-256 `151bed4037530625f7a1be423ec871de460dcb4bd855be1ce032b5807c72ba6b`.
Compact receipt: [`receipts/EXP-406.json`](receipts/EXP-406.json).

Manifest:
[`../../experiments/manifests/EXP-406-jones-homoclinic-chained-secantaligned-successor.json`](../../experiments/manifests/EXP-406-jones-homoclinic-chained-secantaligned-successor.json).
