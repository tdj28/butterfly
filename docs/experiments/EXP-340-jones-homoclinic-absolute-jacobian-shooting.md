# EXP-340 — Absolute-Jacobian homoclinic shooting

Status: completed; failed only the optimizer-termination gate; segmented
multiple-shooting successor required

EXP-339 passes execution but exposes an ineffective relative finite-difference
Jacobian at the zero normalized starting vector. Its actual perturbations are
about `1.49e-8`, not the intended `0.001`, and the 234-time-unit shooting map
does not resolve a useful local derivative at that scale.

EXP-340 binds the exact unresolved receipt and changes only numerical
differentiation: each Jacobian column is an explicit symmetric difference at
absolute normalized offsets `+/-0.001`. The EXP-337 source, fixed parameters,
nonlinear stable target, initial variables, search bounds, DOP853 settings,
optimizer tolerances and budget, `1e-8` root threshold, and claim limits are
unchanged.

An interior root remains a nomination for segmented multiple shooting,
shrinking radii, and independent integration.

## Result

The explicit Jacobian does improve the endpoint mismatch from
`0.000162262469` to `0.000135120195` (`16.73%`) while keeping all three
variables well inside the frozen search box. It nevertheless exhausts all 60
function evaluations, so `optimizer_terminated` is false and the experiment is
preserved as failed. The scaled Jacobian singular values are approximately
`6.837`, `1.546`, and `4.654e-5`, a condition ratio near `1.47e5`.

This is a diagnosis of the long single-shooting representation, not evidence
against Jones's homoclinic claim. Extending the same optimization budget is not
the prospective next step. A failure-bound segmented multiple-shooting solve
will use this interior endpoint as its seed and distribute the 234-time-unit
trajectory across short matched arcs.

Manifest:
[`../../experiments/manifests/EXP-340-jones-homoclinic-absolute-jacobian-shooting.json`](../../experiments/manifests/EXP-340-jones-homoclinic-absolute-jacobian-shooting.json).

Tracked summary: [`receipts/EXP-340.json`](receipts/EXP-340.json). Raw receipt
SHA-256: `02a4bf966256684352a1f63fece4f097b8ab9612ad2eeb21642e38048a5c0ea9`.
