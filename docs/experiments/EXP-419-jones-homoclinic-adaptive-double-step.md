# EXP-419 — Adaptive outgoing double-step

Status: frozen; not yet executed

EXP-416--418 pass three consecutive quarter-steps at the persistent
`3.20e-9` maximum-defect floor, with minimum singular value still above twice
its gate. EXP-419 binds the exact passed EXP-417/418 pair, recomputes the
tangent at EXP-418, and doubles normalized arclength to
`0.009197361472878517`. Every acceptance threshold remains unchanged.

A pass adds the twenty-seventh qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-419-jones-homoclinic-adaptive-double-step.json`](../../experiments/manifests/EXP-419-jones-homoclinic-adaptive-double-step.json).
