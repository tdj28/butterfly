# EXP-234 — Residual-safe multiscale period-24 switch

Status: frozen — not yet executed

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
