# EXP-275 — Near-event period-768 qualification

Status: completed — passed

EXP-274 nominates bilateral primitive period-768 children. EXP-275 selects the
negative-sign step-`0.0005` child only `3.85e-11` below the exact EXP-273
event, then independently corrects the period-384 parent and period-768 child
at that same `a` with DOP853 and Radau.

A pass requires both solvers to classify the parent unstable and child stable,
agree on both whole orbits and multiplier moduli, retain nonzero half-period
closure, and recover exact `896/1024` section identity. This is the decisive
local supercriticality gate, not a basin-measure or universality test.

Manifest:
[`../../experiments/manifests/EXP-275-jones-period768-near-event-qualification.json`](../../experiments/manifests/EXP-275-jones-period768-near-event-qualification.json).

## Result

Every frozen gate passes at `a=0.24070100827074953`, only `3.85e-11` below
the exact event. DOP853/Radau classify the period-384 parent as unstable
(`1.22260901/1.22168588`) and the primitive period-768 child as stable
(`0.08362765/0.08362578`). The child-modulus relative spread is `2.24e-5`;
parent and child whole-orbit RMS are `8.90e-9/0`.

Both solvers retain child half-period closures above `6.10e-6` and exact
`896/1024` identity. This qualifies the sixth local supercritical doubling
and extends the finite cascade through stable period 768 (FND-098). EXP-276
separately freezes tangent-sign equivalence before deeper continuation.

Raw receipt: `artifacts/EXP-275/receipt.json`, 200,151 bytes, SHA-256
`98a47619175a39aa776f3a4c82234d94019ca3d9e766ff525613378035544e61`.
Compact receipt:
[`receipts/EXP-275.json`](receipts/EXP-275.json).
