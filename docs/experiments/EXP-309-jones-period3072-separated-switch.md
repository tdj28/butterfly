# EXP-309 — More separated bilateral period-3072 switch

Status: completed — passed both signs

EXP-308 corrects both signs and passes every common gate, but the positive
sign's direct half-period nonclosure is `4.41e-8`, just below the untouched
`5e-8` floor. EXP-309 preserves that failure and applies the deterministic
factor-two separation rule to the predictor length: `0.00025 -> 0.0005`.

Both signs and every correction, residual, primitivity, displacement,
period-ratio, exact `3584/4096` identity, and minimum-candidate gate remain
unchanged. Preliminary multipliers do not select a sign. A pass nominates
period-3072 candidates only; independent sign equivalence and stability
exchange remain separate.

Manifest:
[`../../experiments/manifests/EXP-309-jones-period3072-separated-switch.json`](../../experiments/manifests/EXP-309-jones-period3072-separated-switch.json).

## Result

Both signs correct in two sparse evaluations at
`a=0.24070100822429846`. Matching residuals stay below `8.92e-11`, parameter
displacement is `1.05e-12`, period ratios differ from two by only `1.11e-12`,
and exact `3584/4096` section identities pass.

Half-node RMS is `9.02e-6` for both candidates. Direct half-period nonclosure
is `2.25e-6` for the negative sign and `3.52e-7` for the positive sign, both
well above the unchanged `5e-8` floor. EXP-309 therefore nominates primitive
period-3072 candidates. Preliminary multipliers are discarded.

The negative sign is prospectively selected for independent DOP853/Radau
qualification solely because it has the larger half-period nonclosure. Child
stability, sign equivalence, and eighth-birth criticality remain open.

Raw receipt: `artifacts/EXP-309/receipt.json`, 1,010,666 bytes, SHA-256
`f4991cc53e1fe68eea5a0a60e3f52ec2f731b43371d943db49ae1e3a19c0510a`.
Compact receipt:
[`receipts/EXP-309.json`](receipts/EXP-309.json).
