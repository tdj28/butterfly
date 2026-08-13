# EXP-286 — Decimal Richardson audit for the period-768 event

Status: frozen — not yet executed

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
