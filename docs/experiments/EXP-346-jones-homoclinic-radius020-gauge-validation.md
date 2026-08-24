# EXP-346 — Radius-0.02 nuisance-gauge validation

Status: frozen; not yet run

EXP-345 solves the radius-`0.02` matching equations below `1e-8` and preserves
`a` to `4.34e-13`, but its nearly null departure-angle coordinate reaches the
frozen boundary. EXP-346 binds those exact nodes and performs no further
optimization.

Only the nuisance-angle half-width is widened from `0.15` to `0.5`. Radius,
physical geometry, 32 Radau arcs, the `a` box, and the prospective `1e-8`
residual and `2e-6` parameter-persistence gates remain unchanged. The exact
seed must reproduce and be interior in a single evaluation.

Passing establishes numerical persistence across matching radii `0.03`,
`0.025`, and `0.02`. It does not establish the exact radius-to-zero limit,
Jones's printed coordinate, or uniqueness.

Manifest:
[`../../experiments/manifests/EXP-346-jones-homoclinic-radius020-gauge-validation.json`](../../experiments/manifests/EXP-346-jones-homoclinic-radius020-gauge-validation.json).
