# EXP-321 — Continue the immediate seventh daughter toward the stable target scale

Status: passed — six-row exact stable segment, no fold

EXP-318--320 distinguish two facts near the seventh event: the immediate
period-1536 daughter is stable and opens toward lower `a`, while EXP-299 also
contains a stable primitive period-1536 orbit slightly above the extrapolated
event. Their global relationship is unknown.

EXP-321 starts from EXP-319's negative-sign children at predictor lengths
`3.125e-5` and `6.25e-5`, forms a normalized secant in all 6,146 orbit,
period, and parameter variables, and takes six exact pseudo-arclength steps of
`3.125e-5`. The 50-digit 4,096-step RK4 3/8 map and five-variable cyclic
Newton elimination are unchanged. Each row records parameter, half-node
amplitude, Floquet stability, any parameter-direction reversal, and the best
cyclic node RMS to EXP-299's stable target.

All rows must close below `1e-20`, grow monotonically in primitive amplitude to
at least `5e-6`, and pass period, cyclic, and neutral gates. The experiment is
outcome-neutral: a fold, stability change, target match, or their absence can
all pass. Any nominated fold or stability bracket requires separate
refinement.

Manifest:
[`../../experiments/manifests/EXP-321-jones-period1536-decimal-sheet-continuation.json`](../../experiments/manifests/EXP-321-jones-period1536-decimal-sheet-continuation.json).

## Result

All six rows pass after 1,099.58 seconds. Matching residuals are at most
`9.16e-22`; primitive half-node RMS grows monotonically from the
`1.57794e-6` source to `6.27302e-6`. The parameter decreases monotonically
from `0.2407010082211119` to `0.24070100821336454`, with increasingly negative
increments, so this bounded segment contains no fold.

Every row is stable. The dominant transverse modulus falls from `0.83912` to
`0.09920` through row five and is `0.18854` at row six after the leading real
multiplier crosses through zero. The phase-invariant RMS to EXP-299's Float64
candidate decreases from `2.0747e-6` to `9.5713e-7`, but does not establish
identity.

The result does not yet justify calling EXP-299 a separate exact sheet.
EXP-299's child had matching residual `2.53e-11` and direct closure
`2.86e-7`, whereas EXP-321 is exact to the new map's `1e-20` gate. EXP-322
therefore freezes a fixed-`a`, 50-digit correction of the EXP-299 candidate to
distinguish a genuine primitive orbit from collapse to the doubled parent or
an unresolved seed.

Raw receipt: `artifacts/EXP-321/receipt.json`, 2,088,241 bytes, SHA-256
`09dc671c78489d38d90d08c1c89458a247fbe51a04582bf3775e2ed6a7e6989a`.
Compact receipt: [`receipts/EXP-321.json`](receipts/EXP-321.json).
