# EXP-404 — Chained decreasing-a homoclinic successor

Status: executed; failed prospectively on coordinate direction alone

EXP-403 passes all prospective gates under decreasing-`a` orientation, adds
the thirteenth qualified curve point, and demonstrates continuation through
the local `c` fold.  Its tangent, however, was computed at EXP-399.  A genuine
successor must recompute the local matching-Jacobian null direction at the new
qualified root.

EXP-404 binds EXP-399/EXP-403 as its exact previous/current pair, recomputes
the local tangent at EXP-403, orients it toward decreasing `a`, leaves `c`
unconstrained, and repeats normalized step `0.0011496701841098146`.  The
canonical unit-weight plane, wall-free bounds, 512 arcs, analytic
sensitivities, CSR/LSMR corrector, 40-evaluation budget, manifold/Radau
settings, and every root, arclength, conditioning, tangent, and margin
threshold remain unchanged.

A pass adds a fourteenth qualified above-section curve point and establishes a
chained step beyond the local fold.  It does not by itself qualify the
historical intersection, uniqueness, proof, or global topology.

## Result

EXP-404 converges in two evaluations to a clean, interior, conditioned root,
but its frozen decreasing-`a` gate rejects it:

```text
(a, c) = (0.17981749367526342, 10.317081501703367)
Delta a from current = +1.384072856325247e-10
Delta c from current = -8.562697217939785e-10
maximum block defect = 4.004071816010325e-9
arclength residual = 5.4449907463291177e-14
minimum singular value = 1.6826266136701472e-9
local tangent residual = 1.0736508744588147e-16
```

Direction is the sole failed check.  The inferred full-state signed
arclength progress is positive, `0.0011496701841642646`, even though both
displayed parameters turn relative to their recent orientations.  Thus neither
`a` nor `c` is a reliable local direction coordinate.  Correct
pseudo-arclength continuation must orient the tangent by the previous
full-state secant and gate the signed full-state displacement.

The runner now implements that coordinate-free orientation and prospective
gate. EXP-405 replays the same source pair and normalized step with `a` and `c`
unconstrained; all numerical-quality thresholds remain unchanged.

Raw receipt: `artifacts/EXP-404/receipt.json`, 78,866 bytes,
SHA-256 `a9838f5525c0e1dee21e78da564b9a35f43e1f2b1c49197ba2b9069b3fd5750b`.
Compact receipt: [`receipts/EXP-404.json`](receipts/EXP-404.json).

Manifest:
[`../../experiments/manifests/EXP-404-jones-homoclinic-chained-decreasing-a-successor.json`](../../experiments/manifests/EXP-404-jones-homoclinic-chained-decreasing-a-successor.json).
