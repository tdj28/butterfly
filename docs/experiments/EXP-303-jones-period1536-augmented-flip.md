# EXP-303 — Augmented exact solve of the nominated eighth flip

Status: frozen before execution

EXP-302 isolates a `1.04e-13`-wide real-`-1` endpoint bracket on the primitive
period-1536 child. EXP-303 jointly corrects 2,048 orbit nodes, period, free
`a`, and 2,048 normalized antiperiodic tangent nodes from a nodewise secant
seed constructed only from the two successful exact bracket rows.

The reference DOP853 solve and independent segmented Radau replay both use
maximum step `0.01`. Orbit, phase, tangent, normalization, real-flip, cyclic,
proper-subperiod, and exact `1792/2048` section gates are unchanged in form
from the preceding exact event solve. A maximum-evaluation stop is admissible
only when every reference science residual already passes.

A pass qualifies an eighth exact real-`-1` event and tangent mode. A
period-3072 child and the eighth birth's criticality remain separate
prospective experiments.

Manifest:
[`../../experiments/manifests/EXP-303-jones-period1536-augmented-flip.json`](../../experiments/manifests/EXP-303-jones-period1536-augmented-flip.json).
