# EXP-291 — High-precision parent-side classification at the seventh birth

Status: completed — failed at the frozen stable-side gate

EXP-289 independently classifies the period-1536 child as unstable at
`a=0.24070100817350334`, but its Float64 period-768 parent multipliers straddle
one inside the frozen neutral margin. EXP-291 evaluates the corrected DOP853
parent nodes at exactly that coordinate with independent classical-RK4 and RK4
3/8 integrations in 50-decimal-digit arithmetic. Both run complete 4,096,
8,192, and 16,384-step profiles on every one of 1,024 segments.

Each method must show order-four raw convergence and successive Richardson
agreement. The extrapolated flip multipliers must agree within `1e-7` and
their real-minus-one residuals must be positive by at least `1e-6`, ten times
that numerical agreement gate. Neutral, cyclic, characteristic, and orbit
matching gates remain mandatory.

A pass classifies the parent as stable at the identical coordinate where
EXP-289 already classifies the child as unstable and therefore qualifies the
seventh birth as locally subcritical. A failure is retained and leaves
criticality unresolved. It says nothing yet about a child saddle-node or a
stable period-1536 attractor.

Manifest:
[`../../experiments/manifests/EXP-291-period768-decimal-parent-side.json`](../../experiments/manifests/EXP-291-period768-decimal-parent-side.json).

## Result

Nine of ten gates pass. Classical RK4 and RK4 3/8 show raw convergence ratios
`15.970/15.960`; their successive Richardson estimates differ by
`8.97e-9/1.06e-8`, and their final flip estimates agree within `5.22e-11`.
All neutral, cyclic, characteristic, and orbit-matching gates pass.

The stable-side gate fails: the two extrapolated parent multipliers are
`-1.0000001149596/-1.0000001150118`, about `1.15e-7` on the unstable side,
not at least `1e-6` on the stable side. Thus the EXP-289 parent and child are
both unstable at the stored coordinate, and the seventh birth is neither
qualified as subcritical nor supercritical.

The corrected Float64 parent orbit differs from the event representation by
only `1.18e-12` node RMS and `2.30e-10` in period, yet those small differences
move the high-precision multiplier by more than the classification signal.
EXP-292 therefore freezes an actual 50-digit multiple-shooting correction of
the parent orbit at fixed `a`, rather than merely integrating a Float64-corrected
representation more accurately.

Raw receipt: `artifacts/EXP-291/receipt.json`, 15,371 bytes, SHA-256
`0030def998d90f85158c6ba23659a6b1f7eb49cb28c972962e1f19289c3ac230`.
Compact receipt:
[`receipts/EXP-291.json`](receipts/EXP-291.json).
