# EXP-391 — Local-tangent homoclinic positive control

Status: frozen; not yet executed

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

Manifest:
[`../../experiments/manifests/EXP-391-jones-homoclinic-local-tangent-positive-control.json`](../../experiments/manifests/EXP-391-jones-homoclinic-local-tangent-positive-control.json).
