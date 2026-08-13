# FND-098 — The exact returning-arm cascade reaches stable period 768

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, EXP-273 qualifies the exact
period-384 parent event at `a=0.24070100830924687`. Bilateral 1,024-segment
switching then produces primitive `896/1024` period-768 candidates at three
predictor scales (EXP-274).

Only `3.85e-11` below the event, independent DOP853 and Radau corrections
classify the period-384 parent as unstable (`1.22260901/1.22168588`) and the
period-768 child as stable (`0.08362765/0.08362578`). The child remains
primitive under both solvers, with half-period closures above `6.10e-6` and
exact `896/1024` section identity. EXP-275 therefore qualifies a sixth local
supercritical doubling and extends the finite returning-arm cascade through
stable period 768.

The six exact event coordinates yield finite spacing ratios
`4.557/4.697/4.300/4.836`. These are strong finite-cascade diagnostics, but
their non-monotonicity does not resolve an accumulation limit or establish
universality. Tangent-sign equivalence, basin measure, deeper continuation, a
full child sheet, paired shrimp boundaries, TBA membership, double-criticality,
and a global parameter-plane explanation remain separate.

Evidence:
[`../experiments/EXP-273-jones-period384-augmented-flip.md`](../experiments/EXP-273-jones-period384-augmented-flip.md),
[`../experiments/EXP-274-jones-period768-segmented-switch.md`](../experiments/EXP-274-jones-period768-segmented-switch.md), and
[`../experiments/EXP-275-jones-period768-near-event-qualification.md`](../experiments/EXP-275-jones-period768-near-event-qualification.md).
