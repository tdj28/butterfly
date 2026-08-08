# FND-031 — Two distinct lag-12 UPO families persist across the local boundary

Status: qualified finite local result from passed EXP-138

## Finding

The primitive lag-12 UPO seeded from the blind two-branch saddle and the
primitive lag-12 UPO seeded from the three-branch saddle each continue through
all 21 frozen points of `a in [0.148,0.14825]` at `(b,c)=(0.2,20)`.

The lower-seeded family has period `75.0981` to `75.1084` and unstable modulus
`2165.49` to `2219.28`. The upper-seeded family has period `75.2335` to
`75.2433` and unstable modulus `1146.64` to `1165.73`. All flow closures are
below `2.30e-9`, neutral-multiplier errors below `5.52e-10`, and proper-divisor
closures above `4.50`.

At the common mathematical midpoint `a=0.148125`, the relative period
difference is `1.7970e-3`, above the frozen distinctness threshold `1e-4`.
Continuous phase-invariant whole-orbit RMS also decisively separates them.
They are two different primitive orbit families, not the same family viewed at
different phases.

All 42 phase-shifted intervals `(0.1 T, 1.1 T]` contain 12 positive Barrio
crossings. This prospectively confirms that EXP-136's 11-count failures were
arbitrary period-window boundary effects.

## Consequence

Three simple local explanations are now ruled out over this finite bracket:

1. birth or death of the upper-side lag-4 UPO;
2. birth or death of either tested lag-12 UPO family; and
3. loss of a Barrio-section crossing by either lag-12 family.

The return-map branch opening must instead be sought in invariant-manifold
geometry, pruning/reinjection, a crisis-like global event, or an untested orbit
family. Persistence of these UPOs does not imply persistence of their
admissible symbolic connections: stable/unstable manifolds can rearrange while
the periodic skeleton survives.

Tracked receipt: `docs/experiments/receipts/EXP-138.json`.
