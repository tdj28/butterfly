# EXP-415 — Defect-aware conditioned quarter-step

Status: frozen; not yet executed

EXP-414 passes but uses `78.5%` of the frozen maximum-block-defect gate.
EXP-415 binds the exact passed EXP-413/414 pair, recomputes the tangent at
EXP-414, and halves normalized arclength to `0.0045986807364392585`. Every
acceptance threshold remains unchanged.

A pass adds a twenty-third qualified point and tests safe progress into the
tighter-defect segment. It does not establish global nonintersection,
uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-415-jones-homoclinic-defect-aware-quarterstep.json`](../../experiments/manifests/EXP-415-jones-homoclinic-defect-aware-quarterstep.json).
