# EXP-033 — Expanded period-5 unit-event curve across a

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-033-expanded-period5-unit-event-a-curve.json`
Claim target: bounded extension of the EXP-028/032 event curve

## Hypothesis and method

The coupled period-5 pitchfork-like event continues smoothly at fixed `c=5.1`
across the wider `a in [0.225,0.265]` interval. Use nine frozen values at
spacing `0.005`, continuing independently upward and downward from EXP-028.
Each point must solve the complete orbit/unit-eigenvector system; EXP-032's
solved rows are not used as numerical inputs.

## Acceptance and limits

All nine points are required inside the prospectively expanded
`b in [0.15,0.4]` domain. Closure, nontrivial eigen, and flow-orthogonality
residuals must be at most `1e-8`, with no adjacent `b` jump over `0.03`.

Passing establishes a bounded fixed-`c` event curve over four times EXP-032's
`a` span. It does not establish persistence of the pitchfork normal form at
every point, a two-dimensional surface under `c`, or a connection to the
return-map topology-change/TBA locus.
