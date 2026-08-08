# FND-030 — Lag 4 persists; lag 12 loses a section crossing

Status: qualified positive and negative result from failed EXP-136

## Finding

The primitive unstable lag-4 orbit recovered on the three-branch side
continues through all 21 frozen parameter points to the two-branch endpoint.
Throughout `a in [0.148,0.14825]` it retains four oriented Barrio-section
crossings, flow closure below `3.44e-11`, neutral-multiplier accuracy near
`1e-10`, proper-divisor nonclosure above `5.36`, and unstable modulus from
`3.484` to `3.664`.

Its creation or destruction is therefore ruled out as the branch-opening
event inside this sampled interval. Its stable or unstable manifolds may still
undergo a tangency or pruning event.

Both lag-12 continuations fail their prospectively frozen crossing-identity
gate near their source endpoints. The lower path passes at `a=0.148` and
`0.1480125`, then has 11 rather than 12 oriented crossings at `0.148025`. The
upper path has 12 at `0.14825` and 11 at `0.1482375`. At both failed points,
periodic correction, flow closure, neutral multiplier, primitivity, and strong
transverse instability still pass. The flow orbit has not disappeared; its
intersection count with the moving Barrio plane has changed.

## Consequence

This is a candidate section-tangency phenomenon on unstable periodic orbits,
analogous in category—but not yet shown identical in role—to the stable-orbit
section grazing isolated by EXP-055. Fixed return-map lag is therefore too
strict to continue these flow families through the interval.

The two lag-12 endpoint seeds are not yet proved equal or distinct. Their
declared midpoint identity comparison is invalid because neither fixed-lag
path reached the midpoint. The next test must continue the closed flow orbits
without freezing their section count, locate the simultaneous section and
tangency condition, and only then perform phase-invariant family matching.

Tracked receipt: `docs/experiments/receipts/EXP-136.json`.
