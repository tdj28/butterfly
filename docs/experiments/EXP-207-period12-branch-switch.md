# EXP-207 — Period-12 branch switching from the lower-c flip curve

Status: prospectively frozen before branch switching

## Question

Does the EXP-206 period-6 flip curve open a distinct doubled-period branch at
separated low, middle, and high `c` values?

## Frozen design

Events at `c=7.18,7.24,7.30` are represented over twice the period-6 flow
period. At each event, two fixed-`c` period-6 corrections define the primary
branch tangent. The doubled-period shooting Jacobian supplies a two-dimensional
nullspace, from which the orthogonal secondary tangent is selected. Both signs
are pseudo-arclength corrected and followed for ten steps with `a` free.

Each arm must provide at least eight corrected points, separate from the
doubled primary by `1e-4`, move in `a`, close within `1e-8`, and retain exactly
12 historical plus 16 Barrio section phases.

Manifest:
[`../../experiments/manifests/EXP-207-period12-branch-switch.json`](../../experiments/manifests/EXP-207-period12-branch-switch.json).

## Claim boundary

A pass establishes local period-12 branch arms at three separated parent-curve
points. It does not establish child stability, supercriticality, attraction,
arm equivalence, a continuous child surface, the TBA curve, or a
doubly-superstable center. Those require a separately frozen off-event audit.
