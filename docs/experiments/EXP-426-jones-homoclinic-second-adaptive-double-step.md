# EXP-426 — Second adaptive outgoing double-step regime

Status: frozen; not yet executed

EXP-423--425 qualify three consecutive post-checkpoint quarter-steps at the
`3.20e-9` defect floor. EXP-426 binds the exact passed EXP-424/425 pair,
recomputes the tangent at EXP-425, and doubles normalized arclength to
`0.009197361472878517`. Every acceptance threshold remains unchanged.

A pass adds the thirty-fourth qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-426-jones-homoclinic-second-adaptive-double-step.json`](../../experiments/manifests/EXP-426-jones-homoclinic-second-adaptive-double-step.json).
