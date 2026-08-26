# EXP-409 — Repeated post-turn homoclinic step

Status: frozen; not yet executed

EXP-408 passes the accelerated normalized step `0.018394722945757034` and
moves `a` upward by `1.01389e-7` with comfortable margins. EXP-409 binds the
passed EXP-407/408 pair, recomputes the tangent at EXP-408, and repeats the
same coordinate-free step and every numerical gate.

A pass adds an eighteenth point and tests persistence of the outgoing trend.
It does not establish global nonintersection, uniqueness, proof, or topology.

Manifest:
[`../../experiments/manifests/EXP-409-jones-homoclinic-postturn-repeat-step.json`](../../experiments/manifests/EXP-409-jones-homoclinic-postturn-repeat-step.json).
