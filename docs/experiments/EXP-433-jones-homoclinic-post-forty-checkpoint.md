# EXP-433 — Conservative post-forty-point successor

Status: frozen; not yet executed

EXP-432 closes the receipt-bound 40-point checkpoint with its defect at the
persistent numerical floor. Its smallest measured singular value is only
`2.01x` the fixed acceptance floor, so EXP-433 binds the exact passed
EXP-431/432 receipts, recomputes the tangent at EXP-432, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold remains
unchanged.

A pass adds the forty-first qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-433-jones-homoclinic-post-forty-checkpoint.json`](../../experiments/manifests/EXP-433-jones-homoclinic-post-forty-checkpoint.json).
