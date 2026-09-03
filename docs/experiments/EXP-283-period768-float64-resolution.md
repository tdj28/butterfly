# EXP-283 — Float64 resolution diagnostic for the period-768 event

Status: completed — passed

EXP-282 leaves a `3.67e-7` tight DOP853/Radau multiplier disagreement on the
same immutable event representation. Before repeating a costly coupled solve,
EXP-283 binds that receipt to the original EXP-280 bracket and compares two
scales with the unchanged `1e-7` event tolerance:

- half the cross-solver multiplier disagreement, the best common-centering
  residual if that local gap persists; and
- the bracket-secant multiplier change corresponding to one representable
  Float64 increment at the corrected `a`.

This is a deterministic conditioning diagnostic, not a seventh-event solve.
A pass motivates a separately frozen higher-precision or better-conditioned
formulation; it does not prove that every possible Float64 formulation fails.

Manifest:
[`../../experiments/manifests/EXP-283-period768-float64-resolution.json`](../../experiments/manifests/EXP-283-period768-float64-resolution.json).

## Result

All six diagnostic gates pass. At `a=0.2407010081734325`, adjacent Float64
values are separated by `2.7756e-17`. The EXP-280 bracket spans 4,387,556 such
increments, and its endpoint secant gives an estimated multiplier change of
`1.024e-6` per increment—more than ten times the `1e-7` event gate.

The tight DOP853/Radau multiplier difference is `3.673e-7`; half that gap is
`1.836e-7`, already above the gate. This diagnoses an inadequately resolved
Float64 formulation for another identical recorrection. It does not prove
that every possible Float64 formulation fails and does not qualify the
seventh event. FND-099 records the numerical-method frontier, and EXP-284
freezes a 50-decimal-digit segmented integration pilot.

Raw receipt: `artifacts/EXP-283/receipt.json`, 2,085 bytes, SHA-256
`8c95e4f58cd77dd58b9272a1bbe7559e8287957c439a9e53462e8f60c3095a4d`.
Compact receipt:
[`receipts/EXP-283.json`](receipts/EXP-283.json).
