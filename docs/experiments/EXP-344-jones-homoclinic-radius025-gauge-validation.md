# EXP-344 — Radius-0.025 nuisance-gauge validation

Status: frozen; not yet run

EXP-343 solves the radius-`0.025` matching equations below `1e-8` and preserves
`a` to `1.30e-13`, but fails because its nearly null departure-angle coordinate
lands on the old box boundary. EXP-344 binds those exact matched nodes and does
not optimize them further.

Only the angle half-width is prospectively widened from `0.0327249` to `0.15`.
The physical endpoint geometry, radius, 32 Radau arcs, `a` box, residual gate,
and `2e-6` parameter-persistence requirement remain fixed. The one-evaluation
run passes only if the bound seed reproduces below `1e-8` and is interior under
the corrected nuisance gauge.

Passing qualifies one shrinking-radius persistence step. It does not replace
the radius-`0.02` test, validate the paper's printed `a`, or establish
uniqueness.

Manifest:
[`../../experiments/manifests/EXP-344-jones-homoclinic-radius025-gauge-validation.json`](../../experiments/manifests/EXP-344-jones-homoclinic-radius025-gauge-validation.json).
