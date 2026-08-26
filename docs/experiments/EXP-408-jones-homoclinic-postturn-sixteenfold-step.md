# EXP-408 — Sixteenfold-base post-turn step

Status: frozen; not yet executed

EXP-407 passes at normalized step `0.0045986807364392585`, with only `0.00941`
normalized node displacement and ample global margins.  Its corrected point
moves decisively toward larger `a` and smaller `c` after the local minimum.

EXP-408 binds EXP-406/407, recomputes the tangent at EXP-407, aligns it with
their full-state secant, and increases normalized arclength fourfold to
`0.018394722945757034`.  Both parameters remain unconstrained and signed
full-state arclength remains the direction gate.  Every numerical-quality,
conditioning, margin, integration, and optimizer threshold is unchanged.

A pass adds a seventeenth point and accelerates the outgoing-branch trace.  It
does not establish global nonintersection, uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-408-jones-homoclinic-postturn-sixteenfold-step.json`](../../experiments/manifests/EXP-408-jones-homoclinic-postturn-sixteenfold-step.json).
