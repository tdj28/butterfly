# Global-atlas launch

Date: 2026-08-06
Status: first reconnaissance complete; qualification launched

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

## EXP-013 result

The clean `29 x 41` scan completed all 1,189 points with 82 periodic detections,
1,107 unresolved points, and no numerical failures. It produced 52 coarse
same-period components spanning periods 1, 2, 3, 4, 5, 6, 8, and 12. Eight
components touch a rectangle boundary. The first provenance-bound `(a,c)`
figure exposes a diagonal low-period band and separated islands at higher `a`.

EXP-014 now binds the exact aggregate hash and freezes 39 targets across the
diagonal, isolated high-`a` detections, boundaries, and top unresolved
near-recurrences. Its stronger tests use two initial conditions, longer
transients, and full Lyapunov spectra.

EXP-014 qualified 26 consensus-periodic targets and sent four finite-time
multistability labels to EXP-015. Long-transient checkpoints rejected three of
those and confirmed common capture at a fourth boundary case. One candidate at
`(a,b,c)=(0.245,0.2,5.75)` retained distinct period-12 and period-3 endpoints
through transient 19,200. EXP-016 now asks whether both cycles are transversely
stable under independent Floquet diagnostics.

EXP-016 passed both Floquet gates. EXP-017 then sampled a declared `21 x 21`
initial-condition plane: all 441 seeds converged, with 282 period-12 and 159
period-3 outcomes. Nearly half of four-neighbor edges switch basin at this
coarse scale. The next basin task is scale-dependent uncertainty measurement,
not a premature fractal/riddled label.

## EXP-018 GPU qualification

The owner authorized tracked-file-only frozen source export to task-owned
Runpod hosts. The first complete A40 run failed exact period parity and exposed
a numerical weakness: linear section interpolation reduced an RK4 trajectory
to second-order crossing accuracy. We retained the strict recurrence tolerance
and replaced the event calculation with cubic-Hermite dense output plus bounded
Newton refinement.

The corrected NVIDIA L4 run passed every period-1/2/3/7/12 control at
`dt=0.005` and `dt=0.0025`; maximum cyclic orbit errors were `4.633e-6` and
`2.922e-7`, respectively. A 32,768-trajectory raw benchmark sustained 717.1
million Float64 state-steps/second. The final receipt and archive hashes matched
across the local and remote copies, and all pods were terminated. The periodic
Poincare GPU path is now qualified for the next basin-scaling and multi-`b`
atlas experiments, but not for chaotic identity or Lyapunov claims.

## Basin scaling and multi-b atlas

EXP-019 resolved all 57,344 period-3/period-12 uncertainty pairs but showed
coarse-scale saturation. Its disclosed four-smallest-scale fit suggested a
fractal boundary. EXP-020 then prospectively froze seven smaller scales and new
seeds: 57,342/57,344 pairs resolved, uncertain fractions fell from `0.3236` to
`0.05657`, and the all-scale fit gave `alpha=0.4264`, pair-bootstrap interval
`[0.4094,0.4442]`, and `R^2=0.9976`. This supports a fractal, non-riddled basin
boundary in the declared plane; the numerical dimension remains provisional.

EXP-021 completed 296,241 `(a,b,c)` points across eleven `b` frames from 0.10
through 0.30. All frames passed, with a single numerical-failure pixel in the
entire slab. The fixed-color contact sheet and GIF show coherent motion of the
low-period band, nested shells, organizing spine, and higher-period windows.
The Jones section/recurrence method therefore scales to bounded 3-D atlas
reconnaissance. Same-period component tracking and true continuation are next;
the raster is not itself a bifurcation explanation.
