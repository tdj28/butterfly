# FND-096 — The exact returning-arm cascade reaches stable period 384

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, EXP-267 qualifies the exact
period-192 parent event at `a=0.24070100861338276`. Bilateral 512-segment
switching then produces primitive `448/512` period-384 candidates at three
predictor scales (EXP-268).

Only `1.13e-10` below the event, independent DOP853 and Radau corrections
classify the period-192 parent as unstable (`1.14929836/1.14909171`) and the
period-384 child as stable (`0.39117576/0.39117648`). The child remains
primitive under both solvers, with half-period closures near `5.64e-5` and
exact `448/512` section identity. EXP-269 therefore qualifies a fifth local
supercritical doubling and extends the finite returning-arm cascade through
stable period 384.

The five exact event coordinates yield finite spacing ratios
`4.557/4.697/4.300`. These are finite-cascade diagnostics, not evidence for a
resolved accumulation limit or universality. Tangent-sign equivalence, basin
measure, deeper continuation, a full child sheet, paired shrimp boundaries,
TBA membership, double-criticality, and a global parameter-plane explanation
remain separate.

Evidence:
[`../experiments/EXP-267-jones-period192-augmented-flip-refinement.md`](../experiments/EXP-267-jones-period192-augmented-flip-refinement.md),
[`../experiments/EXP-268-jones-period384-segmented-switch.md`](../experiments/EXP-268-jones-period384-segmented-switch.md), and
[`../experiments/EXP-269-jones-period384-near-event-qualification.md`](../experiments/EXP-269-jones-period384-near-event-qualification.md).
