# FND-074 — The lower-c period-6 strip has a real flip boundary

Status: qualified on seven prospectively frozen slices

EXP-203 exposed a narrow corrected stable period-6 strip whose dominant real
Floquet multiplier approached `-1`. EXP-205 selected seven adjacent sign
brackets before refinement, spanning `c in [7.192,7.288]`, and independently
bisected each in `a` with fresh DOP853 orbit correction and monodromy
integration.

All seven pass. Their `a` locations decrease smoothly from
`0.2157982842636108` at `c=7.192` to `0.2157187472915650` at `c=7.288`.
Every final bracket is `7.63e-11` wide; the maximum absolute multiplier
residual is `2.02e-7`, the multiplier is real to reported precision, flow
closure is at most `2.83e-13`, and the neutral multiplier error is at most
`1.20e-9`. Every orbit retains exactly six historical-section and eight
Barrio-section phases.

The sampled high-`a` edge is therefore a genuine period-doubling boundary of
the corrected period-6 family, not a raster boundary or arbitrary
`|lambda|<1` cutoff. This is constructive support for Jones's broader
period-doubling organization. It does not identify the topology-changing
curve, prove curve continuity between or beyond the seven slices, establish a
period-12 child or supercriticality, or solve either critical-membership
residual.

Evidence: [`../experiments/EXP-205-lower-c-period6-flip-refinement.md`](../experiments/EXP-205-lower-c-period6-flip-refinement.md).
