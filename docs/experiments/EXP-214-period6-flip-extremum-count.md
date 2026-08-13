# EXP-214 — Extremum-partitioned qualification of the flip-curve grazing

Status: prospectively frozen before execution

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
