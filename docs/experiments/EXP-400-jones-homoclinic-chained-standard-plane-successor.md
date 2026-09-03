# EXP-400 — Chained standard-plane successor

Status: executed; failed prospectively after step inflation

EXP-399 passes every gate at normalized step `0.00459868`, adding the twelfth
qualified homoclinic-curve point and showing that the larger-step backward
roots were finite-step curvature effects.

EXP-400 binds the passed 512-arc EXP-396/EXP-399 roots, recomputes the local
tangent at EXP-399, and requests the same `Delta c=3.125e-8`; its normalized
step is measured from the new tangent.  The canonical unit-weight plane,
wall-free bounds, final forward-direction gate, 512 arcs, analytic
sensitivities, CSR/LSMR corrector, 40-evaluation budget, manifold/Radau
settings, and every root, arclength, conditioning, tangent, and margin
threshold remain unchanged.

A pass adds a thirteenth qualified above-section curve point.  Neither outcome
alone qualifies the historical intersection, uniqueness, proof, or global
topology.

## Result

EXP-400 converges to an interior, conditioned root but does not pass:

```text
(a, c) = (0.17981754860165525, 10.317081332869073)
Delta c from current = -1.7466870971816206e-7
maximum block defect = 3.593220973814375e-9
arclength residual = 4.199133987574377e-14
minimum singular value = 1.4711057734233137e-9
```

Direction is the sole failed check.  The reason is measurable: the scaled
local tangent's `c` component falls from `0.00169886` at EXP-396 to
`0.000398274` at EXP-399.  Holding `Delta c=3.125e-8` fixed therefore inflates
the normalized step from the passed `0.00459868` to `0.0196159`, again entering
the finite-curvature regime.

This preserves EXP-399's passed twelfth point.  The runner now supports a
prospectively fixed normalized-arclength step, automatically deriving the
local physical `c` request after positive-`c` tangent orientation.  EXP-401
replays this successor at normalized step `0.00459868` with all gates fixed.

Raw receipt: `artifacts/EXP-400/receipt.json`, 79,122 bytes,
SHA-256 `80db4786bd0af8f7601a9532653118034bfc4bf31d761ec233143385087e9221`.
Compact receipt: [`receipts/EXP-400.json`](receipts/EXP-400.json).

Manifest:
[`../../experiments/manifests/EXP-400-jones-homoclinic-chained-standard-plane-successor.json`](../../experiments/manifests/EXP-400-jones-homoclinic-chained-standard-plane-successor.json).
