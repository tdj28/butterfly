# EXP-296 — Period-1536 switch from the qualified augmented event

Status: frozen before execution

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
