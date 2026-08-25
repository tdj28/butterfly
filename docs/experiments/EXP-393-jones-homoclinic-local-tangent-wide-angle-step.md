# EXP-393 — Wide-angle local-tangent homoclinic step

Status: frozen; not yet executed

EXP-392 preserves a machine-accurate local tangent and passing conditioning,
but stops simultaneously on its forward-`c` and departure-angle walls.  The
angle wall is independently active to `5.15e-11` normalized margin.

EXP-393 widens only the angle half-width from `0.25` to `1.0`.  The measured
local tangent, `Delta c=5e-7` (`0.09015` normalized step), 512 arcs, passed
`0.003` metric, analytic sensitivities, CSR/LSMR corrector, Radau/manifold
settings, all other bounds, budget, and every tangent, root, arclength,
conditioning, direction, and margin gate remain unchanged.

A pass adds a twelfth qualified above-section point.  A failure away from the
angle wall licenses a smaller normalized tangent step; neither outcome alone
qualifies the historical section, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-393-jones-homoclinic-local-tangent-wide-angle-step.json`](../../experiments/manifests/EXP-393-jones-homoclinic-local-tangent-wide-angle-step.json).
