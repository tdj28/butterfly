# EXP-397 — Standard-plane local-tangent forward step

Status: executed; failed prospectively after finding an interior backward root

EXP-396 passes the zero-step standard-plane control in four evaluations with
`4.00845e-9` maximum block defect, `1.69490e-9` minimum singular value, and
`0.002005` normalized node motion.

EXP-397 executes the licensed wall-free quarter step.  Relative to the control,
it changes `Delta c` from zero to `1.25e-7` (normalized step `0.02254`), uses
the prospectively frozen 40-evaluation forward budget, restores the forward
initial/plane gates (`0.01` and `1e-8`), and switches the direction check from
stationary to forward.  Relative to failed EXP-395, only the closing-plane
weights change.  The wide angle interval, 512 arcs, analytic sensitivities,
CSR/LSMR corrector, manifold/Radau settings, and every root, conditioning,
tangent, and margin threshold are unchanged.

A pass adds a twelfth qualified above-section curve point.  A backward result
or non-root remains a preserved failure; neither outcome alone qualifies the
historical intersection, uniqueness, proof, or global topology.

## Result

EXP-397 converges cleanly but does not pass:

```text
(a, c) = (0.17981753580258716, 10.317081372235611)
Delta c from inherited current = -1.1650627307346895e-7
maximum block defect = 2.803159052511406e-9
arclength residual = 1.8206139720811088e-14
minimum singular value = 1.0456336653497923e-9
```

The optimizer converges by gradient tolerance after 17 evaluations.  Every
root, margin, tangent, conditioning, and termination check passes, but the
result is backward in `c`; the direction gate is the sole failure.  The
standard plane improves conditioning relative to EXP-395 but does not create
a forward point when its tangent is recomputed at the inherited EXP-368 state.

EXP-396 already supplies a better corrected 512-arc standard-plane root at
this location.  EXP-398 therefore binds that passed receipt as the current
source and recomputes its local tangent before reducing the step.  This tests
source-root representation error without relaxing any gate.

Raw receipt: `artifacts/EXP-397/receipt.json`, 81,985 bytes,
SHA-256 `ec7cc02cc8dd86ea3d93f518591586abaa7ad732ad9eee821cad7a0c1fa3536f`.
Compact receipt: [`receipts/EXP-397.json`](receipts/EXP-397.json).

Manifest:
[`../../experiments/manifests/EXP-397-jones-homoclinic-local-tangent-standard-plane-forward.json`](../../experiments/manifests/EXP-397-jones-homoclinic-local-tangent-standard-plane-forward.json).
