# EXP-304 — Cyclic-elimination pilot for the nominated eighth flip

Status: frozen before execution

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
