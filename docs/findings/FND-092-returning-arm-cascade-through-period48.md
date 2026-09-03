# FND-092 — The exact returning-arm cascade reaches stable period 48

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, the primitive period-24 branch born
at the EXP-237 period-12 flip undergoes its own exact real-`-1` event at
`a=0.24070104611236293` (EXP-244). DOP853 and Radau agree on the event,
anti-periodic tangent field, primitive `28/32` identity, and all proper-
subperiod nonclosure gates.

Exact 64-segment switching then produces primitive `56/64` period-48
candidates on both signs (EXP-245). At a near-event offset of `-2.04e-10`,
independent DOP853 and Radau classify the period-24 parent as unstable and the
period-48 child as stable (EXP-246), qualifying a second local supercritical
doubling.

The two newly qualified event coordinates differ by `1.35363e-7` in `a`.
This is strong finite evidence for a rapidly accumulating local cascade on the
corrected Jones returning arm, not a universality limit, full child sheet,
paired shrimp-boundary assignment, TBA membership, double-criticality, or a
global parameter-plane explanation.

Evidence:
[`../experiments/EXP-246-jones-period48-near-event-qualification.md`](../experiments/EXP-246-jones-period48-near-event-qualification.md).
