# EXP-286 — Decimal Richardson audit for the period-768 event

Status: completed — passed

EXP-285 fails only raw multiplier convergence, while its 4,096/8,192-step
flip errors decrease by a factor `15.988`, nearly the fourth-order factor 16.
EXP-286 adds one untouched 16,384-step classical-RK4 profile over all 1,024
immutable segments.

The test requires the second raw error ratio to stay in `[12,20]`, successive
order-four Richardson flip estimates to agree within `1e-7`, and the newest
extrapolated flip residual to lie within `1e-7` of `-1`. It applies analogous
neutral-root gates and preserves cyclic, characteristic, orbit, tangent,
primitive, and exact-section checks.

A pass qualifies a converged high-precision classical-RK4 multiplier estimate
at the immutable coordinate only. An independent high-precision integrator
remains mandatory before the seventh event can be promoted.

Manifest:
[`../../experiments/manifests/EXP-286-period768-decimal-richardson-audit.json`](../../experiments/manifests/EXP-286-period768-decimal-richardson-audit.json).

## Result

All 11 gates pass in 108.9 seconds. The untouched 16,384-step multiplier is
`-1.00000029755517`; the second raw convergence ratio is `15.9704`.
Successive order-four Richardson estimates are `-1.00000000380019` and
`-0.999999994828276`, differing by `8.97e-9`. The newest extrapolated flip
residual is `5.17e-9`.

The extrapolated neutral residual is `3.82e-8`, cyclic spread is `2.71e-43`,
and characteristic residual is `1.01e-49`. New-profile orbit/tangent
mismatches remain below `3.73e-11/1.15e-11`; primitivity and exact `896/1024`
identity pass.

This qualifies one converged high-precision classical-RK4 multiplier estimate
at the immutable coordinate, not the seventh event. EXP-287 freezes an
independent 50-digit RK4 3/8-tableau three-level Richardson audit and requires
cross-tableau agreement before event promotion.

Raw receipt: `artifacts/EXP-286/receipt.json`, 4,896 bytes, SHA-256
`3010388772d5fc8f1e975f19171192bd35b21df375c1d416c1b2faafdb8e7b02`.
Compact receipt:
[`receipts/EXP-286.json`](receipts/EXP-286.json).
