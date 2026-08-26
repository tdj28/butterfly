# EXP-406 — Chained secant-aligned homoclinic successor

Status: frozen; not yet executed

EXP-405 passes every coordinate-free gate and adds the fourteenth qualified
curve point.  It replays a tangent computed at EXP-403, so the next decisive
test is a true chain that recomputes the tangent at the new root.

EXP-406 binds EXP-403/EXP-405 as its exact previous/current pair, recomputes
the local matching-Jacobian tangent at EXP-405, aligns it with their full-state
scaled secant, and repeats normalized step `0.0011496701841098146`.  Both `a`
and `c` remain unconstrained; positive signed full-state arclength is the only
direction gate.  The canonical unit-weight plane, wall-free bounds, 512 arcs,
analytic sensitivities, CSR/LSMR corrector, 40-evaluation budget,
manifold/Radau settings, and every numerical threshold remain unchanged.

A pass adds a fifteenth qualified curve point and shows whether the first local
turn continues away from the historical section.  It does not by itself
establish a later intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-406-jones-homoclinic-chained-secantaligned-successor.json`](../../experiments/manifests/EXP-406-jones-homoclinic-chained-secantaligned-successor.json).
