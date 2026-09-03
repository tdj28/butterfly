# EXP-276 — Period-768 tangent-sign equivalence

Status: completed — failed one multiplier-agreement gate

EXP-274 produces period-768 candidates from both signs of the exact
anti-periodic period-384 tangent. EXP-276 corrects both signs at their frozen
mean coordinate `a=0.24070100827079027` under DOP853 and Radau, then compares
the complete 1,024-segment orbits with bounded continuous phase minimization
and 16,384 phase samples.

Matching, phase, endpoint, period, multiplier, stability, half-period
primitivity, within-solver sign identity, and cross-solver identity gates are
fixed before execution. A pass establishes that both switch signs represent
one stable primitive period-768 orbit up to phase. It does not establish basin
measure, deeper continuation, another event, a limiting scaling law, or any
global shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-276-jones-period768-sign-equivalence.json`](../../experiments/manifests/EXP-276-jones-period768-sign-equivalence.json).

## Result

Nine of ten gates pass. DOP853/Radau align the two signs at phase shifts
`0.4999999999093/0.4999999999094`, with whole-orbit RMS
`1.39e-8/2.72e-8`. Cross-solver RMS is at most `4.11e-8`, segment endpoint
error is at most `7.89e-12`, and all four corrected orbits are stable and
primitive.

The sole failure is modulus spread: `0.0034504` exceeds the frozen `0.002`
gate. The positive-sign DOP853/Radau moduli agree closely
(`0.08606828/0.08606644`), while the negative-sign values differ
(`0.08480440/0.08825478`). Therefore the orbit identity is strongly supported
but not yet promoted under the complete frozen contract. EXP-277 repeats the
same test with tighter integration and no relaxed gate.

Raw receipt: `artifacts/EXP-276/receipt.json`, 264,226 bytes, SHA-256
`73314439c762866e73eff3864a2a90db8ed6ec746860156a9f2df0971a6c9412`.
Compact receipt:
[`receipts/EXP-276.json`](receipts/EXP-276.json).
