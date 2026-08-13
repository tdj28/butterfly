# EXP-251 — Residual-safe segmented audit of the period-48 flip

Status: completed — passed all gates

EXP-250 reaches all frozen DOP853 event residuals but exhausts its optimizer
ceiling, while a full-period Radau replay accumulates enough drift to miss the
multiplier gate. EXP-251 accepts the source status only if those already
frozen residuals pass, then evaluates the identical 64-segment orbit and
anti-periodic tangent equations under Radau and computes independent
block-Floquet products at four cyclic shifts.

The independent orbit, phase, tangent, normalization, real-`-1`, cyclic, exact
`56/64` identity, and proper-subperiod gates remain explicit. A pass qualifies
the event representation; a failure triggers a new collocation solve.

Manifest:
[`../../experiments/manifests/EXP-251-period48-flip-residual-safe-audit.json`](../../experiments/manifests/EXP-251-period48-flip-residual-safe-audit.json).

## Result

The source DOP853 residuals pass unchanged, and the independent segmented
Radau evaluation agrees: orbit and tangent residuals are `2.16e-10` and
`1.21e-10`; the four cyclic flip multipliers have median
`-1.000000032852` and spread `2.37e-12`. The primitive-subperiod and exact
`56/64` section identities also pass. This qualifies the period-48 flip event
and its anti-periodic tangent representation for the separately frozen
EXP-252 period-96 switch; it is not itself evidence for a period-96 child.

Raw receipt: `artifacts/EXP-251/receipt.json`, 5,512 bytes, SHA-256
`db095fb0f303aee1d39418024517958b8b514e949ba6b82233eed49241cac2f5`.
Compact receipt:
[`receipts/EXP-251.json`](receipts/EXP-251.json).
