# EXP-394 — Quarter-step local-tangent homoclinic continuation

Status: frozen; not yet executed

EXP-393's wide-angle control moves the departure angle well into the interior,
but the `0.09015` normalized tangent step remains on its forward-`c` wall,
above the matching gate, at the evaluation budget, and just below the frozen
conditioning floor.

EXP-394 implements the preregistered step reduction.  It reduces
`Delta c=5e-7` to `1.25e-7`, hence the normalized local-tangent step from
`0.09015` to `0.02254`, and proportionately reduces the prospective `c` floor
to `current+2.5e-9`.  It retains the `1.0` angle half-width, 512 arcs, analytic
sensitivities, weighted metric, CSR/LSMR corrector, 40-evaluation budget,
manifold/Radau settings, and every tangent, root, arclength, conditioning,
direction, and margin gate.

A pass adds a twelfth qualified above-section curve point.  Failure preserves
the eleven-point curve and triggers a coordinate/phase-gauge audit rather than
another post hoc threshold relaxation.  Neither outcome alone qualifies the
historical intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-394-jones-homoclinic-local-tangent-quarter-step.json`](../../experiments/manifests/EXP-394-jones-homoclinic-local-tangent-quarter-step.json).
