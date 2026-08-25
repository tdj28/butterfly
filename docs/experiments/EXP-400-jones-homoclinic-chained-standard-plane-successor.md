# EXP-400 — Chained standard-plane successor

Status: frozen; not yet executed

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

Manifest:
[`../../experiments/manifests/EXP-400-jones-homoclinic-chained-standard-plane-successor.json`](../../experiments/manifests/EXP-400-jones-homoclinic-chained-standard-plane-successor.json).
