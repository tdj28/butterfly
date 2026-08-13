# EXP-211 — Identity-constrained recovery of the period-12 surface patch

Status: prospectively frozen before recovery

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
