# EXP-296 — Period-1536 switch from the qualified augmented event

Status: completed — failed only the unchanged source event-matching gate

The earlier EXP-288--291 period-1536 candidates were rooted in the retracted
Float64 event coordinate and cannot establish the seventh birth's criticality.
EXP-296 repeats the sparse bilateral switch from EXP-295's passed 4,096-step
RK4 3/8 augmented event representation.

All EXP-288 predictor lengths, solver tolerances, residual, primitivity,
parameter-displacement, period-ratio, and exact `1792/2048` identity gates are
unchanged. The source must also pass the original DOP853 event-matching and
secondary-null gates despite the change in representation. At least two of the
six switched candidates must pass.

A pass only nominates corrected period-1536 candidates. Independent DOP853 and
Radau parent/child correction and stability exchange are required before the
seventh birth can be called supercritical or subcritical.

Manifest:
[`../../experiments/manifests/EXP-296-jones-period1536-qualified-event-switch.json`](../../experiments/manifests/EXP-296-jones-period1536-qualified-event-switch.json).

## Result

All six bilateral candidates pass their correction, residual, phase,
primitivity, period-ratio, displacement, and exact `1792/2048` identity gates.
Every solve takes two evaluations. Half-node RMS grows from `1.58e-6` to
`6.31e-6`, and half-period closure grows from `5.56e-7` to `3.07e-6` across
the predictor ladder. The corrected coordinates lie within
`1.77e-13`--`2.01e-13` of FND-102's Richardson consensus coordinate.

The receipt nevertheless fails overall because the doubled 4,096-step source
has DOP853 event-matching norm `1.441e-8`, narrowly above the unchanged `1e-8`
gate. Its secondary-null residual is `4.48e-11`. No child is promoted from a
failed source gate, and the preliminary candidate multipliers are not used for
criticality.

EXP-297 must refine the independent augmented event to 8,192 steps and require
the expected fourth-order increment plus direct passage of the same DOP853
source gate. Only then may a fresh switch be frozen.

Raw receipt: `artifacts/EXP-296/receipt.json`, 1,520,301 bytes, SHA-256
`b95912543e0b15566bb93dda64994c1cbd178625655200c1988e89e4bf69f4ac`.
Compact receipt:
[`receipts/EXP-296.json`](receipts/EXP-296.json).
