# EXP-220 — Exact-event multiscale returning-arm child test

Status: prospectively frozen before execution

EXP-219 serializes a complete negative single-shooting switch: neither signed
direction produces a candidate at any of three events. The two remote source
events also have under-resolved doubled-period singularities under the
inherited integration configuration.

EXP-220 first recorrects each real-`-1` event with the analytic augmented
second-variational system at tighter tolerance. It then probes both signed
secondary nullspace directions at the declared predictor lengths `0.002`,
`0.001`, `0.0005`, and `0.00025`, retaining no failed solve. Every generated
candidate is subjected to the unchanged primitivity, `7/8` versus `14/16`
section identity, period-ratio, parent/child Floquet stability-exchange, and
DOP853/Radau whole-orbit gates.

The directional prediction remains frozen: each event must yield a primitive
stable period-12 child toward lower `a`. A pass is compatible with the
returning arm being an opposing shrimp boundary. A failure may still diagnose
single-shooting conditioning and cannot establish child nonexistence.

Manifest:
[`../../experiments/manifests/EXP-220-returning-period12-children-multiscale.json`](../../experiments/manifests/EXP-220-returning-period12-children-multiscale.json).
