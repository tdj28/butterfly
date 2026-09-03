# EXP-285 — Full decimal multiplier audit for the period-768 event

Status: completed — failed one convergence gate

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

## Result

Nine of ten gates pass in 80.5 seconds. All 1,024 fine-grid orbit/tangent
mismatches remain below `5.54e-11/1.82e-10`; segment endpoint/transition
differences are below `5.58e-10/4.44e-10`. Four cyclic products agree to
`1.82e-43`, their characteristic residuals are below `1.01e-49`, and the
fine neutral root passes.

The raw flip multiplier moves from `-1.00007735833519` at 4,096 steps to
`-1.00000483845863` at 8,192. Their difference, `7.25e-5`, fails the frozen
`1e-7` convergence gate, so this receipt does not supply a converged
multiplier and does not qualify the seventh event.

The residual ratio is `15.988`, closely matching fourth-order error reduction;
the prospectively unclaimed two-level Richardson value is
`-1.00000000380`. EXP-286 freezes a new 16,384-step profile and gates
successive Richardson estimates before that extrapolation is promoted.

Raw receipt: `artifacts/EXP-285/receipt.json`, 6,190 bytes, SHA-256
`832e419cf3e1597a878df5a1f7da80a740626715f2d6bd34fb8f990ea33b6c21`.
Compact receipt:
[`receipts/EXP-285.json`](receipts/EXP-285.json).
