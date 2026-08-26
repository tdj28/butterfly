# EXP-411 — Repeated conditioned outgoing half-step

Status: frozen; not yet executed

EXP-410 recovers comfortable conditioning at normalized arclength
`0.009197361472878517`. EXP-411 binds the exact passed EXP-408/410 pair,
recomputes the tangent at EXP-410, aligns it with their full-state secant, and
repeats that step with every gate unchanged.

A pass adds a nineteenth qualified point and tests whether the conditioned
outgoing trend persists. It does not establish global nonintersection,
uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-411-jones-homoclinic-conditioned-repeat-halfstep.json`](../../experiments/manifests/EXP-411-jones-homoclinic-conditioned-repeat-halfstep.json).
