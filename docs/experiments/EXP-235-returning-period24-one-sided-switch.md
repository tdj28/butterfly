# EXP-235 — One-sided-tangent multiscale period-24 switch

Status: complete — failed with zero generated candidates

EXP-234 shows that the symmetric primary-family stencil fails only at its
positive `a` offset, with raw closure `0.00801`; the center and negative offset
pass near `1e-11`. EXP-235 changes only the primary tangent stencil to
`[-2e-5,-1e-5,0]`.

The exact EXP-232 event, six switch scales, both nullspace signs, solver,
residual-safe handling, and all primitive period-24 nomination gates are
unchanged. A pass remains only a candidate nomination pending independent
DOP853/Radau qualification.

Manifest:
[`../../experiments/manifests/EXP-235-returning-period24-one-sided-switch.json`](../../experiments/manifests/EXP-235-returning-period24-one-sided-switch.json).

## Result

The one-sided primary stencil passes at all three offsets, and the switch
geometry is well resolved: the small singular value is `7.64e-7` and the
primary/secondary tangent dot product is `2.39e-15`. Nevertheless, none of the
12 one-step correctors across six scales and both signs produces a candidate.
Residual norms range from `1.19e-5` to `7.71`; the closest trial is the positive
direction at step `0.00025`, which exhausts 160 evaluations at `1.19e-5`.

This rejects the frozen full-period one-step switch configuration, not the
existence of a period-24 child. EXP-236 freezes a targeted recovery of that
closest trial with the same predictor and gates but 480 corrector evaluations.
Persistent failure will trigger a segmented multiple-shooting switch.

Raw receipt: `artifacts/EXP-235/receipt.json`, 12,865 bytes, SHA-256
`67eb323fab5db4622344df874deb73eb3a5c7cc78b26851fb74519f6011e5911`.
Compact receipt:
[`receipts/EXP-235.json`](receipts/EXP-235.json).
