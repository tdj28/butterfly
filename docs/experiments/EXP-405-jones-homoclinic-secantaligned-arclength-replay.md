# EXP-405 — Secant-aligned homoclinic replay

Status: frozen; not yet executed

EXP-404 recomputes the tangent at the qualified EXP-403 root and converges to
another clean, interior, conditioned root.  Its frozen decreasing-`a` gate
alone rejects the result: both `a` and `c` reverse locally, even though the
closing plane implies positive full-state signed arclength.  Neither displayed
parameter is therefore a reliable orientation coordinate at this scale.

EXP-405 prospectively aligns the recomputed matching-Jacobian tangent with the
previous EXP-399--403 full-state scaled secant.  It leaves both `a` and `c`
unconstrained and requires positive signed full-state arclength.  The exact
sources, normalized step `0.0011496701841098146`, canonical unit-weight plane,
wall-free bounds, 512 arcs, analytic sensitivities, CSR/LSMR corrector,
40-evaluation budget, manifold/Radau settings, and every root, arclength,
conditioning, tangent, and margin threshold remain unchanged.

A pass adds a fourteenth qualified curve point under the coordinate-free
pseudo-arclength protocol.  It does not by itself qualify the historical
intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-405-jones-homoclinic-secantaligned-arclength-replay.json`](../../experiments/manifests/EXP-405-jones-homoclinic-secantaligned-arclength-replay.json).
