# EXP-307 — 8,192-step representation of event eight

Status: frozen before execution

EXP-306 qualifies the primitive period-1536 real-`-1` event from independent
three-resolution augmented sequences. Before attempting a 4,096-segment
period-3072 switch, EXP-307 applies the same representation safeguard required
at the preceding rung: refine the passed RK4 3/8 event from 4,096 to 8,192
steps on every one of 2,048 segments.

The 2,048/4,096/8,192 parameter and period increments must converge with
ratios in `[12,20]`. Successive Richardson estimates, source displacement,
augmented residual, target-blind continuation-envelope, and primitive
half-orbit gates are frozen. The doubled representation must then pass direct
DOP853 event matching below `1e-8` and secondary-null residual below `1e-6`.

A pass qualifies only this representation as the source of a prospective
period-3072 switch. It does not establish a child or birth direction.

Manifest:
[`../../experiments/manifests/EXP-307-jones-period1536-decimal-augmented-8192.json`](../../experiments/manifests/EXP-307-jones-period1536-decimal-augmented-8192.json).
