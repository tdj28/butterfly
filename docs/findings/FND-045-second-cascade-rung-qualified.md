# FND-045 — The second fixed-path cascade rung is qualified

Status: passed EXP-160 through EXP-163

## Finding

Identity-safe pseudo-arclength continuation carries the primitive period-2
child to an exact second flip at
`(a,b,c)=(0.1798,0.2,4.3100451384813105)`. The event period is
`11.724290361610073`. The reference Floquet residual from `-1` is `3.94e-14`;
independent Radau gives `5.91e-13`, while preserving two windings and strong
half-period nonclosure.

A doubled-cover nullspace switch opens two local arms. At `c=4.318`, the two
arms are one primitive period-4 orbit up to phase, with whole-orbit RMS
`3.14e-7` and near-half-cycle shift `0.50140`. Independent Radau gives the
unstable period-2 parent multiplier `-1.0115948996` and stable period-4 child
multiplier `0.9535193007`. The child-to-parent period ratio is `2.000002`, its
winding is four, and perturbed integration recovers it to phase-invariant RMS
`2.83e-9`.

## Implication for Jones

The fixed Jones-like path now has two complete, independently qualified
supercritical period-doubling rungs: period 1 to 2 and period 2 to 4. This is
substantially stronger than reading a period sequence from the parameter
raster and shows that the original local cascade methodology is extensible.

It does not yet establish the claimed finite symbolic ordering through period
seven, the exact historical `L1`/`L2` parameterizations, logistic conjugacy, or
the equilibrium homoclinic endpoint. The next gate is identity-safe
continuation of this period-4 child to its first flip, followed by a period-8
switch and independent qualification.

Tracked receipts: `docs/experiments/receipts/EXP-160.json` through
`docs/experiments/receipts/EXP-163.json`.
