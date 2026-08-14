# EXP-297 — 8,192-step augmented event representation

Status: frozen before execution

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
