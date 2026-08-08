# EXP-125 — Blind censor-aware PIM saddle at `a=0.148`

Status: passed

## Question

Does an independent stable-set-targeting construction identify one
horizon-stable branch topology at the EXP-123/124 conditioning-sensitive
midpoint without relying on exponentially rare final sprinkler survivors?

## Frozen design

EXP-125 applies the censor-aware Nusse--Yorke PIM method qualified on both
published controls by EXP-115/116. Three fixed access lines at `z=0.0090`,
`0.0096`, and `0.0102` are independently refined at 128- and 256-return
right-censor ceilings. Each successful straddle advances 800 Poincare returns;
the first 100 are discarded. Adaptive DOP853 uses `rtol=1e-10`, `atol=1e-12`,
and `max_step=0.05`.

No expected branch count and no sprinkler critical-point reference is encoded.
For each censor horizon, at least two access lines and 1000 return pairs must
survive. All 15 frozen oracle variants must resolve in both `y` and `z`, the
coordinates must choose the same count from `{2,3}`, and both horizons must
choose that same count. Within-profile normalized critical span must not exceed
`0.03`; combined 128/256 span must not exceed `0.04`; the period-4 reference
and every adaptive integration must pass.

A pass assigns the common PIM branch count at this finite 128/256 censor pair.
A two result would move the sampled classifier bracket to `[0.148,0.149]`; a
three result would move it to `[0.147,0.148]`. A failure leaves `a=0.148`
unlabeled and keeps `[0.147,0.149]`.

Immutable manifest:
`experiments/manifests/EXP-125-blind-a148-censored-pim.json`.

## Execution host

The frozen implementation uses adaptive SciPy DOP853 lifetime integrations in
eight CPU worker processes. The qualified Runpod/Triton GPU kernel is a
different fixed-step sprinkler method and cannot be substituted without a new
PIM parity experiment. EXP-125 therefore runs on the local reference host; a
GPU port is a separate optimization, not a result-dependent method change.

## Result

EXP-125 passes from clean commit `982a729` in `4091.72 s`. All six fixed PIM
access lines complete: three at the 128-return censor ceiling and three at 256.
Each profile contributes 2097 post-burn-in return pairs. Both `y` and `z`
select two branches at both horizons; all 15 oracle variants in each of the
four decisions agree, for 60/60 two-branch cells and no contrary or unresolved
cell.

The normalized within- and cross-horizon critical spans are `0.008504` in `y`
and `0.004735` in `z`, far below the frozen `0.03`/`0.04` gates. The period-4
reference passes. The 128 profile has two certified right-censored lifetime
evaluations and the 256 profile has none; all six straddles have zero failed
lifetime evaluations.

The independently targeted finite-horizon PIM saddle at `a=0.148` is therefore
qualified as two-branch. The sampled classifier bracket moves from
`[0.147,0.149]` to `[0.148,0.149]`. This is not yet a continued TBA curve or an
infinite-lifetime proof.

Tracked compact receipt: `docs/experiments/receipts/EXP-125.json`. Raw receipt
SHA-256:
`d76f6b84943ba527a83850d396144525c3c9c9726e92065c441870085cffc623`.
The 88,372-byte PIM state artifact has SHA-256
`74300f95d4af34a810dbd58972e45df9add4cbfa96d1810f88c9f150bd16b045`.
