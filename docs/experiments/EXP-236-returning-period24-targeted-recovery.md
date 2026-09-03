# EXP-236 — Targeted period-24 switch recovery

Status: completed — failed primitive-child gate

EXP-235's closest failed switch is the positive direction at predictor step
`0.00025`, whose corrector reaches residual `1.19e-5` only when its frozen 160
evaluations are exhausted. EXP-236 retains that scale, both directions, exact
event, one-sided primary tangent, solver, and every candidate gate, changing
only the corrector ceiling to 480 evaluations.

A pass nominates primitive period-24 candidates for independent two-solver
qualification. A failure triggers segmented multiple shooting and does not
reject child existence.

## Result

The increased ceiling lets the positive-direction corrector converge after
329 evaluations with residual `2.03e-11`. The resulting orbit has closure
`1.51e-9`, period ratio `2.0000094`, and the required `28/32` section counts.
It is nevertheless rejected: its half-period closure is only `4.03e-9`, far
below the frozen `1e-4` primitivity gate. It is the period-12 parent traversed
twice, not a primitive period-24 child. The negative direction stops at
residual `0.472`.

This is a representation-specific negative result. It shows that additional
full-period iterations collapse to the doubled parent; it does not reject a
period-24 branch. EXP-237 therefore moves to an exact anti-periodic segmented
event solve before attempting a segmented child switch.

Raw receipt: `artifacts/EXP-236/receipt.json`, 4,227 bytes, SHA-256
`d522639a8bfffe86f764a2481c45417c6071184df37ce799bc2b54ca5b17422b`.
Compact receipt:
[`receipts/EXP-236.json`](receipts/EXP-236.json).

Manifest:
[`../../experiments/manifests/EXP-236-returning-period24-targeted-recovery.json`](../../experiments/manifests/EXP-236-returning-period24-targeted-recovery.json).
