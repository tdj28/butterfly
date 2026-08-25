# EXP-397 — Standard-plane local-tangent forward step

Status: frozen; not yet executed

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

Manifest:
[`../../experiments/manifests/EXP-397-jones-homoclinic-local-tangent-standard-plane-forward.json`](../../experiments/manifests/EXP-397-jones-homoclinic-local-tangent-standard-plane-forward.json).
