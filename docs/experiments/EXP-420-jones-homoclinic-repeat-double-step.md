# EXP-420 — Repeat outgoing double-step

Status: frozen; not yet executed

EXP-419 qualifies the first adaptive double-step with maximum defect
`3.794e-9`, minimum singular value `1.143e-9`, and two evaluations. EXP-420
binds the exact passed EXP-418/419 pair, recomputes the tangent at EXP-419, and
holds normalized arclength at `0.009197361472878517`. Every acceptance
threshold remains unchanged.

A pass adds the twenty-eighth qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-420-jones-homoclinic-repeat-double-step.json`](../../experiments/manifests/EXP-420-jones-homoclinic-repeat-double-step.json).
