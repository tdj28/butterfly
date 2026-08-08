# FND-020 — `a=0.148` topology is escape-lifetime-conditioning sensitive

Status: strong diagnosis from a prospectively failed blind gate

## Result

EXP-123 fails from clean commit `a23770a` after `180.91 s`, so no branch label
is assigned and the sampled bracket remains `[0.147,0.149]`.

The failure is structured:

- all six runs with a 300-time-unit horizon return three branches in all 90
  `y` variants;
- in their `z` projections, all 72 variants at 30--80 bins return three;
- their 18 coarse 20-bin `z` cells contain three resolved-two votes and 15
  bootstrap-unstable cells;
- the 360-unit later-conditioned survivor subset returns two branches in all
  15 variants of both coordinates.

Support and numerics do not explain the split. The weakest run retains 200
survivors and 1737 pairs, survivor fractions agree within `0.00403`, the stable
cycle remains period 4, no integration fails, and every DOP853/Hermite audit
passes.

## Interpretation

The sprinkler retains midpoint crossings only from trajectories that survive
to the final horizon. Thus the 300- and 360-unit runs sample differently
conditioned subsets. At `a=0.148`, the additional branch is prominent among
300-unit survivors but absent among the smaller 360-unit survivor set. A
plausible explanation at this stage was that the third-branch region had a
shorter escape lifetime and was filtered out as conditioning deepened.

This is not evidence for two coexisting attractors and it is not yet a
topology label for the asymptotic chaotic saddle. It shows that finite-horizon
sprinkler topology itself must converge with escape-lifetime conditioning near
the transition. The next test must use nested horizons beyond 360 with new
ensembles and require stable branch count and critical geometry.

## Later resolution

EXP-127 rejects the shorter-mean-lifetime explanation. On three untouched
ensembles, the extra branch instead has roughly 30 more restricted-mean
residual lifetime units than the pooled core. Its capture is delayed but
bounded: all assigned trajectories survive 60 residual units and none survives
180, while the core includes both much earlier captures and a small tail beyond
270. This bounded tail, rather than faster mean escape, explains the 300/360
conditioning split.

Raw receipt SHA-256:
`73f7d6be60afcc70cb72f902f4b48063e647bff2d22d01a5f3be1c551cf1f3d6`.
