# EXP-404 — Chained decreasing-a homoclinic successor

Status: frozen; not yet executed

EXP-403 passes all prospective gates under decreasing-`a` orientation, adds
the thirteenth qualified curve point, and demonstrates continuation through
the local `c` fold.  Its tangent, however, was computed at EXP-399.  A genuine
successor must recompute the local matching-Jacobian null direction at the new
qualified root.

EXP-404 binds EXP-399/EXP-403 as its exact previous/current pair, recomputes
the local tangent at EXP-403, orients it toward decreasing `a`, leaves `c`
unconstrained, and repeats normalized step `0.0011496701841098146`.  The
canonical unit-weight plane, wall-free bounds, 512 arcs, analytic
sensitivities, CSR/LSMR corrector, 40-evaluation budget, manifold/Radau
settings, and every root, arclength, conditioning, tangent, and margin
threshold remain unchanged.

A pass adds a fourteenth qualified above-section curve point and establishes a
chained step beyond the local fold.  It does not by itself qualify the
historical intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-404-jones-homoclinic-chained-decreasing-a-successor.json`](../../experiments/manifests/EXP-404-jones-homoclinic-chained-decreasing-a-successor.json).
