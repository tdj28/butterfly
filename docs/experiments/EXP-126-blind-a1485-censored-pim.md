# EXP-126 — Blind censor-aware PIM midpoint at `a=0.1485`

Status: passed

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

## Result

EXP-126 passes from clean commit `e78ec6a` in `3840.50 s`. All six fixed PIM
access lines complete, three at each censor ceiling. Each profile contributes
2097 post-burn-in pairs per coordinate. Both `y` and `z` select three branches
at both 128 and 256 returns; all 15 oracle variants agree in each decision, for
60/60 three-branch cells and no two-branch or unresolved result.

The combined 128/256 normalized critical spans are `0.014702` in `y` and
`0.008531` in `z`, below the frozen `0.04` gate. The stable period-4 reference
passes. The 128 profile contains 119 right-censored lifetime evaluations and
104 certified censor-block selections under the already qualified rule; the
256 profile contains none. No lifetime integration fails.

The independently targeted PIM saddle at `a=0.1485` is qualified as
three-branch. Together with the blind two-branch EXP-125 result at `a=0.148`,
this narrows the finite sampled classifier bracket to `[0.148,0.1485]`. It does
not yet establish a continuous TBA curve or infinite-lifetime saddle.

Tracked compact receipt: `docs/experiments/receipts/EXP-126.json`. Raw receipt
SHA-256:
`1b2b044e803aed5ba64124305796b6a4847f74c7ef617fcff99270912fd8851a`.
The 87,968-byte state artifact has SHA-256
`2d4a0feff7a47c584a9bede3f48a890c310785d81b1bfae35a8a4b2364609f45`.
