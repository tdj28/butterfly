# EXP-323 — Residual-decreasing correction of the EXP-299 target

Status: frozen; not yet run

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
