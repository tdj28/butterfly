# EXP-285 — Full decimal multiplier audit for the period-768 event

Status: frozen — not yet executed

EXP-284 establishes clean 50-digit fourth-order convergence on four
phase-separated segments. EXP-285 extends the same state and variational
integrator to all 1,024 immutable EXP-281 segments, using nested 4,096 and
8,192-step profiles and eight local workers.

For each profile, four cyclic monodromy products are accumulated entirely in
50-digit decimal arithmetic. The real roots near `-1` and `+1` are solved
from each `3x3` characteristic polynomial without converting the products to
Float64. The audit gates medium/fine multiplier convergence, cyclic spread,
characteristic residual, the neutral root, segment integration convergence,
orbit/tangent matching, primitivity, and exact section identity.

A pass supplies a converged high-precision multiplier at the immutable source
`a` and permits a separately frozen arbitrary-precision parameter correction.
It does not itself qualify the seventh event.

Manifest:
[`../../experiments/manifests/EXP-285-period768-decimal-multiplier-audit.json`](../../experiments/manifests/EXP-285-period768-decimal-multiplier-audit.json).
