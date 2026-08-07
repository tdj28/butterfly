# EXP-103 — Exact augmented period-640 flip solve

Status: executed; passed

Apply the EXP-102-validated exact augmented formulation to the unresolved
period-640 parent. Bind the failed full EXP-099 receipt for its tight-solver
64-node orbit at `b=0.17971219643223532`, and independently bind the passed
full EXP-102 validation receipt. Recompute the initial anti-periodic tangent
field with the frozen tight integrator.

Use the audited EXP-093 signed bracket `[0.17971219,0.17971220]` as the hard
optimizer bounds. The narrower EXP-099 interval is retained as evidence but is
not used as a hard box because its endpoint behavior is sensitive at a few
double-precision ulps. Keep DOP853 `rtol=1e-12`, `atol=1e-14`, and
`max_step=0.025`; permit 30 exact residual/Jacobian evaluations at tolerance
`1e-11`.

The frozen prospective prediction `b=0.17971219644700012` is recorded as the
comparison target, not fitted as an equality. Pass only on solver success, a
solution inside the signed bracket, prediction error `<=5e-8`, orbit, phase,
tangent, and normalization residuals each `<=1e-8`, direct flip residual
`<=1e-6` with imaginary part `<=1e-8`, and block/direct difference and cyclic
spread each `<=1e-8`.

Passing establishes the corrected eighth parent event and completes the third
prospective event-location test. It does not establish supercriticality or a
stable period-1280 child; those require a separately frozen branch switch and
common-parameter identity/Floquet qualification. Failure retains only the
EXP-093/099 bracket evidence and triggers diagnosis.

The clean run at `859a3024c50c2c21d1c68dd48fbf10cfd7d32911` passed in three
exact evaluations and `62.68 s`. It converged to
`b=0.17971219643223899`, only `-1.476e-11` from the frozen prospective
prediction. Orbit, tangent, phase, and normalization residuals are
`1.46e-12`, `7.81e-12`, `1.95e-18`, and `2.22e-16`. Four direct products give
`-0.999999999809874`, with block/direct difference `6.66e-15` and cyclic
spread `2.66e-15`. Full receipt SHA-256:
`ddc37ede99dce1070c1e00bdab30f21afeb1ec468679ebd903e4cc49beb618bb`.

The corrected eighth event is established, and the third frozen prospective
event-location test succeeds. The new finite spacing ratio is `4.6689869`.
EXP-094 through EXP-096 and EXP-098/099 remain failed pointwise scalar
experiments; EXP-103 shows that their limit was removed by solving the orbit
and anti-periodic tangent together. A period-1280 child, its identity, and
supercriticality remain unclaimed pending separate experiments.
