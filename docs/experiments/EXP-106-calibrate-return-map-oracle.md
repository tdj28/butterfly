# EXP-106 — Calibrate the branch oracle on a published chaotic Rössler control

Status: executed; failed expected branch count, discovered robust three branches

Use the Barrio-Blesa-Serrano Figure 2 chaotic-attractor control
`(a,b,c)=(0.2,0.2,20)` from EXP-005, with the same initial state `(0,4,0)` and
baseline DOP853 integrator. After transient `1000`, integrate for `8000` time
units and retain at most 1200 interpolated crossings.

Start from the recovered historical section through the small equilibrium and
perturb its plane offset by `-0.005`, `0`, and `+0.005`, leaving orientation and
the one-sided gate fixed. For each section, form consecutive return pairs from
the crossing `x` coordinate. Freeze 40 bins, five points per populated bin,
spline smoothing `1e-5`, prominence `0.03`, maximum conditional-spread ratio
`0.08`, minimum domain coverage `0.7`, and 100 deterministic bootstraps with
consensus `0.8`.

The classical scalar Rössler control is prospectively expected to resolve as a
two-branch relation on all three nearby sections. Pass only if every integration
succeeds with at least 1000 retained crossings and every oracle result is
resolved with branch count two. Failure is retained: a graph-likeness,
coverage, prominence, bootstrap, or section-robustness failure triggers
threshold/coordinate diagnosis and cannot be relabeled visually.

Passing calibrates the DEC-004 oracle on one real chaotic attractor and one
small section-perturbation family. It does not establish the Jones global
two/three-branch transition. That requires prospective application along a
declared parameter path and continuation of the transition boundary.

The clean run at `a6bcfa545e65901226013d677a8322a2561c402b` failed because all
three sections resolve as three branches rather than the frozen expectation of
two. This is not an unresolved or threshold-marginal result. Every section has
1200 crossings, domain coverage `1.0`, conditional spread ratio `0.01832027`,
and bootstrap consensus `1.0` with all 100 resamples returning three. The two
critical points stay near `x=-25.43355` and `x=-17.43792`; their maximum drift
across offset perturbations is about `2.2e-6`. Full receipt SHA-256:
`534629e20de81b9b90da2bd247b83076a635eecf4048e283bc00871650a2ad10`.

The preregistered calibration claim remains failed. The unexpected outcome is
retained as new local, section-offset-robust evidence for a three-branch scalar
return relation at one published chaotic control. Before promoting it toward
the Jones mechanism, a frozen sensitivity audit must vary crossing orientation,
coordinate, bin/smoothing/prominence choices, and nearby parameter values.
