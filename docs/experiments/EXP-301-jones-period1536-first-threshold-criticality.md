# EXP-301 — Criticality at the first separated period-1536 row

Status: completed — failed because parent and child are both unstable

EXP-300 fails its full 33-row continuation gate but preserves an exact accepted
prefix. EXP-301 deterministically selects the first prefix row whose absolute
distance from the bound finite 8,192-step event coordinate reaches `1e-11`.
This is step 16 at `a=0.24070100822533044`; every source row through it must
retain matching below `1e-8` and half-node RMS above `5e-6`. No preliminary
multiplier participates in selection.

DOP853 and Radau independently correct the 1,024-segment parent and
2,048-segment child at this fixed coordinate. Both must pass matching, phase,
cyclic node identity, multiplier-spread, child half-period nonclosure, and
exact `1792/2048` section identity gates. Consistent
parent-unstable/child-stable or parent-stable/child-unstable classifications
pass; unresolved or mixed classifications fail.

A pass qualifies the sampled seventh birth as supercritical or subcritical.
It does not validate EXP-300 beyond the selected prefix, establish a globally
stable period-1536 branch, or establish an eighth event.

Manifest:
[`../../experiments/manifests/EXP-301-jones-period1536-first-threshold-criticality.json`](../../experiments/manifests/EXP-301-jones-period1536-first-threshold-criticality.json).

## Result

Both solvers independently correct the same parent and child and pass every
nonclassification gate. DOP853/Radau parent moduli are
`1.0013257841/1.0013032457`, consistently beyond the frozen `1e-4` neutral
margin. Child moduli are `284.8080412/284.8091548`, also consistently unstable.
Relative parent/child spreads are only `2.25e-5/3.91e-6`; solver-node RMS is
below `9.00e-10`; all matching residuals remain below `9.83e-9`; child
half-period closures are `7.98e-5/7.96e-5`; and exact `1792/2048` identity
passes.

The frozen result fails because parent and child are on the same unstable side,
so the classification is `other-or-unresolved`. This does not contradict
EXP-299's independently stable child at the source coordinate. Instead, the
two audits establish a stability-change bracket along the exact accepted child
prefix: the daughter is stable at the source and strongly unstable by step 16.
No real-`-1` event, eighth birth, or seventh-birth criticality direction is
claimed until that child stability loss is scanned and refined.

Raw receipt: `artifacts/EXP-301/receipt.json`, 389,010 bytes, SHA-256
`0da8240a6ca16bc756bbb0526ae5e2478aa0873fe4e8db9d7c534c6fd29d9339`.
Compact receipt:
[`receipts/EXP-301.json`](receipts/EXP-301.json).
