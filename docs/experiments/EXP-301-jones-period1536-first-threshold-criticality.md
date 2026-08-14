# EXP-301 — Criticality at the first separated period-1536 row

Status: frozen before execution

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
