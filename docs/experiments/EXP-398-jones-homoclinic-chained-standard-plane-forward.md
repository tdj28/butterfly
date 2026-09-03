# EXP-398 — Chained standard-plane homoclinic step

Status: executed; failed prospectively after finding an interior backward root

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

## Result

EXP-398 converges cleanly in four evaluations but remains backward:

```text
(a, c) = (0.1798175179368785, 10.317081427044887)
Delta c from corrected current = -5.4691112083560256e-8
maximum block defect = 3.700476206118981e-9
arclength residual = 3.4203027779802775e-14
minimum singular value = 1.5301952439832897e-9
```

The recomputed tangent is machine-accurate at `1.36960e-16` residual and
changes the normalized requested step from `0.02254` to `0.0183947`.  Every
root, margin, tangent, conditioning, and optimizer check passes; direction is
the sole failure.  Corrected-source representation error is therefore not the
primary explanation for the sign reversal at this step size.

Under the frozen decision rule, EXP-399 reduces `Delta c` and normalized
arclength by four, to `3.125e-8` and `0.00459868`, while keeping the corrected
source, canonical plane, and every acceptance gate unchanged.

Raw receipt: `artifacts/EXP-398/receipt.json`, 79,151 bytes,
SHA-256 `a50453bfe9d77abfafc6b11a38b919d25132bb4e2b43424f24c77fcc065e4c38`.
Compact receipt: [`receipts/EXP-398.json`](receipts/EXP-398.json).

Manifest:
[`../../experiments/manifests/EXP-398-jones-homoclinic-chained-standard-plane-forward.json`](../../experiments/manifests/EXP-398-jones-homoclinic-chained-standard-plane-forward.json).
