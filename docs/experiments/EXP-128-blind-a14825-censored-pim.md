# EXP-128 — Blind censor-aware PIM midpoint at `a=0.14825`

Status: passed

## Question

Which PIM-resolved saddle topology occupies the midpoint of the qualified
finite sampled bracket `[0.148,0.1485]`?

## Frozen design

EXP-128 changes only the target parameter and deterministic bootstrap seed from
the passing EXP-125/126 protocol. At `a=0.14825`, the same three fixed PIM
access lines are independently reconstructed at 128- and 256-return
right-censor ceilings. Each successful straddle advances 800 Poincare returns
and discards the first 100. Adaptive DOP853 retains `rtol=1e-10`,
`atol=1e-12`, and `max_step=0.05`.

No expected count or prior critical-point location is encoded. Each profile
must complete at least two access lines, supply at least 1000 pairs, and resolve
all 15 oracle variants to the same allowed count in both `y` and `z`. The two
profiles must agree. Within-profile and cross-horizon normalized critical spans
remain bounded by `0.03` and `0.04`; the stable period-4 reference and every
lifetime integration must pass.

If the blind common count is two, the finite bracket becomes
`[0.14825,0.1485]`. If it is three, the bracket becomes `[0.148,0.14825]`. Any
failure leaves `[0.148,0.1485]` unchanged. No result establishes a continuous
TBA curve or an infinite-lifetime saddle.

EXP-127's rejected faster-capture hypothesis does not enter the classifier.
It motivates using the PIM invariant-set construction rather than the
transient extra domain, but contributes no expected EXP-128 label or critical
location.

Immutable manifest:
`experiments/manifests/EXP-128-blind-a14825-censored-pim.json`.

## Result

EXP-128 passes from clean commit `61d9044` in `3492.09 s`. All six fixed PIM
access lines complete, three at each censor ceiling. Each profile contributes
2097 post-burn-in pairs per coordinate. Both `y` and `z` select three branches
at both 128 and 256 returns; all 15 oracle variants agree in each decision, for
60/60 three-branch cells and no two-branch or unresolved result.

The combined 128/256 normalized critical spans are `0.009043` in `y` and
`0.009093` in `z`. The period-4 reference and every lifetime integration pass.
Horizon 128 contains 31 censored evaluations and 29 certified selections;
horizon 256 contains none. The finite sampled classifier bracket therefore
narrows to `[0.148,0.14825]`.

Tracked compact receipt: `docs/experiments/receipts/EXP-128.json`. Raw receipt
SHA-256:
`a4aae2dc04b3d0171e9b74bd88cd3a9d79e73cd123715a8f81642d9a0664423e`.
