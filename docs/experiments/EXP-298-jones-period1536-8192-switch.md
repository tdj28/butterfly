# EXP-298 — Period-1536 switch from the 8,192-step event

Status: completed — passed all frozen gates

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

## Result

Both signs correct in two evaluations and pass every source, secondary-null,
matching, phase, primitivity, displacement, period-ratio, and exact
`1792/2048` identity gate. The common coordinate is
`a=0.24070100823781396`, only `7.24e-14` above EXP-297's Richardson event
estimate. Half-node RMS is `6.31e-6`; half-period closures are
`2.11e-6/2.97e-6`.

The raw DOP853 multipliers disagree strongly between sign representations
(`0.0394` versus `1.1748` modulus), so neither is a stability result. The
positive sign is prospectively selected for the next two-solver correction by
its larger half-period closure, not by that preliminary multiplier.

Raw receipt: `artifacts/EXP-298/receipt.json`, 507,907 bytes, SHA-256
`b929effef1dd0f84073631f6da60b6dd0324331af434e7f6d6fc40edf89d6b26`.
Compact receipt:
[`receipts/EXP-298.json`](receipts/EXP-298.json).
