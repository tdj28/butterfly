# EXP-340 — Absolute-Jacobian homoclinic shooting

Status: frozen; not yet run

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

Manifest:
[`../../experiments/manifests/EXP-340-jones-homoclinic-absolute-jacobian-shooting.json`](../../experiments/manifests/EXP-340-jones-homoclinic-absolute-jacobian-shooting.json).
