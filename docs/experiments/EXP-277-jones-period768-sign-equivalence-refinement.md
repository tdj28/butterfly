# EXP-277 — Tighter period-768 tangent-sign audit

Status: frozen — not yet executed

EXP-276 passes whole-orbit sign identity, cross-solver identity, correction,
endpoint, period, stability, and primitivity gates, but misses the `0.002`
modulus-spread gate at `0.0034504`. EXP-277 repeats the complete common-`a`
audit with both solvers' maximum step reduced from `0.03` to `0.01` and
tighter integration tolerances.

All science thresholds are unchanged, including the failed modulus gate and
the `1e-6` whole-orbit sign-identity gate. A pass may qualify the two signs as
one stable primitive period-768 orbit; a failure remains evidence against
deeper continuation from an arbitrarily chosen sign.

Manifest:
[`../../experiments/manifests/EXP-277-jones-period768-sign-equivalence-refinement.json`](../../experiments/manifests/EXP-277-jones-period768-sign-equivalence-refinement.json).
