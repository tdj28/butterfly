# EXP-385 — Unwalled weighted-plane homoclinic crossing

Status: frozen; not yet executed

EXP-384 aborts before solving because its exact passed EXP-383 warm start lies
below the optimizer's prospective `c>=current+1e-6` wall.  EXP-385 removes
only that optimizer bound.  It keeps the final forward-`c` acceptance check,
so a wrong-direction root still fails, and it keeps the explicit
`a<=0.1798` section requirement.

All mathematical settings remain unchanged: exact EXP-367/368 sources, exact
EXP-383 512-arc warm state, `Delta c=7.5e-5`, unit `a/c` and `0.01` nuisance
weights, analytic variational sensitivities, CSR/LSMR correction, Radau
tolerances, source-centered node/global bounds, and `1e-8` matching and
arclength gates.

Manifest:
[`../../experiments/manifests/EXP-385-jones-homoclinic-weighted-plane-crossing-unwalled.json`](../../experiments/manifests/EXP-385-jones-homoclinic-weighted-plane-crossing-unwalled.json).

A pass qualifies a bracket with EXP-368, not the exact fixed-`a` root or a
uniqueness claim.
