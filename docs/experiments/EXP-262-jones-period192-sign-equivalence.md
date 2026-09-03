# EXP-262 — Period-192 tangent-sign equivalence

Status: completed — passed

EXP-260 produces period-192 candidates from both signs of the exact
anti-periodic period-96 tangent. EXP-262 corrects both signs at their frozen
mean coordinate `a=0.24070100959763152` under DOP853 and Radau, then compares
the complete segmented orbits with bounded continuous phase minimization.

The phase method is declared prospectively because EXP-254/256 already showed
that a refined grid can resolve the correct half-period basin but stop above
the orbit-identity threshold. Matching, phase, endpoint, period, multiplier,
stability, half-period primitivity, within-solver sign identity, and
cross-solver identity gates are fixed before execution.

A pass will establish that both switch signs represent one stable primitive
period-192 orbit up to phase. It will not establish basin measure, deeper
continuation, another event, a limiting scaling law, or any global
shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-262-jones-period192-sign-equivalence.json`](../../experiments/manifests/EXP-262-jones-period192-sign-equivalence.json).

## Result

All four common-parameter corrections pass. DOP853/Radau place the two signs
at phase shifts `0.4999999938670/0.4999999938681` with whole-orbit RMS
`9.18e-10/5.62e-10`. Cross-solver whole-orbit RMS is at most `2.72e-8`,
segment endpoint error is at most `2.74e-12`, and all stable moduli lie in
`[0.4909661,0.4911399]`.

The switch signs therefore represent one stable primitive period-192 orbit up
to phase. EXP-263 freezes an eight-step exact continuation of that unified
branch toward a separately gated fifth-flip scan.

Raw receipt: `artifacts/EXP-262/receipt.json`, 75,782 bytes, SHA-256
`088a2a15da962971b3a52ee654cab8bc24f866b963c47f59ae90d3740768c1d3`.
Compact receipt:
[`receipts/EXP-262.json`](receipts/EXP-262.json).
