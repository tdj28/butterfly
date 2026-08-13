# EXP-236 — Targeted period-24 switch recovery

Status: frozen — not yet executed

EXP-235's closest failed switch is the positive direction at predictor step
`0.00025`, whose corrector reaches residual `1.19e-5` only when its frozen 160
evaluations are exhausted. EXP-236 retains that scale, both directions, exact
event, one-sided primary tangent, solver, and every candidate gate, changing
only the corrector ceiling to 480 evaluations.

A pass nominates primitive period-24 candidates for independent two-solver
qualification. A failure triggers segmented multiple shooting and does not
reject child existence.

Manifest:
[`../../experiments/manifests/EXP-236-returning-period24-targeted-recovery.json`](../../experiments/manifests/EXP-236-returning-period24-targeted-recovery.json).
