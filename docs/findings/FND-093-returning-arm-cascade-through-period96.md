# FND-093 — The exact returning-arm cascade reaches stable period 96

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, the primitive period-48 branch has
an exact real-`-1` event at `a=0.24070101640878155`. The original EXP-250
optimizer stopped at its evaluation ceiling despite satisfying all DOP853
science residuals; EXP-251 independently evaluates the identical segmented
orbit and anti-periodic tangent equations under Radau and qualifies the event
without changing any threshold.

Hash-bound 128-segment switching produces primitive `112/128` period-96
candidates on both tangent signs (EXP-252). At a near-event offset of
`-4.04e-10`, independent DOP853 and Radau classify the period-48 parent as
unstable and the period-96 child as stable (EXP-253), qualifying a third local
supercritical doubling on the corrected Jones returning arm.

At a common parameter, EXP-256 independently aligns the two switch signs at a
half-period phase shift with DOP853/Radau whole-orbit RMS
`3.45e-10/4.57e-9`. Thus the bilateral switch candidates are one stable
primitive period-96 orbit, not two nearby cycles.

The three exact event coordinates are
`0.24070118147582764`, `0.24070104611236293`, and
`0.24070101640878155`. Their first two spacings have ratio about `4.557`.
That is finite cascade evidence, not a Feigenbaum-limit or universality proof,
full child sheet, paired shrimp-boundary assignment, TBA membership,
double-criticality, or a global parameter-plane explanation.

Evidence:
[`../experiments/EXP-253-jones-period96-near-event-qualification.md`](../experiments/EXP-253-jones-period96-near-event-qualification.md) and
[`../experiments/EXP-256-jones-period96-sign-phase-resolution-audit.md`](../experiments/EXP-256-jones-period96-sign-phase-resolution-audit.md).
