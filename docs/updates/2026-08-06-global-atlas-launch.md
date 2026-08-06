# Global-atlas launch

Date: 2026-08-06
Status: implementation and preregistration checkpoint

## Scientific decision

The Jones methodology is being extended from a primary-hub raster into a
bounded superstructure atlas. The target explanation has four layers:

1. stable periodic families and their saddle-node/period-doubling boundaries;
2. hub and branch-addition curves in return-map topology;
3. chaotic attractors versus nonattracting chaotic saddles and capture times;
4. global organization by saddle-focus/homoclinic geometry and reinjection.

No finite computation can cover the literal unbounded `(a,c)` plane. Each atlas
release will state its closed search domain. Boundary activity, newly discovered
families per added area, and continuation curves determine whether the domain
must expand.

## New execution item

EXP-013 is frozen as the first high-`a` reconnaissance. It covers
`a in [0.22,0.36]` and `c in [5,15]` at 1,189 points, including the historical
high-`a` Quickstart rectangle. A deterministic component extractor converts
periodic pixels into candidates for refinement and continuation without
mistaking raster adjacency for proof of connectivity.

## Compute authorization

The owner authorized up to USD 100 and invited a larger budget if justified.
The project treats USD 100 as a cumulative hard ceiling, not a target to spend.
Runpod use begins only after an exact production-observable parity test and must
record live price, runtime, estimated and actual spend, artifact hashes, and
verified teardown.

## Next evidence checkpoint

Run EXP-013 locally, summarize every component and near-recurrence, then select
spatially separated high-`a` candidates for convergence and basin qualification.
In parallel in the implementation sequence, upgrade the CUDA path from endpoint
parity to Poincare-crossing and period-classification parity.
