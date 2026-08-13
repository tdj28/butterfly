# FND-095 — Five exact returning-arm events, without a scaling-limit claim

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, EXP-267 qualifies the fifth exact
primitive returning-arm real-`-1` event at
`a=0.24070100861338276`. Tighter DOP853 and segmented Radau independently pass
orbit, anti-periodic tangent, real-multiplier, cyclic-product,
proper-subperiod, and exact `224/256` section-identity gates.

The five event coordinates, for period-12, 24, 48, 96, and 192 parents, are:

`0.24070118147582764`, `0.24070104611236293`,
`0.24070101640878155`, `0.2407010100842176`, and
`0.24070100861338276`.

Their four gaps are `1.35363e-7`, `2.97036e-8`, `6.32456e-9`, and
`1.47083e-9`, giving three finite ratios `4.557`, `4.697`, and `4.300`.
The fifth event strongly extends the finite doubling cascade, but the newest
ratio breaks any apparent monotone convergence toward the classical
period-doubling constant. No accumulation limit or universality claim is
warranted from these three ratios.

The event does not establish a period-384 child. That switch and its
independent stability exchange are separately gated by EXP-268 and successors.
It also does not establish a full child sheet, paired shrimp boundaries, TBA
membership, double-criticality, or a global parameter-plane explanation.

Evidence:
[`../experiments/EXP-267-jones-period192-augmented-flip-refinement.md`](../experiments/EXP-267-jones-period192-augmented-flip-refinement.md).
