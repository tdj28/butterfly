# EXP-292 — High-precision correction of the seventh-birth parent

Status: completed — failed correction, neighborhood, and raw-convergence gates

EXP-291 shows that accurately integrating the Float64-corrected parent is not
enough: a `1.18e-12` orbit-representation difference exceeds the remaining
side-of-event signal. EXP-292 therefore corrects the periodic orbit itself in
50-decimal-digit arithmetic at the exact EXP-289 child coordinate.

For each classical-RK4 discretization (4,096, 8,192, and 16,384 steps per
segment), the 1,024 cyclic matching equations are eliminated analytically to
one phase-fixed 4-by-4 Decimal Newton system. Every profile must reach
`1e-25` matching and phase residuals while staying within `1e-6` of the source
nodes and period. The three corrected multipliers must retain fourth-order raw
and Richardson convergence, plus neutral, cyclic, and characteristic gates.

A pass qualifies one high-precision corrected classical-RK4 representation
and its converged multiplier, not criticality. A separately frozen RK4 3/8
correction must agree before the side of the event can be promoted.

Manifest:
[`../../experiments/manifests/EXP-292-period768-decimal-parent-correction.json`](../../experiments/manifests/EXP-292-period768-decimal-parent-correction.json).

## Result

All three Newton sequences reduce maximum matching residuals from
`6.15e-10/5.77e-11/3.49e-11` to
`1.18e-16/1.63e-15/1.85e-15` after four updates, with phase residuals below
`7.05e-52`. None reaches the frozen `1e-25` completion gate. More decisively,
the profiles move `7.32e-5/9.21e-5/9.32e-5` in state, well beyond the `1e-6`
source neighborhood, and their periods move by as much as `1.56e-6`.

The tracked `-1` characteristic root collapses toward zero in all profiles;
the raw convergence ratio is `3.339`, not fourth order. This is consistent
with unconstrained Newton correction approaching the nearby lower-period
double cover. The cyclic, characteristic, neutral, and Richardson-difference
checks happen to pass for that wrong representation and do not rescue the
claim.

EXP-292 therefore invalidates the promotion of event seven from frozen-node
multiplier agreement alone. FND-101 retracts FND-100's event claim. EXP-293
freezes an augmented high-precision orbit-plus-antiperiodic-tangent pilot whose
`-1` transport constraint excludes the double cover.

Raw receipt: `artifacts/EXP-292/receipt.json`, 13,198 bytes, SHA-256
`acbc7accff4e480536affad6ea062768b9936f870518e0afa5a81eb521bc5dd5`.
Compact receipt:
[`receipts/EXP-292.json`](receipts/EXP-292.json).
