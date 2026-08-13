# EXP-283 — Float64 resolution diagnostic for the period-768 event

Status: frozen — not yet executed

EXP-282 leaves a `3.67e-7` tight DOP853/Radau multiplier disagreement on the
same immutable event representation. Before repeating a costly coupled solve,
EXP-283 binds that receipt to the original EXP-280 bracket and compares two
scales with the unchanged `1e-7` event tolerance:

- half the cross-solver multiplier disagreement, the best common-centering
  residual if that local gap persists; and
- the bracket-secant multiplier change corresponding to one representable
  Float64 increment at the corrected `a`.

This is a deterministic conditioning diagnostic, not a seventh-event solve.
A pass motivates a separately frozen higher-precision or better-conditioned
formulation; it does not prove that every possible Float64 formulation fails.

Manifest:
[`../../experiments/manifests/EXP-283-period768-float64-resolution.json`](../../experiments/manifests/EXP-283-period768-float64-resolution.json).
