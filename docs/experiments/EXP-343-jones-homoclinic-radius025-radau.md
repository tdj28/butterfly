# EXP-343 — Radius-0.025 Radau homoclinic persistence

Status: frozen; not yet run

EXP-342 independently reproduces the radius-`0.03` root with 32 Radau arcs.
EXP-343 binds its exact matched nodes and changes only the nonlinear
stable-manifold matching sphere to radius `0.025`. The same global search box,
integrator settings, optimizer budget, and `1e-8` maximum arc-defect gate are
retained.

Because shrinking the sphere changes only where the same homoclinic orbit is
truncated near the equilibrium, `a` should remain invariant. The prospective
agreement gate permits at most `2e-6` change in `a`, `0.01` in departure angle,
and `0.1` in total flight time. Passing is one radius-persistence step, not a
radius-to-zero proof or uniqueness result; a radius-`0.02` successor remains
mandatory.

Manifest:
[`../../experiments/manifests/EXP-343-jones-homoclinic-radius025-radau.json`](../../experiments/manifests/EXP-343-jones-homoclinic-radius025-radau.json).
