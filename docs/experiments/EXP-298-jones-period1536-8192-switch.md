# EXP-298 — Period-1536 switch from the 8,192-step event

Status: frozen before execution

EXP-297 passes the DOP853 source gate that stopped EXP-296. EXP-298 repeats the
period-1536 switch from that 8,192-step event representation. It prospectively
uses only predictor length `0.00025`, selected from EXP-296 because both signs
maximize half-node and half-period separation, not because of their
preliminary multipliers.

Both tangent signs must pass the unchanged source, secondary-null, correction,
residual, primitivity, displacement, period-ratio, and exact `1792/2048`
identity gates. A pass nominates the two representations for a separately
frozen sign-equivalence and two-solver stability audit; it does not decide
birth criticality.

Manifest:
[`../../experiments/manifests/EXP-298-jones-period1536-8192-switch.json`](../../experiments/manifests/EXP-298-jones-period1536-8192-switch.json).
