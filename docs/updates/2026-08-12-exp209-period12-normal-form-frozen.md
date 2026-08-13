# EXP-209 freezes normal-form and attraction tests at three period-12 children

EXP-208 upgrades three isolated switch leads to independently qualified
primitive stable period-12 children. EXP-209 now freezes the stronger local
claim before tracing any intermediate child point.

Each event-to-child interval receives the same seven dimensionless offsets.
The gates jointly require square-root whole-orbit opening, the flip-normal-form
multiplier ratio near four, stability exchange, period and two-section
identity, proper-subperiod rejection, DOP853/Radau agreement at three scales,
and return from two opposite perturbations. This design can support a sampled
local supercritical interpretation while remaining explicitly short of a
continuous child surface or TBA identification.

The clean execution passes. Across the three slices, opening exponents are
`0.50258--0.50350` with `R^2 > 0.999995`; all 21 multiplier ratios lie in
`4.0107--4.1503`, with medians `4.0342--4.0474`. Every parent remains unstable,
every child stable and primitive, all section counts remain exact, and nine
Radau checkpoints agree with DOP853.

Both opposite perturbations at every full-offset child return within
`6.57e-11` of the orbit. This supplies replicated sampled local supercritical
signatures and perturbed attraction along the period-6 flip curve. A continuous
two-parameter period-12 surface and its relation to the TBA remain open.

Receipt: [`../experiments/receipts/EXP-209.json`](../experiments/receipts/EXP-209.json).
