# EXP-390 — Physical-predictor homoclinic forward step

Status: executed; failed prospectively

EXP-387 and EXP-389 hit the same forward wall under nuisance weights `0.01`
and `0.003`, respectively.  EXP-389 passes the prospective conditioning gate,
so further plane retuning is not justified by those results.  Both runs use a
full-state secant predictor whose node, flight-time, and departure-angle
components may place the optimizer in the backward-root basin.

EXP-390 changes only predictor initialization.  It advances physical `(a,c)`
by the source secant to `Delta c=2e-5`, while holding all 511 internal nodes,
flight time, and angle at the qualified EXP-368 values.  The passed `0.003`
closing plane, forward optimizer wall, 512-arc representation, analytic
sensitivities, CSR/LSMR solver, Radau/manifold settings, bounds, budget,
`1e-8` root/arclength gates, and `5e-10` conditioning gate remain unchanged.

A pass adds a twelfth qualified curve point above `a=0.1798`.  It does not
qualify the exact historical fixed-`a` intersection, uniqueness, proof, or
global topology.

## Result

EXP-390 does not pass, but sharply separates orbit correction from the closing
geometry.  It terminates normally on `gtol` after 13 evaluations at

```text
(a, c) = (0.1798174950959779, 10.317081588741887)
maximum block defect = 6.275387542223247e-9
arclength residual = 9.54011175613445e-15
minimum Jacobian singular value = 2.1583023505600602e-9
```

The physical-only predictor lowers node motion by a factor of about 46 versus
EXP-389 and brings the matching blocks below the unchanged root-defect gate.
It still lands exactly on `c=current c+1e-7`, so the global-interiority gate
and therefore `root_nominated` fail.

The final angle moves by `0.141677` radians while `c` advances only `1e-7`.
Even at nuisance weight `0.003`, that gauge motion can close the secant plane
without taking the intended physical step.  The next method must derive its
local predictor and closing direction from the matching Jacobian at EXP-368,
not from the longer EXP-367/368 full-state secant.  No threshold is relaxed.

Raw receipt: `artifacts/EXP-390/receipt.json`, 80,684 bytes,
SHA-256 `a038cf8a1a6089b38e4f747a1e8ce8fb0b4f131aa5ef1f8ee48fcd396120231f`.
Compact receipt: [`receipts/EXP-390.json`](receipts/EXP-390.json).

Manifest:
[`../../experiments/manifests/EXP-390-jones-homoclinic-physical-predictor-forward-step.json`](../../experiments/manifests/EXP-390-jones-homoclinic-physical-predictor-forward-step.json).
