# EXP-324 — Armijo correction of the EXP-299 target

Status: passed — EXP-299 seed collapses to the doubled parent

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

## Result

EXP-324 passes all gates after 3,404.10 seconds. Thirteen accepted Armijo
updates reduce matching from `5.366e-10` to `1.196e-23`. The accepted factors
are `1/2`, `1/32`, `1/128`, `1/256`, `1/256`, `1/16`, `1/16`, `1/4`, then
five full steps. This records the severe near-flip conditioning without
relaxing the closure target.

The half-node RMS falls from `6.30690e-6` to `7.38176e-20`, unambiguously
classifying the corrected solution as the doubled period-768 parent. The
neutral residual is `1.22e-20`, cyclic spread is zero, and the doubled-parent
transverse modulus is `0.208036`. Thus the old EXP-299 Float64 seed does not
survive as a primitive higher-`a` period-1536 orbit in the 4,096-step exact
map; its earlier apparent stable-child multiplier was evaluated on an
insufficiently closed near-neutral seed.

This retracts the interim separate-sheet/fold interpretation, not the Jones
cascade. EXP-325 freezes a complete 8,192-step replay from the original seed
before the collapse is promoted across resolutions.

Raw receipt: `artifacts/EXP-324/receipt.json`, 372,313 bytes, SHA-256
`c077aeaa23ca74fd64fc74f98d39ca7ad6ba81a255955ccf87647f3a0bf233e6`.
Compact receipt: [`receipts/EXP-324.json`](receipts/EXP-324.json).
