# EXP-211 — Identity-constrained recovery of the period-12 surface patch

Status: complete — passed all frozen gates

## Question

Does independent child-family interpolation and explicit nonclosure selection
recover the complete EXP-210 grid without its 16 doubled-parent collapses?

## Frozen design

The 124-cell grid and every scientific acceptance threshold are unchanged from
EXP-210. Each cell is now seeded independently: each EXP-209 anchor family is
interpolated in physical post-flip offset, then those three anchor states are
interpolated in `c`. The corrected root is accepted only if its half-period
closure exceeds `1e-3`. If that first root collapses, two declared EXP-210
seeds are attempted and the root with greatest half-period nonclosure is
selected. This fallback is diagnostic and cannot relax any surface gate.

All 124 cells must still pass closure, stability, primitivity, period ratio,
two-section identity, multiplier scaling, 31 opening-law fits, adjacent-orbit
coherence, and six DOP853/Radau controls.

Manifest:
[`../../experiments/manifests/EXP-211-period12-surface-recovery.json`](../../experiments/manifests/EXP-211-period12-surface-recovery.json).

## Claim boundary

A pass establishes a dense regular sampled period-12 surface patch under
explicit child-root identity. It does not erase EXP-210's failure, prove formal
continuity, continue global endpoints, measure basins, identify the TBA curve,
or establish double superstability.

## Result

All 124 cells pass, and all 124 select the independently interpolated EXP-209
seed without invoking either fallback. The 31 square-root opening exponents
lie in `0.502636--0.503088`, with minimum `R^2=0.99999696`. Maximum adjacent
child whole-orbit RMS is `0.005020`, ten times below its frozen limit.

Every period-6 parent is unstable, every period-12 child stable and primitive,
and all section counts are exactly 6/8 versus 12/16. The period ratios lie in
`1.999932--1.999993`, and the flip multiplier ratios lie in
`4.01176--4.12635`. All six Radau controls pass, with maximum DOP853/Radau
whole-orbit RMS `1.314e-8` and multiplier-modulus difference `1.453e-9`.

Raw receipt: `artifacts/EXP-211/receipt.json`, 244,973 bytes, SHA-256
`1e706b3c331c6261a358681ab127063c123fe8e30ba2e7ab24ee6a301edb9249`.
Compact receipt:
[`receipts/EXP-211.json`](receipts/EXP-211.json).
