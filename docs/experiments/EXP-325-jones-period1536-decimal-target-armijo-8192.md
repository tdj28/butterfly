# EXP-325 — Resolution-doubled replay of the EXP-299 target collapse

Status: frozen; not yet run

EXP-324 closes the original EXP-299 seed below `1e-20` in the 4,096-step
50-digit RK4 3/8 map and collapses its primitive amplitude to `7.38e-20`.
EXP-325 binds that passed raw receipt and replays the correction from the
unchanged original seed using the passed EXP-320 event period and 8,192 steps
per segment.

The complete Armijo factor ladder, coefficient, twenty-update cap, precision,
fixed parameters, and every science gate are unchanged. The run does not start
from EXP-324's collapsed endpoint; it must independently globalize the old
Float64 seed in the finer discrete map.

Either primitive survival or doubled-parent collapse may pass. Agreement with
EXP-324 promotes FND-106 across two resolutions, while disagreement preserves
both receipts and leaves the seed fate representation-dependent.

Manifest:
[`../../experiments/manifests/EXP-325-jones-period1536-decimal-target-armijo-8192.json`](../../experiments/manifests/EXP-325-jones-period1536-decimal-target-armijo-8192.json).
