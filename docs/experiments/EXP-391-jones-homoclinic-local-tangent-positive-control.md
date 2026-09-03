# EXP-391 — Local-tangent homoclinic positive control

Status: executed; passed prospectively

EXP-390 brings every numerical residual below its gate but remains on the
forward wall because the closing direction still comes from the long
EXP-367/368 full-state secant.  EXP-391 replaces that secant by the local
branch tangent obtained from a bordered solve of the underdetermined analytic
matching Jacobian at EXP-368.

This is a zero-step control.  The local tangent is oriented toward increasing
`c`, normalized in the frozen variable scales, and must have matching-Jacobian
residual at most `1e-8`.  The passed `0.003` metric, 512 arcs, CSR/LSMR
corrector, Radau/manifold settings, stationary-`c` gate, `1e-8` root gate,
`1e-10` plane gate, `5e-10` conditioning gate, bounds, and 12-evaluation
budget remain unchanged from the passed method controls.

A pass licenses one forward local-tangent step.  It does not add a curve point
or qualify the historical section, uniqueness, proof, or global topology.

## Result

EXP-391 passes every prospective gate:

```text
local tangent residual = 1.4056470405395967e-16
maximum block defect = 4.5847994637209154e-9
minimum bordered-Jacobian singular value = 1.9353811897810293e-9
```

The zero-step corrector terminates normally after four evaluations, holds `c`
within `4.78e-9`, and retains `0.99900` normalized node margin.  The local
tangent is highly node-dominated in the frozen scales: node norm `0.999992`,
versus `0.00138650` for `c` and `0.000902772` for `a`.  This quantifies the
long unstable orbit's sensitivity and explains why parameter-sized secant
steps were misleading.

Using the measured `c` tangent, a forward increment `Delta c=5e-7` corresponds
to normalized tangent step `0.09015`, below the `0.167--0.527` normalized steps
of the last three qualified predecessors.  That conservative first local step
is therefore licensed prospectively.

Raw receipt: `artifacts/EXP-391/receipt.json`, 79,064 bytes,
SHA-256 `659166ea43ed108540ed9650a043ab1b75145c0c64aa9554cde2cdbe2b3b93d4`.
Compact receipt: [`receipts/EXP-391.json`](receipts/EXP-391.json).

Manifest:
[`../../experiments/manifests/EXP-391-jones-homoclinic-local-tangent-positive-control.json`](../../experiments/manifests/EXP-391-jones-homoclinic-local-tangent-positive-control.json).
