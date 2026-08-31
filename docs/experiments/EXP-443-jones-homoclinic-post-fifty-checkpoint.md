# EXP-443 — Conservative post-fifty-point successor

Status: frozen prospectively; not yet executed

EXP-442 closes the receipt-bound 50-point checkpoint at the defect floor, but
its minimum singular value is only `1.87x` the fixed conditioning floor.
EXP-443 therefore binds the exact passed EXP-441/442 receipts, recomputes the
tangent at EXP-442, and holds normalized arclength at
`0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-first qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-443-jones-homoclinic-post-fifty-checkpoint.json`](../../experiments/manifests/EXP-443-jones-homoclinic-post-fifty-checkpoint.json).
