# EXP-216 — Adaptive flip continuation below the section grazing

Status: prospectively frozen before execution

## Question

Does EXP-215 stop only because its fixed arclength step is too large for the
local curve geometry, and can the same exact flip locus be traced to
`c<=6.05` without relaxing any scientific gate?

## Frozen design

The last two accepted EXP-215 events seed the same exact dual-parameter
pseudo-arclength system. The initial step is one quarter of their separation.
An inaccurate or identity-failing correction halves the step, down to
`0.00025`; three consecutive corrections requiring at most seven evaluations
grow it by `1.2`, capped at `0.03`. No failed candidate is retained.

At least 20 and at most 120 events are permitted. A pass requires reaching
`c<=6.05`, exact real-`-1` event gates at every point, persistent
extremum-partitioned historical/Barrio counts `7/8`, bounded adjacent parameter
jumps, and independent Radau recorrection of the terminal event.

Manifest:
[`../../experiments/manifests/EXP-216-period6-flip-adaptive-below-grazing.json`](../../experiments/manifests/EXP-216-period6-flip-adaptive-below-grazing.json).

## Claim boundary

A pass establishes a broader sampled lower parent arm. It does not locate its
physical endpoint, qualify the period-12 child sheet there, identify the TBA,
prove global connectivity, or establish double-critical membership.
