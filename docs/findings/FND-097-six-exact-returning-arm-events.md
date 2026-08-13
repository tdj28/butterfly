# FND-097 — Six exact returning-arm events, without a scaling-limit claim

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, EXP-273 qualifies the sixth exact
primitive returning-arm real-`-1` event at
`a=0.24070100830924687`. Tight-step DOP853 and segmented Radau independently
pass orbit, anti-periodic tangent, real-multiplier, cyclic-product,
proper-subperiod, and exact `448/512` section-identity gates.

The six event coordinates, for period-12, 24, 48, 96, 192, and 384 parents,
are:

`0.24070118147582764`, `0.24070104611236293`,
`0.24070101640878155`, `0.24070101008421760`,
`0.24070100861338276`, and `0.24070100830924687`.

Their five gaps are `1.35363e-7`, `2.97036e-8`, `6.32456e-9`,
`1.47083e-9`, and `3.04136e-10`, giving four finite ratios `4.557`, `4.697`,
`4.300`, and `4.836`. The sixth event strongly extends the finite doubling
cascade, but the ratios remain non-monotone. No accumulation limit or
universality claim is warranted from four finite ratios.

The event does not establish a period-768 child. That switch and its
independent stability exchange are separately gated by EXP-274 and
successors. It also does not establish a full child sheet, paired shrimp
boundaries, TBA membership, double-criticality, or a global parameter-plane
explanation.

Evidence:
[`../experiments/EXP-273-jones-period384-augmented-flip.md`](../experiments/EXP-273-jones-period384-augmented-flip.md).
