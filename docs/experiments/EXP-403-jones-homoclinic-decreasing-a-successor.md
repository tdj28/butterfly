# EXP-403 — Decreasing-a homoclinic successor

Status: executed; passed all prospective gates

EXP-401 and its quarter-size EXP-402 replay both converge to clean, interior,
conditioned roots on the backward-`c` side of their positive-`c` predictors.
EXP-402 nevertheless moves downward in `a`, toward Jones's historical
fixed-`a=0.1798` section.  The branch has reached a local fold where `c` is no
longer a monotone or scientifically useful direction coordinate.

EXP-403 prospectively freezes decreasing `a` as the local-tangent orientation
and final progress gate.  It leaves `c` unconstrained and repeats EXP-402's
normalized step `0.0011496701841098146`.  The exact EXP-396/EXP-399 sources,
canonical unit-weight plane, wall-free bounds, 512 arcs, analytic
sensitivities, CSR/LSMR corrector, 40-evaluation budget, manifold/Radau
settings, and every root, arclength, conditioning, tangent, and margin
threshold remain unchanged.

A pass adds a thirteenth qualified above-section curve point and demonstrates
continuation through the local `c` fold.  It does not by itself qualify the
historical intersection, uniqueness, proof, or global topology.

## Result

EXP-403 passes every gate in two evaluations:

```text
(a, c) = (0.17981749353685614, 10.317081502559637)
Delta a from current = -3.464635522920645e-10
Delta c from current = -4.978145895506714e-9
maximum block defect = 4.006366641443459e-9
matching norm = 1.4713407779193762e-8
arclength residual = 5.069595580276112e-14
minimum singular value = 1.685357240195257e-9
local tangent residual = 1.0896856617345182e-16
```

This adds the thirteenth qualified homoclinic-curve point.  It also validates
the fold-aware protocol: the numerical curve continues toward smaller `a`
while `c` reverses locally, so positive `c` was an invalid orientation gate at
this point rather than a failed homoclinic mechanism.  The remaining gap to
Jones's fixed-`a=0.1798` section is `1.7493536856150183e-5`.

Raw receipt: `artifacts/EXP-403/receipt.json`, 78,887 bytes,
SHA-256 `f22747d1996f80c9af2d9765a32115f755e988752e4ccf8de2847f663fe40bcf`.
Compact receipt: [`receipts/EXP-403.json`](receipts/EXP-403.json).

Manifest:
[`../../experiments/manifests/EXP-403-jones-homoclinic-decreasing-a-successor.json`](../../experiments/manifests/EXP-403-jones-homoclinic-decreasing-a-successor.json).
