# EXP-126 — Blind censor-aware PIM midpoint at `a=0.1485`

Status: preregistered; target not executed

## Question

Which PIM-resolved saddle topology occupies the midpoint of the independently
qualified finite sampled bracket `[0.148,0.149]`?

## Frozen design

EXP-126 changes only the target parameter and bootstrap seed from the passing
EXP-125 protocol. At `a=0.1485`, the same three fixed PIM access lines are
independently reconstructed at 128- and 256-return right-censor ceilings. Each
successful straddle advances 800 Poincare returns and discards the first 100.
Adaptive DOP853 retains `rtol=1e-10`, `atol=1e-12`, and `max_step=0.05`.

No expected count or prior critical-point location is encoded. Each profile
must complete at least two access lines, supply at least 1000 pairs, and resolve
all 15 oracle variants to the same allowed count in both `y` and `z`. The two
profiles must agree. Within-profile and cross-horizon normalized critical spans
remain bounded by `0.03` and `0.04`; the period-4 reference and every lifetime
integration must pass.

If the blind common count is two, the finite bracket becomes
`[0.1485,0.149]`. If it is three, the bracket becomes `[0.148,0.1485]`. Any
failure leaves `[0.148,0.149]` unchanged. No result establishes a continuous
TBA curve or an infinite-lifetime saddle.

Immutable manifest:
`experiments/manifests/EXP-126-blind-a1485-censored-pim.json`.
