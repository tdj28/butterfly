# EXP-046 — Coarse independent flip-fold/atlas overlay

Status: preregistered; pending clean execution
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
