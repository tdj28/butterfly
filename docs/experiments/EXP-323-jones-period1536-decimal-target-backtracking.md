# EXP-323 — Residual-decreasing correction of the EXP-299 target

Status: failed as unresolved — fixed decrease rule rejects a descent trial

EXP-322 preserves the full-step Newton failure: no iterate improves the
EXP-299 seed's initial `5.366e-10` exact-map mismatch. EXP-323 changes no
scientific gate and binds that raw failure by hash.

At each update, the same 50-digit fixed-`a` Newton direction is tested at
factors `1`, `1/2`, `1/4`, `1/8`, `1/16`, and `1/32` in that order. The first
trial reducing the maximum matching/phase residual by at least five percent,
or reaching `1e-20`, is accepted. If no trial qualifies, the experiment stops
unresolved. At most twelve accepted updates are allowed.

As in EXP-322, either a primitive period-1536 orbit or collapse to the doubled
period-768 parent may pass, but only after `1e-20` correction plus period,
cyclic Floquet, neutral, and unambiguous amplitude gates. Stability and node
identity remain outcome diagnostics.

Manifest:
[`../../experiments/manifests/EXP-323-jones-period1536-decimal-target-backtracking.json`](../../experiments/manifests/EXP-323-jones-period1536-decimal-target-backtracking.json).

## Result

EXP-323 fails after 523.00 seconds. At the first update, the full step raises
the residual by `2.115x`, while the accepted half step lowers it from
`5.366e-10` to `2.711e-10` and reduces half-node amplitude from `6.307e-6` to
`1.682e-6`.

At update two, factors through `1/16` increase the residual. The `1/32` trial
does descend to `2.697e-10`, a ratio of `0.99487`, but correctly fails the
frozen factor-independent `0.95` threshold. The accepted iterate therefore
remains unresolved and its Floquet spectrum is inadmissible.

The failure reveals a solver-design issue rather than a science-gate issue: a
fixed five-percent decrease is incompatible with sufficiently small Newton
fractions, whose expected linear decrease scales with the fraction. EXP-324
binds this failure and freezes a standard step-scaled Armijo rule while
retaining `1e-20` closure and every orbit-classification gate.

Raw receipt: `artifacts/EXP-323/receipt.json`, 351,951 bytes, SHA-256
`76e98740943d62b7de6a28366b6916cd2aa213cf03c1951380e3e9e5d94d2702`.
Compact receipt: [`receipts/EXP-323.json`](receipts/EXP-323.json).
