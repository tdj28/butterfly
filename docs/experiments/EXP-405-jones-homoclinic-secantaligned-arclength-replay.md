# EXP-405 — Secant-aligned homoclinic replay

Status: executed; passed all prospective gates

EXP-404 recomputes the tangent at the qualified EXP-403 root and converges to
another clean, interior, conditioned root.  Its frozen decreasing-`a` gate
alone rejects the result: both `a` and `c` reverse locally, even though the
closing plane implies positive full-state signed arclength.  Neither displayed
parameter is therefore a reliable orientation coordinate at this scale.

EXP-405 prospectively aligns the recomputed matching-Jacobian tangent with the
previous EXP-399--403 full-state scaled secant.  It leaves both `a` and `c`
unconstrained and requires positive signed full-state arclength.  The exact
sources, normalized step `0.0011496701841098146`, canonical unit-weight plane,
wall-free bounds, 512 arcs, analytic sensitivities, CSR/LSMR corrector,
40-evaluation budget, manifold/Radau settings, and every root, arclength,
conditioning, tangent, and margin threshold remain unchanged.

A pass adds a fourteenth qualified curve point under the coordinate-free
pseudo-arclength protocol.  It does not by itself qualify the historical
intersection, uniqueness, proof, or global topology.

## Result

EXP-405 passes every gate in two evaluations:

```text
(a, c) = (0.17981749367526337, 10.317081501703367)
Delta a from current = +1.3840723012137346e-10
Delta c from current = -8.562697217939785e-10
signed arclength progress = 0.0011496701841634165
maximum block defect = 4.004071829237827e-9
arclength residual = 5.4137862431346824e-14
minimum singular value = 1.6826267297404894e-9
local tangent residual = 1.3879884100989164e-16
```

This adds the fourteenth qualified curve point and validates coordinate-free
full-state pseudo-arclength across the local double turn in `(a,c)`.  The
nearest observed `a` remains EXP-403's `0.17981749353685614`; this first local
turn therefore does not reach the exact historical section.  Continued
full-state tracking is required to determine whether a later turn approaches
it again.

Raw receipt: `artifacts/EXP-405/receipt.json`, 79,057 bytes,
SHA-256 `b7148d4747a861f262384d50f1f376091f149fe68b9b75bb3add58b1582a0d9a`.
Compact receipt: [`receipts/EXP-405.json`](receipts/EXP-405.json).

Manifest:
[`../../experiments/manifests/EXP-405-jones-homoclinic-secantaligned-arclength-replay.json`](../../experiments/manifests/EXP-405-jones-homoclinic-secantaligned-arclength-replay.json).
