# EXP-239 — Segmented period-24 continuation

Status: completed — passed

EXP-238 nominates primitive period-24 candidates on both signs, but they lie
only `3.22e-10` in `a` from the singular event. EXP-239 selects the negative
mode at frozen predictor length `0.002` and continues it for up to 20
pseudo-arclength steps of nominal length `0.02`, with adaptive halving only on
corrector failure.

The run must retain multiple-shooting matching and half-node separation at
every point, span at least `2e-6` in `a`, and finish with low full-period and
neutral residuals, period-24 half-period nonclosure, and exact `28/32` section
identity. A pass provides a well-separated endpoint for independent
two-solver, sign-equivalence, stability-exchange, and attraction tests.

Manifest:
[`../../experiments/manifests/EXP-239-jones-period24-segmented-continuation.json`](../../experiments/manifests/EXP-239-jones-period24-segmented-continuation.json).

## Result

All 20 nominal `0.02` steps pass without halving. The 21 retained points span
`8.14e-6` in `a`; half-node RMS grows monotonically from `0.000361` to
`0.057204`. The terminal orbit has half-period closure `0.11948`, retains
`28/32` section identity, and has multiple-shooting residual `7.79e-14`.

Its preliminary single-flow multiplier is approximately `-703.44`, suggesting
a strongly unstable child. That classification is not promoted until the
frozen EXP-240 block-Floquet DOP853/Radau audit passes.

Raw receipt: `artifacts/EXP-239/receipt.json`, 55,914 bytes, SHA-256
`e28fa5f0dc211c09803f2412737d384bc6823606d3b036731bfaf19696ac8a29`.
Compact receipt:
[`receipts/EXP-239.json`](receipts/EXP-239.json).
