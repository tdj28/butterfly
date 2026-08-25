# EXP-398 — Chained standard-plane homoclinic step

Status: frozen; not yet executed

EXP-397's canonical tangent plane finds a fully interior, well-conditioned
root but moves `1.16506e-7` backward in `c`.  That tangent was still computed
at the inherited EXP-368 state.  Passed EXP-396 provides a better corrected
512-arc root at the same location.

EXP-398 binds EXP-368 as the previous source and the hash-bound passed EXP-396
receipt as the current source.  It recomputes the local matching-Jacobian
tangent at EXP-396, orients it toward increasing `c`, and requests the same
`Delta c=1.25e-7`; the normalized step is measured from the new tangent rather
than assumed from EXP-368.  The standard unit-weight tangent normal, wall-free
interior bounds, final forward-direction gate, 512 arcs, analytic
sensitivities, CSR/LSMR corrector, 40-evaluation budget, manifold/Radau
settings, and every root, arclength, conditioning, tangent, and margin
threshold remain unchanged.

A pass adds a twelfth qualified above-section curve point.  A backward result
licenses a smaller chained step; neither outcome alone qualifies the
historical intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-398-jones-homoclinic-chained-standard-plane-forward.json`](../../experiments/manifests/EXP-398-jones-homoclinic-chained-standard-plane-forward.json).
