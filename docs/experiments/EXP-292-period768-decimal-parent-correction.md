# EXP-292 — High-precision correction of the seventh-birth parent

Status: frozen — not yet executed

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
