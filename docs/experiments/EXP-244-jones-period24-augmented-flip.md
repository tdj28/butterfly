# EXP-244 — Exact segmented period-24 flip

Status: completed — passed

EXP-243 supplies one unambiguous real-`-1` bracket on the primitive period-24
branch. EXP-244 initializes from the exact index-2 nodes and solves the
32-segment orbit plus anti-periodic tangent field as one augmented system,
holding `b=0.2` and `c=7.625815600403827` fixed and solving `a` inside the
frozen bracket.

The gates require small orbit, phase, tangent, and normalization residuals;
independent Radau closure and a real-`-1` multiplier; exact `28/32` section
identity; and nonclosure at every proper subperiod. A pass supplies the event
and tangent representation for a separately frozen period-48 switch.

Manifest:
[`../../experiments/manifests/EXP-244-jones-period24-augmented-flip.json`](../../experiments/manifests/EXP-244-jones-period24-augmented-flip.json).

## Result

All gates pass at `a=0.24070104611236293`. The 32-segment orbit and tangent
residuals are `4.83e-13` and `2.05e-12`; the direct multiplier is
`-1.0000000059`, and independent Radau gives `-0.9999983197`. The event
retains primitive `28/32` identity and minimum proper-subperiod closure
`0.0105200`.

This qualifies the period-24 real-`-1` event, not yet a period-48 child.
EXP-245 freezes a 64-segment child switch from the exact tangent mode.

Raw receipt: `artifacts/EXP-244/receipt.json`, 11,555 bytes, SHA-256
`9c3579c86500998daca262dda77b480beaaee913ab3089767bea3a20102defba`.
Compact receipt:
[`receipts/EXP-244.json`](receipts/EXP-244.json).
