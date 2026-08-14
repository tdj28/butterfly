# EXP-290 — Period-1536 continuation away from the seventh event

Status: completed — passed

EXP-289 independently classifies the period-1536 child as unstable but leaves
the period-768 parent inside the unchanged neutral margin only `7.08e-14` in
`a` from the event. EXP-290 continues the same selected child for eight frozen
sparse pseudo-arclength steps of `0.0003125`, with halving allowed only down to
`0.000009765625` on correction failure.

Nine exact rows, at least `1e-12` total `a` separation from the event, matching
below `1e-8`, persistent half-node separation, terminal full/half closure,
neutral mode, period ratio two, and exact `1792/2048` section identity are all
mandatory. A pass supplies a farther child for a new independently frozen
criticality audit. It does not itself classify stability or criticality.

Manifest:
[`../../experiments/manifests/EXP-290-jones-period1536-segmented-continuation.json`](../../experiments/manifests/EXP-290-jones-period1536-segmented-continuation.json).

## Result

All eight full sparse steps pass without halving in 670 seconds. The exact
period-1536 branch reaches `a=0.2407010081704185`, `3.014e-12` below the event,
while half-node RMS grows monotonically from `6.31e-6` to `6.95e-5`.
Terminal half-period closure is `9.07e-5`; full closure and neutral error are
`4.04e-5/1.08e-3`, and exact `1792/2048` identity remains intact.

The first continued row crosses from the source candidate's tiny positive
`a` offset to a negative offset while the child amplitude grows. Because these
parameter changes are below the conditioning scale of the Float64 correction,
this geometry is not promoted as a child-branch fold. A real `+1` multiplier
crossing or a higher-precision branch audit would be required.

The terminal direct multiplier is `-3.0274`, but it is only a preliminary
long-product diagnostic. EXP-291 instead returns to the original same-coordinate
question and resolves the EXP-289 parent side with two independent 50-digit
tableaux; this is the shortest path to deciding whether the unstable child is
born subcritically.

Raw receipt: `artifacts/EXP-290/receipt.json`, 1,138,117 bytes, SHA-256
`3ecfae732464bd8816ae434a2902cdd7f90265dbdc83e1479f5891b3c14ed1bc`.
Compact receipt:
[`receipts/EXP-290.json`](receipts/EXP-290.json).
