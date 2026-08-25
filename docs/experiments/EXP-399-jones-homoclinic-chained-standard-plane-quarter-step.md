# EXP-399 — Quarter-size chained standard-plane step

Status: frozen; not yet executed

EXP-398 recomputes the local tangent at the passed corrected EXP-396 root and
finds a fully interior, conditioned root, but the `Delta c=1.25e-7` request
still returns `5.46911e-8` backward in `c`.  Direction is its only failed gate.

EXP-399 reduces both the requested `c` increment and normalized arclength by
four, to `3.125e-8` and `0.00459868`.  It retains the exact EXP-368/EXP-396
source bindings, freshly recomputed tangent, standard unit-weight plane,
wall-free bounds, final forward-direction gate, 512 arcs, analytic
sensitivities, CSR/LSMR corrector, 40-evaluation budget, manifold/Radau
settings, and every root, arclength, conditioning, tangent, and margin
threshold.

A pass adds a twelfth qualified above-section curve point.  A backward result
would resolve a local `c` reversal or source-scale floor rather than weaken the
eleven qualified points; neither outcome alone qualifies the historical
intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-399-jones-homoclinic-chained-standard-plane-quarter-step.json`](../../experiments/manifests/EXP-399-jones-homoclinic-chained-standard-plane-quarter-step.json).
