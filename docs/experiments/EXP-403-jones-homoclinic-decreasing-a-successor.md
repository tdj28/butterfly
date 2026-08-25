# EXP-403 — Decreasing-a homoclinic successor

Status: frozen; not yet executed

EXP-401 and its quarter-size EXP-402 replay both converge to clean, interior,
conditioned roots on the backward-`c` side of their positive-`c` predictors.
EXP-402 nevertheless moves downward in `a`, toward Jones's historical
fixed-`a=0.1798` section.  The branch has reached a local fold where `c` is no
longer a monotone or scientifically useful direction coordinate.

EXP-403 prospectively freezes decreasing `a` as the local-tangent orientation
and final progress gate.  It leaves `c` unconstrained and repeats EXP-402's
normalized step `0.0011496701841098146`.  The exact EXP-396/EXP-399 sources,
canonical unit-weight plane, wall-free bounds, 512 arcs, analytic
sensitivities, CSR/LSMR corrector, 40-evaluation budget, manifold/Radau
settings, and every root, arclength, conditioning, tangent, and margin
threshold remain unchanged.

A pass adds a thirteenth qualified above-section curve point and demonstrates
continuation through the local `c` fold.  It does not by itself qualify the
historical intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-403-jones-homoclinic-decreasing-a-successor.json`](../../experiments/manifests/EXP-403-jones-homoclinic-decreasing-a-successor.json).
