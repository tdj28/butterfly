# EXP-245 — Segmented period-48 child switch

Status: completed — passed candidate nomination

EXP-244 supplies the exact 32-segment period-24 event and anti-periodic tangent
mode. EXP-245 doubles it to 64 segments and attempts three frozen predictor
lengths on both signs at fixed `(b,c)`, with `a` free to open along the child.

Candidates must pass matching, phase, direct closure, neutral, period-ratio,
parameter-displacement, half-period nonclosure, half-node separation, and
exact `56/64` section-identity gates. Any survivor is a nomination requiring a
separately frozen independent-solver and stability-exchange qualification.

Manifest:
[`../../experiments/manifests/EXP-245-jones-period48-segmented-switch.json`](../../experiments/manifests/EXP-245-jones-period48-segmented-switch.json).

## Result

All six corrections retain low segmented residuals. Both signs at predictor
length `0.002` pass every candidate gate. Their parameter offsets are
`-2.04e-10/-2.07e-10`, half-period closures are
`0.00049213/0.00049646`, and both retain primitive `56/64` section identity.
Their preliminary dominant moduli are `0.987258/0.987031`.

EXP-246 freezes independent 32/64-segment DOP853/Radau correction of the
period-24 parent and one nominated child at the same near-event coordinate.

Raw receipt: `artifacts/EXP-245/receipt.json`, 40,488 bytes, SHA-256
`a94cc3efe278fdc6ddae53ac4610d46564beab1c7424e29253ae746606038527`.
Compact receipt:
[`receipts/EXP-245.json`](receipts/EXP-245.json).
