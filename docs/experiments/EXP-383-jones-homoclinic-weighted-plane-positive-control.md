# EXP-383 — Weighted-plane multiple-shooting positive control

Status: frozen; not yet executed

EXP-382 rejects unconstrained collocation even at the qualified EXP-368 root.
EXP-371--377 show that the pure physical `(a,c)` plane is nearly singular,
whereas EXP-369 shows that the unweighted full-state plane can select a
wrong-direction root.  EXP-383 returns to the bounded analytic-variational
multiple-shooting representation and tests a prospectively weighted hybrid.

The closing-plane weights are fixed before execution:

```text
nodes = 0.01
total flight time = 0.01
a = 1
c = 1
angle = 0.01
```

With the EXP-367/368 secant and existing variable scales, this makes the
physical `(a,c)` direction dominant while retaining a small full-state
component to regularize the measured near-null mode.  The predictor step is
exactly zero.  Deterministic subdivision converts the two 256-arc sources to
512 arcs, and the result must reproduce EXP-368 without moving `c` by more
than `1e-8`.

Manifest:
[`../../experiments/manifests/EXP-383-jones-homoclinic-weighted-plane-positive-control.json`](../../experiments/manifests/EXP-383-jones-homoclinic-weighted-plane-positive-control.json).

Only a pass below the unchanged `1e-8` maximum matching-block gate and the new
`1e-10` arclength gate licenses a forward weighted-plane crossing attempt.
This control cannot qualify the exact historical-section intersection.
