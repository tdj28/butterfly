# EXP-207 — Period-12 branch switching from the lower-c flip curve

Status: complete — strict branch-arm gate failed; three child candidates nominated

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

## Result

The strict branch-switching claim **fails** at all three events. The frozen
minimum was eight corrected points in each direction; each negative direction
produced one point and each positive direction produced none. Second negative
steps stopped with residuals from `8.30e-4` to `1.30e-3`, while the positive
first steps stopped with residuals from `4.55e-4` to `7.82e-4`.

This failure does not establish absence of the doubled child. At every event,
the negative switch direction produced one well-corrected, stable candidate
separated from the doubled parent by `0.00416`--`0.00430`. Their closure errors
are `3.24e-11`--`4.12e-10`, dominant transverse multiplier moduli are
`0.0235`--`0.2062`, and all retain exactly 12 historical plus 16 Barrio section
phases. Because these points were observed inside a failed branch-continuation
experiment, they are nominations only. EXP-208 must independently recorrect
the parent and child with DOP853 and Radau, demonstrate half-period nonclosure,
period ratio two, stability exchange, and solver identity before the manuscript
can call them period-12 children.

Raw receipt: `artifacts/EXP-207/receipt.json`, 7,383 bytes, SHA-256
`5cef4ec98795ebc04a52f78ba182ccc0d6ecb92b9f355357becd2f332b59b34f`.
Compact receipt:
[`receipts/EXP-207.json`](receipts/EXP-207.json).
