# FND-094 — The exact returning-arm cascade reaches stable period 192

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, the exact returning-arm parent
events now occur at

`a12=0.24070118147582764`, `a24=0.24070104611236293`,
`a48=0.24070101640878155`, and `a96=0.2407010100842176`.

EXP-259 independently qualifies the period-96 real-`-1` event using a
128-segment DOP853 augmented orbit/tangent solve and segmented Radau parity.
Its DOP853/Radau event multipliers are
`-1.0000000394/-0.9999999149`, and its nearest proper-subperiod closure is
`1.68235e-4`.

Hash-bound 256-segment switching then produces primitive `224/256`
period-192 candidates on both tangent signs (EXP-260). Only `5.08e-10` below
the event, independent DOP853 and Radau corrections classify the period-96
parent as unstable (`1.13241659/1.13237635`) and the period-192 child as stable
(`0.46117807/0.46117779`). The two child half-period closures are about
`1.067e-4`. EXP-261 therefore qualifies a fourth local supercritical doubling
and extends the finite returning-arm cascade through stable period 192.

At the common coordinate `a=0.24070100959763152`, EXP-262 aligns both switch
signs at a half-period shift with DOP853/Radau whole-orbit RMS
`9.18e-10/5.62e-10`. Thus the bilateral candidates are one stable primitive
period-192 orbit, not two neighboring cycles.

The successive event spacings are about `1.35363e-7`, `2.97036e-8`, and
`6.32456e-9`, giving two finite ratios `4.557` and `4.697`. Their proximity to
the classical period-doubling constant is a promising observation, not an
accumulation-limit estimate or universality proof. Tangent-sign equivalence,
basin measure, the next event, a full child sheet, paired shrimp boundaries,
TBA membership, double-criticality, and a global parameter-plane explanation
remain separate.

EXP-267 subsequently qualifies the next period-192 event. Its added finite
spacing ratio is `4.300`, so the expanded sequence `4.557/4.697/4.300` does
not support a monotone limiting-scaling inference (FND-095). The already
qualified stable period-192 rung is unchanged.

Evidence:
[`../experiments/EXP-259-jones-period96-augmented-flip.md`](../experiments/EXP-259-jones-period96-augmented-flip.md),
[`../experiments/EXP-260-jones-period192-segmented-switch.md`](../experiments/EXP-260-jones-period192-segmented-switch.md), and
[`../experiments/EXP-261-jones-period192-near-event-qualification.md`](../experiments/EXP-261-jones-period192-near-event-qualification.md), and
[`../experiments/EXP-262-jones-period192-sign-equivalence.md`](../experiments/EXP-262-jones-period192-sign-equivalence.md).
