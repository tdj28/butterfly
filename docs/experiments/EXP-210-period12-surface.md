# EXP-210 — Dense fixed-offset period-12 surface patch

Status: complete — failed child-identity and surface-coherence gates

## Question

Can the isolated and fixed-`c` EXP-208/209 child results be extended into a
regular two-parameter period-12 surface patch over the dense EXP-206 flip
curve?

## Frozen design

All 31 exact EXP-206 event slices from `c=7.18` through `7.30` are crossed at
physical post-flip offsets `5e-6`, `15e-6`, `30e-6`, and `45e-6` in `a`. Each
of the resulting 124 fixed-parameter parent/child pairs is corrected directly,
avoiding EXP-207's ill-conditioned free-`a` nullspace predictor.

Every point must close, retain an unstable period-6 parent and primitive stable
period-12 child, preserve period ratio two and exact 6/8 versus 12/16 section
identity, and keep the flip multiplier ratio in `[3,5]`. At each of the 31
`c` slices, the four physical offsets must fit a square-root opening exponent
in `[0.4,0.6]` with `R^2 >= 0.995`. Neighboring children along each fixed-offset
line must agree phase-invariantly within RMS `0.05`. DOP853/Radau parity is
required at the six near/far-offset corner, center, and endpoint controls.

Manifest:
[`../../experiments/manifests/EXP-210-period12-surface.json`](../../experiments/manifests/EXP-210-period12-surface.json).

## Claim boundary

A pass establishes a dense regular sampled period-12 surface patch with local
normal-form scaling. It is not a formal continuous-surface theorem, global
continuation or endpoint result, basin-size measurement, TBA curve, or
double-superstability result.

## Result

The strict surface claim fails. Although all 124 cells complete and 108 pass
their pointwise gates, 16 child corrections collapse onto the double-covered
period-6 parent. At those cells the apparent opening RMS is below `1.69e-8`,
proper-subperiod closure is at numerical zero, and the doubled-parent
multiplier is unstable. These collapses corrupt the four-offset opening fits:
the minimum `R^2` is `0.0264`, the exponent range is `[-3.72,7.95]`, and maximum
adjacent whole-orbit RMS is `0.0870` versus the `0.05` gate.

This is a root-selection failure, not evidence that the child sheet ends.
Several collapsed cells are isolated between valid stable child corrections,
and EXP-209 independently qualifies the child at all three anchor slices.
EXP-211 must seed each grid cell independently from interpolated EXP-209 child
orbits and enforce proper-subperiod nonclosure before accepting a root.

Raw receipt: `artifacts/EXP-210/receipt.json`, 220,385 bytes, SHA-256
`4f9c5885d91754a29ac59d2d0bdfae7916f7a19d5d91ea91ff797fc1ccb211ce`.
Compact receipt:
[`receipts/EXP-210.json`](receipts/EXP-210.json).
