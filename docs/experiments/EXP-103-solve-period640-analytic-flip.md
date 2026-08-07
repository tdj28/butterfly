# EXP-103 — Exact augmented period-640 flip solve

Status: preregistered; not executed

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
