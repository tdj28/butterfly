# EXP-227 — Local continuation of the second period-6 flip

Status: complete — passed all frozen gates

EXP-226 proves that the stable child strip meets a second period-6 flip on one
fixed offset path. EXP-227 tests whether that crossing belongs to a distinct
local plane curve rather than being an isolated or path-dependent coincidence.

Starting only from the DOP853 endpoint receipt, the exact augmented
orbit--real-`-1` system is solved at 21 fixed `c` values over
`c_root±2e-4`. Every point must pass orbit, phase, event-eigenvector,
normalization, real-multiplier, neutral-multiplier, and `7/8` two-section
identity gates. The candidate must remain at least `5e-8` lower in `a` than
the interpolated EXP-217 returning arm throughout the local grid. Both
endpoints and the center receive independent Radau event correction.

A pass establishes a distinct local second flip curve. It does not establish
broad continuation, close the child sheet globally, connect the curve to
either broad arm, prove paired shrimp boundaries, identify the TBA, or locate
a double-critical center.

Manifest:
[`../../experiments/manifests/EXP-227-second-period6-flip-local-curve.json`](../../experiments/manifests/EXP-227-second-period6-flip-local-curve.json).

## Result

All 21 coupled event solves pass over
`c=[7.62517829761,7.62557829761]`, with exact historical/Barrio counts `7/8`.
The resulting `a` range is `[0.24067639595,0.24069231097]`; maximum adjacent
`a` change is `7.96e-7`. At every point the new event remains lower than the
interpolated EXP-217 returning arm by `5.60e-7--5.85e-7`, passing the frozen
distinctness gate.

Maximum orbit, tangent, independent flip, and neutral residuals are
`8.55e-12`, `1.65e-12`, `9.74e-10`, and `2.77e-9`. Both endpoints and the
center pass independent Radau correction; the largest solver differences are
`1.37e-13` in `a`, `9.08e-14` relative period, `3.59e-12` in state, and
`5.52e-10` in multiplier modulus.

This promotes the EXP-226 path crossing to a distinct local second period-6
flip curve. EXP-228 freezes broad two-direction pseudo-arclength continuation
while preserving explicit separation from the source returning arm.

Raw receipt: `artifacts/EXP-227/receipt.json`, 26,411 bytes, SHA-256
`eb6581841bb60424300fd7eaf4c5aa6c4a22d0d508eec6d33ebf622b950bf806`.
Compact receipt:
[`receipts/EXP-227.json`](receipts/EXP-227.json).
