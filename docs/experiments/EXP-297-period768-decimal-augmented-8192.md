# EXP-297 — 8,192-step augmented event representation

Status: completed — passed all ten gates

EXP-296 accepts all six switched children but fails the unchanged DOP853 source
event-matching gate by a narrow margin. EXP-297 extends the independent RK4 3/8
augmented event from 4,096 to 8,192 steps on every segment before any switch is
retried.

The 2,048/4,096/8,192 increments in `a` and period must converge with ratios in
`[12,20]`; successive Richardson estimates, source displacement, augmented
residual, event bracket, and primitive half-orbit gates are frozen. The doubled
8,192-step representation must then pass the same DOP853 `1e-8` event-matching
and `1e-6` secondary-null gates that stopped EXP-296.

A pass qualifies only this representation as the source of a fresh switch. It
does not promote any prior child or decide seventh-birth criticality.

Manifest:
[`../../experiments/manifests/EXP-297-period768-decimal-augmented-8192.json`](../../experiments/manifests/EXP-297-period768-decimal-augmented-8192.json).

## Result

The 8,192-step augmented system converges in two Newton updates to
`1.28e-31/5.67e-31` orbit/tangent residuals. The 2,048/4,096/8,192 increments
give `a` and period ratios `15.860/15.853`. The new Richardson coordinate is
`0.24070100823774155628`, only `1.41e-13` from the previous independent
estimate; the Richardson period changes by `2.97e-10`.

State, tangent, period, bracket, and primitive-separation gates all pass. The
doubled representation's DOP853 event-matching residual is `9.64e-10`, down
from EXP-296's `1.441e-8` and below the unchanged `1e-8` gate. The
secondary-null residual is `3.61e-12`.

EXP-297 therefore qualifies the 8,192-step event representation as the source
of a fresh period-1536 switch. It does not promote any EXP-296 candidate or
decide birth criticality.

Raw receipt: `artifacts/EXP-297/receipt.json`, 352,578 bytes, SHA-256
`8942a66a3bad641624ddb188630c4e0f882a0b806d6519dfe0b48ee622118c95`.
Compact receipt:
[`receipts/EXP-297.json`](receipts/EXP-297.json).
