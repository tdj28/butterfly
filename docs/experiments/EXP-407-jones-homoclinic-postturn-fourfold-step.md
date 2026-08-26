# EXP-407 — Fourfold post-turn homoclinic step

Status: frozen; not yet executed

EXP-406 passes the first genuine secant-aligned chain and confirms that the
recomputed tangent and corrected point both move toward larger `a` after the
local minimum.  Its normalized node displacement is only `0.00235144`, leaving
ample room inside the unchanged bounds.

EXP-407 restores the previously exercised fourfold-larger normalized step
`0.0045986807364392585`.  It binds EXP-405/EXP-406, recomputes the tangent at
EXP-406, aligns it with their full-state scaled secant, leaves `a` and `c`
unconstrained, and requires positive signed arclength.  All root, arclength,
conditioning, tangent, margin, integration, and optimizer settings remain
unchanged.

A pass adds a sixteenth qualified point and measures the post-turn trend more
efficiently.  It does not by itself establish global nonintersection,
uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-407-jones-homoclinic-postturn-fourfold-step.json`](../../experiments/manifests/EXP-407-jones-homoclinic-postturn-fourfold-step.json).
