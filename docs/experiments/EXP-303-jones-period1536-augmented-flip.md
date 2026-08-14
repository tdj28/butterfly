# EXP-303 — Augmented exact solve of the nominated eighth flip

Status: terminated — dense formulation computationally unsuitable; no verdict

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

## Administrative result

The 12,290-variable dense trust-region formulation is terminated after four
evaluations. The secant seed at `a=0.24070100823779308` has residual norm
`0.2509918851`; the second trial leaves it unchanged, and the next two trials
diverge to `2.91e6` and `1.84e5`. Each dense factorization takes several
minutes and memory reaches about 2 GB. Continuing the remaining 20 allowed
evaluations would not be a proportionate scientific computation.

No raw result receipt is produced, no acceptance gate is evaluated, and this
termination is neither a scientific pass nor a scientific failure. EXP-302's
bracket remains unchanged. The next implementation retains the exact bracket
and science gates but replaces the dense solve with the already validated
Decimal cyclic elimination to an 8-by-8 Newton system.

Administrative compact receipt:
[`receipts/EXP-303.json`](receipts/EXP-303.json).
