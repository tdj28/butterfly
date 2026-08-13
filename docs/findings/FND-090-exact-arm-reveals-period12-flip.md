# FND-090 — Exact-arm continuation reveals a period-12 flip

Status: numerically qualified with two solvers and bilateral controls

After EXP-229 removes the interpolation-induced false period-6 boundary,
EXP-230 carries the primitive period-12 child farther and brackets its real
multiplier crossing `-1`. EXP-232 independently localizes that crossing with
DOP853 and Radau to `3.38e-8` in `c` near
`(a,c)=(0.2407011815,7.6258156004)`.

Both roots retain primitive `14/16` two-section identity, period ratio two,
finite proper-subperiod separation, and an unstable period-6 parent. Both
solvers also show the period-12 multiplier moving from approximately
`-0.998722` to `-1.001278` across bilateral points.

The former apparent endpoint is therefore replaced by a deeper cascade rung:
the period-12 child loses stability in a flip. This strengthens Jones's local
cascade mechanism but does not yet establish the period-24 child,
supercriticality, a complete child surface, paired shrimp boundaries, TBA
membership, or double-criticality.

Evidence:
[`../experiments/EXP-232-returning-period12-flip-residual-safe.md`](../experiments/EXP-232-returning-period12-flip-residual-safe.md).
