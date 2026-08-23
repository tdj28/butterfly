# EXP-324 — Armijo correction of the EXP-299 target

Status: frozen; not yet run

EXP-323 proves that deterministic backtracking can reduce the old target's
exact-map residual, but its fixed five-percent threshold rejects a genuine
`1/32` descent trial. EXP-324 binds that failed receipt and changes only the
sufficient-decrease rule.

Each fixed-`a` Newton update tests power-of-two fractions from `1` through
`1/1024`. It accepts the first factor `alpha` satisfying the standard
step-scaled condition

`R_trial <= (1 - 0.01 alpha) R_current`,

where `R` is the maximum matching/phase residual. No more than twenty accepted
updates are allowed. Failure to find a qualifying factor remains unresolved.

The exact-map closure gate remains `1e-20`. Primitive period-1536 survival and
doubled-period-768 collapse remain equally admissible, but neither may be
claimed without convergence plus the unchanged period, cyclic Floquet,
neutral, and amplitude-classification gates.

Manifest:
[`../../experiments/manifests/EXP-324-jones-period1536-decimal-target-armijo.json`](../../experiments/manifests/EXP-324-jones-period1536-decimal-target-armijo.json).
