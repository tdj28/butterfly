# FND-103 — Independent augmented solves qualify the eighth event

Status: qualified numerical event; period-3072 birth remains open

At fixed `(b,c)=(0.2,7.625815600403827)`, the primitive period-1536 branch has
an eighth numerical real-`-1` event near `a=0.24070100822410`. This claim is
based on direct augmented orbit-plus-antiperiodic-tangent roots, not on
EXP-302's subsequently rejected Float64 micro-bracket.

Classical RK4 augmented solves at 1,024, 2,048, and 4,096 steps per each of
2,048 segments give parameter and period convergence ratios
`15.7178/15.7060`, with Richardson coordinate
`0.24070100822409128130`. An algebraically distinct RK4 3/8 sequence gives
ratios `15.7210/15.7069` and Richardson coordinate
`0.24070100822411182397`.

The two extrapolated coordinates differ by `2.05e-14`; extrapolated periods
differ by `7.21e-11`; finest nodes agree within `1.24e-10` maximum and
`5.04e-11` RMS; base tangents agree within `5.73e-13`; and the global
tangent-line cosine differs from one by only `4.51e-23`. Finest independent
orbit/tangent residuals are `5.05e-28/7.72e-25`, while half-orbit node RMS
remains `7.99e-6`, excluding the period-768 double cover.

The consensus midpoint is `a=0.24070100822410155263`, with cross-tableau
spread `2.05e-14`. It adds the sixth finite spacing ratio `5.312`, giving
`4.557/4.697/4.300/4.836/4.244/5.312`. This remains a non-monotone finite
sequence, not a limiting constant or universality result.

The qualified scope is eight exact numerical flip events on one returning-arm
orbit and six independently supercritical births through stable primitive
period 768. A period-3072 child, the seventh and eighth births' criticality,
paired shrimp boundaries, TBA membership, double-criticality, a homoclinic
endpoint, and global parameter-plane topology remain open.

Evidence:
[`../experiments/EXP-305-jones-period1536-decimal-augmented-refinement.md`](../experiments/EXP-305-jones-period1536-decimal-augmented-refinement.md)
and
[`../experiments/EXP-306-jones-period1536-decimal-augmented-independent.md`](../experiments/EXP-306-jones-period1536-decimal-augmented-independent.md).
