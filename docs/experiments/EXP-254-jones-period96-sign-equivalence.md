# EXP-254 — Period-96 tangent-sign equivalence

Status: completed — failed sign-identity resolution gate

EXP-252 produces period-96 candidates on both signs of the exact
anti-periodic tangent. EXP-254 corrects both signs to their frozen mean
coordinate `a=0.24070101600213994` under DOP853 and Radau, then compares the
full continuous segmented orbits after independently refined phase alignment.

Matching, phase, segment endpoint, period, multiplier, stability, and
half-period primitivity gates are explicit. A pass establishes that both signs
are one stable primitive period-96 orbit up to phase, not two nearby cycles.
It does not establish basin measure, the next flip, a limiting scaling law, or
any global shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-254-jones-period96-sign-equivalence.json`](../../experiments/manifests/EXP-254-jones-period96-sign-equivalence.json).

## Result

All four common-parameter corrections pass matching, phase, endpoint, period,
multiplier, stability, primitivity, and cross-solver identity gates. The only
failure is tangent-sign identity: both solvers place the optimum at a
half-period shift, but the four-stage grid stops at spacing `7.45e-9` and RMS
`1.07e-5`, above the frozen `1e-6` gate. EXP-255 preserves that failure and
freezes bounded continuous scalar minimization on the same immutable corrected
orbits without changing the threshold.

Raw receipt: `artifacts/EXP-254/receipt.json`, 45,066 bytes, SHA-256
`2d7d709643aa720c2910c9ac523c730b790aab2edb62f95e0bd82a1d8458ed07`.
Compact receipt:
[`receipts/EXP-254.json`](receipts/EXP-254.json).
