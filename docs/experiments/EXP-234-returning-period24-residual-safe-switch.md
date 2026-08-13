# EXP-234 — Residual-safe multiscale period-24 switch

Status: complete — administrative failure before receipt

EXP-233 stops before receipt on a primary-family `xtol` status. EXP-234 keeps
the exact EXP-232 event, six predictor scales, both nullspace signs, solver,
and every period-24 nomination gate unchanged.

The sole change is representation-safe: a failed optimizer status may survive
only for the exact `xtol` message when raw closure is at most `2e-8` and phase
residual at most `1e-8`. All three primary-family correction statuses are
serialized in every scale trial.

A pass nominates primitive period-24 candidates for independent two-solver
qualification. It does not establish stability or supercriticality.

Manifest:
[`../../experiments/manifests/EXP-234-returning-period24-residual-safe-switch.json`](../../experiments/manifests/EXP-234-returning-period24-residual-safe-switch.json).

## Result

The residual-safe runner still stops before receipt because the positive
`a` primary-family offset is not a qualified correction: at `+1e-5` it has
raw closure `0.00801`, far outside the unchanged `2e-8` threshold. The center
and `-1e-5` corrections pass with raw closures `1.81e-11` and `4.20e-11`.

This is a failed symmetric tangent stencil, not evidence against the period-24
branch. EXP-235 changes only that stencil to the qualified one-sided offsets
`[-2e-5,-1e-5,0]`, retaining the exact event and every switch/candidate gate.
