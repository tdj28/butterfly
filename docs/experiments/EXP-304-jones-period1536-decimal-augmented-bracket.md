# EXP-304 — Cyclic-elimination pilot for the nominated eighth flip

Status: completed — failed `a_bounds` and raw tangent neighborhood

EXP-303 shows that dense trust-region correction is operationally unsuitable
for the 12,290-variable augmented system. EXP-304 retains the identical first
EXP-302 bracket and constructs the orbit and tangent seed only from its two
successful exact endpoint rows.

The pilot evaluates the full 2,048-segment orbit and antiperiodic tangent at 50
decimal digits with classical RK4 and 1,024 steps per segment. Exact cyclic
elimination reduces every Newton update to an 8-by-8 system in base state,
base tangent, total period, and `a`; eight workers integrate the segment
profiles in parallel.

A pass requires all discrete augmented residuals below `1e-22`, the corrected
coordinate inside the untouched `1.04e-13` bracket, bounded displacement from
the secant seed, and half-node RMS above `5e-6`. A pass validates only this
single discrete formulation. Multi-resolution convergence and an independent
RK4 tableau remain mandatory before an eighth event is promoted.

Manifest:
[`../../experiments/manifests/EXP-304-jones-period1536-decimal-augmented-bracket.json`](../../experiments/manifests/EXP-304-jones-period1536-decimal-augmented-bracket.json).

## Result

The scalable formulation works. Five reduced Newton updates converge the
50-digit discrete equations to orbit/tangent residuals
`6.69e-33/2.70e-31`; phase and normalization residuals are
`2.92e-52/1.77e-37`. Runtime is 145 seconds after the DOP853 tangent seed.
Half-node RMS is `7.99e-6`, so the primitive period-1536 orbit does not collapse
to a period-768 double cover.

The frozen receipt nevertheless fails two gates. At 1,024 RK4 steps per
segment, the corrected coordinate is
`0.2407010036618510867056640438`, shifted `4.576e-9` below the secant seed and
outside the `1.04e-13` physical bracket. Raw tangent coordinates move by
`54.55`, exceeding the pilot neighborhood even though orbit-node and period
displacements remain only `7.30e-6/1.60e-5`.

This validates the 8-by-8 cyclic formulation but not the physical event. The
next experiment must warm-start 2,048- and 4,096-step profiles, require
fourth-order coordinate/period convergence and Richardson bracket recovery,
and compare sign-aligned tangent lines rather than raw transported tangent
coordinates.

Raw receipt: `artifacts/EXP-304/receipt.json`, 697,130 bytes, SHA-256
`3b850e0544ec3edd0647de53dc3d0fbbd1fab654694796f9d1fa3895c0d411b2`.
Compact receipt:
[`receipts/EXP-304.json`](receipts/EXP-304.json).
