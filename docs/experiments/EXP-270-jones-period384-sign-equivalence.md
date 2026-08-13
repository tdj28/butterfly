# EXP-270 — Period-384 tangent-sign equivalence

Status: completed — passed

EXP-268 produces period-384 candidates from both signs of the exact
anti-periodic period-192 tangent. EXP-270 corrects both signs at their frozen
mean coordinate `a=0.24070100850360543` under DOP853 and Radau, then compares
the complete 512-segment orbits with bounded continuous phase minimization and
8,192 phase samples.

Matching, phase, endpoint, period, multiplier, stability, half-period
primitivity, within-solver sign identity, and cross-solver identity gates are
fixed before execution. A pass establishes that both switch signs represent
one stable primitive period-384 orbit up to phase. It does not establish basin
measure, deeper continuation, another event, a limiting scaling law, or any
global shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-270-jones-period384-sign-equivalence.json`](../../experiments/manifests/EXP-270-jones-period384-sign-equivalence.json).

## Result

All four common-parameter corrections pass. DOP853/Radau place the two signs
at phase shifts `0.4999999983626/0.4999999983638` with whole-orbit RMS
`2.15e-10/3.28e-9`. Cross-solver whole-orbit RMS is at most `4.33e-8`,
segment endpoint error is at most `2.79e-12`, and all stable moduli lie in
`[0.411880,0.412898]`.

The switch signs therefore represent one stable primitive period-384 orbit up
to phase. EXP-271 freezes an eight-step exact continuation of that unified
branch toward a separately gated sixth-flip scan.

Raw receipt: `artifacts/EXP-270/receipt.json`, 138,617 bytes, SHA-256
`f84677cc588f970a3a7a94bedc742a0a6b19850bf13f3353d61762a8b3512f8d`.
Compact receipt:
[`receipts/EXP-270.json`](receipts/EXP-270.json).
