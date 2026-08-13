# EXP-216 — Adaptive flip continuation below the section grazing

Status: complete — failed decreasing-`c` target; qualified a returning arm

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

## Result

The frozen `c<=6.05` claim fails, but for a more informative reason than
corrector inaccuracy. Starting from EXP-215's last two points, the accepted
locus reaches a sampled minimum at `c=6.83093274`, then reverses its
`c`-projection and returns through 21 exact events to
`(a,c)=(0.2204843485,6.9999328849)`. All 21 retain raw/extremum historical and
Barrio counts `7/7/8`. Maximum orbit, event-eigenvector, arclength, and
extremum-section residuals are `1.67e-12`, `6.97e-13`, `6.84e-14`, and
`2.80e-13`.

The terminal event independently recorrects under Radau with `9.93e-13`
parameter difference, `9.49e-13` relative period difference, `1.65e-11` state
difference, and `1.80e-9` multiplier-modulus difference. The next predictors
are rejected before correction because the frozen `c<=7.0` guard is exceeded;
step halving reaches the minimum allowed step. This is an administrative guard
boundary, not a physical endpoint. EXP-217 prospectively expands only that
guard and continues the returning arm toward `c=8.25`.

Raw receipt: `artifacts/EXP-216/receipt.json`, 64,425 bytes, SHA-256
`c0dfcfc02153da3066e4e1198dd1a8ce9ada902c78afa4d584ab1c469b75f2e5`.
Compact receipt:
[`receipts/EXP-216.json`](receipts/EXP-216.json).
