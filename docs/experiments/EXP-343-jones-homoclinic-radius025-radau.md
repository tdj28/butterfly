# EXP-343 — Radius-0.025 Radau homoclinic persistence

Status: completed; preserved nuisance-gauge boundary failure despite a
sub-`1e-8` match and invariant `a`

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

## Result

The solve reaches maximum arc defect `5.49708e-9` in eight evaluations and
preserves `a` to `1.30e-13` relative to EXP-342. It nevertheless fails the
prospective source-root agreement gate: angle changes by `0.04983`, flight time
by `0.10973`, and the angle lands only `3.13e-7` normalized units inside the
old search boundary.

The experiment is therefore not reclassified as passing. The observed failure
is confined to the nearly null angle/time gauge; the invariant parameter and
matching equations show the expected persistence. A failure-bound successor
will widen only the nuisance-variable gauge and will reassess these exact
matched nodes without relaxing the `a` or residual thresholds.

Tracked summary: [`receipts/EXP-343.json`](receipts/EXP-343.json). Raw receipt
SHA-256: `b3e5d603de968f648ca8c304b4462885db6c0baaae5b66f4002526f88bd1ce1f`.
