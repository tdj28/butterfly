# DEC-005 — Qualify a survival-ensemble saddle sampler before GPU scaling

Status: accepted for prospective qualification

## Context

EXP-108 reproduces the published two- and three-branch return maps on chaotic
attractors. EXP-109 brackets the corresponding change on the attracting set,
but it necessarily loses the chaotic map inside stable windows. Barrio, Blesa,
and Serrano's stronger claim concerns the nonattracting chaotic saddle that
coexists with a stable period-4 orbit at `a=0.118` and `a=0.149`.

The saddle approximation must therefore be defined without selecting a long
trajectory after inspecting its return map. It must also have a transparent
CPU reference before a faster GPU implementation can be trusted.

## Decision

Use a frozen survival-ensemble (sprinkler) construction as the first numerical
saddle method:

1. Recover the coexisting stable period-4 section cycle independently with
   adaptive Float64 DOP853.
2. Seed a declared two-dimensional grid on the published oriented section.
3. Propagate every seed with deterministic vectorized Float64 RK4.
4. Declare attraction only after a declared number of consecutive section
   returns fall within a declared scaled neighborhood of the stable cycle.
5. Approximate the saddle using middle-time section crossings from trajectories
   that remain uncaptured at the final horizon.
6. Form return pairs only within a single survivor trajectory. Never join the
   last crossing of one trajectory to the first crossing of another.
7. Require both section coordinates to pass the preregistered branch oracle and
   audit selected survivor/captured labels with adaptive DOP853.

EXP-110 freezes the first grid, horizon, capture rule, oracle, and acceptance
thresholds before execution.

## Why midpoint states of final survivors

Final-time survivor states approximate the stable direction of an open system;
initial survivor states approximate its unstable preimages. States well away
from both ends suppress these conditioning biases and are the conventional
sprinkler approximation to the invariant saddle. Requiring survival to the
full horizon prevents a merely long but already captured transient from being
promoted after its shape is inspected.

This remains a finite-time approximation. Survivor decay, horizon stability,
capture-radius stability, and an independent saddle method are required before
making invariant or global claims.

## Failure semantics

An EXP-110 failure is retained as evidence and classified by the first failed
gate: stable-cycle recovery, numerical integration, insufficient survivors,
insufficient return pairs, unresolved topology, wrong branch count, or failed
precision audit. The return map may not be rescued retrospectively by changing
the grid, time window, or capture threshold.

A new manifest may test a diagnosed change prospectively. A PIM-triple or
stagger-and-step construction is an independent corroboration route, not a
post-hoc tuning fallback.

## GPU qualification rule

Passing EXP-110 qualifies only the CPU reference. A Runpod/Triton port must use
the same Float64 equations and frozen inputs, then agree on:

- capture/failure labels for a declared comparison subset;
- the survivor count at every checkpoint;
- retained midpoint return pairs to declared numerical tolerances; and
- the resolved branch count in both coordinates.

Only after this parity gate may GPU results support a parameter-plane saddle
atlas. GPU speed is not evidence of numerical equivalence.

## Consequences

This decision directly targets the central result that attracting-orbit scans
cannot see. A positive control result would reproduce the published saddle
topology at two regular-window parameters. It would not by itself establish a
topological bifurcation, a global TBA curve, or a complete explanation of the
parameter plane; those require continuation, convergence, and independent
invariant-set tests.
