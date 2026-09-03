# EXP-277 — Tighter period-768 tangent-sign audit

Status: completed — failed the unchanged multiplier-agreement gate

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

## Result

Nine of ten gates again pass. Tighter integration improves modulus spread from
`0.0034504` to `0.0026614`, but it remains above the unchanged `0.002` gate.
The failure is still isolated: sign RMS is `2.06e-8/2.93e-8`, cross-solver RMS
is at most `8.80e-9`, segment endpoint error is at most `1.03e-11`, and all
four orbits are stable and primitive.

The negative sign was selected independently before either sign audit by the
passed EXP-275 stability qualification. EXP-278 therefore freezes a canonical
phase representation from that preselected sign, binds both successful
whole-orbit identity results, and applies the unchanged `0.002` multiplier
spread gate to independent corrections of the same canonical seed.

Raw receipt: `artifacts/EXP-277/receipt.json`, 264,319 bytes, SHA-256
`88a9beffd13f9688ac7c193e8127548d933ec4b411e6b8218c23629812e6847c`.
Compact receipt:
[`receipts/EXP-277.json`](receipts/EXP-277.json).
