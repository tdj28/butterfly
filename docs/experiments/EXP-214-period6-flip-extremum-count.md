# EXP-214 — Extremum-partitioned qualification of the flip-curve grazing

Status: complete — passed all frozen gates

## Question

Does a crossing counter that explicitly partitions the orbit at every `y`
extremum recover the seven-to-six historical phase change around EXP-213's
continuous grazing?

## Frozen design

Eight exact flip events are corrected at four logarithmic `c` offsets on each
side of `c=6.93831802121`. Each period is partitioned by all `dy/dt=0` events;
the section equation is then root-bracketed separately on every monotone
interval before applying the historical half-plane gate. This construction
cannot skip a close pair merely because both roots lie inside one adaptive
integration step.

All lower points must have seven extremum-aware historical crossings and
positive grazing clearance; all upper points must have six and negative
clearance. Every point must retain eight Barrio phases and the invariant
real-`-1` orbit event. Radau independently repeats the two closest and two
intermediate offsets.

Manifest:
[`../../experiments/manifests/EXP-214-period6-flip-extremum-count.json`](../../experiments/manifests/EXP-214-period6-flip-extremum-count.json).

## Claim boundary

A pass establishes a local historical-section representation boundary on the
sampled flip curve. It does not establish a flow bifurcation, curve endpoint,
TBA event, or global shrimp mechanism.

## Result

All eight bilateral points pass. The extremum-partitioned historical counts
are exactly `7,7,7,7` below and `6,6,6,6` above the refined grazing, while the
Barrio count remains eight throughout. The standard collector disagrees at
three of the four lower-side points, directly confirming the close-pair loss.

Every point retains the exact real-`-1` flow-orbit event. Maximum orbit
residual is `6.04e-13`, maximum multiplier residual `3.19e-12`, and maximum
section-root residual `2.63e-13`. All four Radau controls reproduce the same
extremum-aware and Barrio counts; the largest cross-solver clearance difference
is `4.86e-12`.

Raw receipt: `artifacts/EXP-214/receipt.json`, 23,589 bytes, SHA-256
`9ab2233c6f78a5a77d41b8912d45fd1387ea99c0816cabd0086379b2ec77510a`.
Compact receipt:
[`receipts/EXP-214.json`](receipts/EXP-214.json).
