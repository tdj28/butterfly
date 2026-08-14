# EXP-291 — High-precision parent-side classification at the seventh birth

Status: frozen — not yet executed

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
