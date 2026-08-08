# EXP-125 — Blind censor-aware PIM saddle at `a=0.148`

Status: preregistered; target not executed

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
