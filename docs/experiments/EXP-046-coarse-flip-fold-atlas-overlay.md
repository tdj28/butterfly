# EXP-046 — Coarse independent flip-fold/atlas overlay

Status: executed; failed
Manifest: `experiments/manifests/EXP-046-coarse-flip-fold-atlas-overlay.json`
Claim target: first independent alignment screen between the flip fold and raster window geometry

## Hypothesis and method

The EXP-045 fold line was derived entirely from corrected periodic orbits. The
earlier EXP-021 atlas was generated independently from one initial condition
using finite-time recurrence. Invert the EXP-045 descriptive fold fit at the
six pre-existing atlas frames `b=0.16,0.18,...,0.26` and compare each predicted
`(a,c)` coordinate with period-5 and period-10 pixels.

Measure distances in native raster-cell units (`da=0.0025`, `dc=0.1`) to the
nearest period-5 pixel, period-10 pixel, and direct 8-neighbor period-5/10 edge.
Produce fixed-scale local crops with the predictions overlaid.

## Acceptance and limits

Within five grid-cell units of the prediction, at least four of six frames must
contain both periods 5 and 10, and at least three must contain a direct
period-5/10 adjacency. Every frame hash is verified against EXP-021 before use.

Passing is a coarse independent alignment screen, not proof that the fold line
causes or globally bounds the shrimp. Failure is also informative: the atlas
may be too coarse/finite-time, the single basin may miss the child, or the
orbit-defined fold may not coincide with the visible raster caustic. A targeted
fine scan is required to distinguish those cases.

## Result and diagnostic

The clean run at commit `9c651f27e25eaa46fef6dc4206c1fb3e82badf3a`
failed decisively: zero of six frames contained both periods 5 and 10 within
the frozen five-cell radius, and zero contained a nearby direct 5/10 edge.
Nearest period-5 distances were `6.64`–`7.32` cells and period-10 distances
`7.22`–`8.59` cells. The failure is systematic, not a marginal threshold miss.

Post-result inspection of the already generated crops revealed a stronger
alternative: every prediction lies in a period-3/period-6 band. The nearest
pixel is period 6 in five frames and period 3 in one; small neighborhoods are
dominated by periods 3 and 6. This observation was not part of the frozen gate
and is therefore a hypothesis for EXP-047, not a repaired EXP-046 result.

The complete receipt SHA-256 is
`3f5340ffd1e223d0b8d6ae3c824d922d9ca35c185a3e24846db95d56a3955e2f`.
The overlay figure is
`artifacts/EXP-046/EXP-046-coarse-flip-fold-atlas-overlay.png` (SHA-256
`f2ae5296354d4537d0af4e54602fa99b7984f95d27ad6ca16be7e7da0a23f23c`).

## Decision

Retain the failed 5/10 alignment claim. Before spending on a finer raster,
directly audit the Poincare recurrence identity of the corrected parent and
child orbits. If they are period 3 and 6, the local flip geometry remains valid
but the historical “period-5 event surface” label records an earlier family
switch and must be corrected throughout the project.
