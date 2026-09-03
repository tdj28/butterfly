# FND-086 — The returning arm has local opposing-side stability exchange

Status: numerically qualified at one held-out returning-arm slice

At the untouched `c=7.16299104` EXP-217 event, EXP-220 recovers four primitive
stable period-12 children toward lower `a`, opposite the original flip arm's
qualified higher-`a` opening. Each is paired with an unstable period-6 parent,
has period ratio two, retains exact `7/8` parent versus `14/16` child section
identity, rejects every proper subperiod, and agrees between DOP853 and Radau.

This is the first dynamical evidence—not just parameter-plane geometry—that
the returning arm is locally compatible with an opposing shrimp boundary.
The complete three-slice claim fails: a middle-slice candidate lies on the
wrong side and fails qualification, while the far single-shooting switch
produces no candidate. Those failures leave remote child existence unresolved.

Evidence:
[`../experiments/EXP-220-returning-period12-children-multiscale.md`](../experiments/EXP-220-returning-period12-children-multiscale.md).
