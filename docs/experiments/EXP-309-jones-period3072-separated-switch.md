# EXP-309 — More separated bilateral period-3072 switch

Status: frozen before execution

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
