# EXP-390 — Physical-predictor homoclinic forward step

Status: frozen; not yet executed

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

Manifest:
[`../../experiments/manifests/EXP-390-jones-homoclinic-physical-predictor-forward-step.json`](../../experiments/manifests/EXP-390-jones-homoclinic-physical-predictor-forward-step.json).
