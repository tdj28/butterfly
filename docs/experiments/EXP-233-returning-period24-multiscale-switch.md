# EXP-233 — Multiscale period-24 branch switch

Status: complete — administrative failure before receipt

EXP-232 qualifies a primitive period-12 real-`-1` event on the exact returning-
arm offset path. EXP-233 represents that orbit over twice its period, separates
the primary-family and doubled-period null directions, and probes both signs
at six predictor lengths from `0.008` through `0.00025`.

At least one corrected candidate must close within `2e-8`, have period ratio
two relative to the period-12 parent, reject half-period closure, retain
historical/Barrio counts `28/32`, move in `a`, and separate from the doubled
primary family. A pass only nominates primitive period-24 candidates; a
separate experiment must independently recorrect them under DOP853 and Radau
and test parent/child stability exchange.

Manifest:
[`../../experiments/manifests/EXP-233-returning-period24-multiscale-switch.json`](../../experiments/manifests/EXP-233-returning-period24-multiscale-switch.json).

## Result

The run stops before atomic receipt while constructing the primary period-12
family tangent. One offset correction reports optimizer failure at `xtol`, and
the inherited switch helper raises before testing its orbit residuals. No
period-24 nomination decision is available.

EXP-234 preserves the event, solver, predictor scales, nullspace construction,
and every scientific gate. It adds only the residual-safe `xtol` rule already
validated by EXP-232 and serializes all primary-correction statuses.
