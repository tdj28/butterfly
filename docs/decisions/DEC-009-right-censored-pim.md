# DEC-009 — Treat finite-horizon PIM lifetimes as right-censored bounds

Date: 2026-08-07
Status: adopted prospectively for EXP-115

## Context

EXP-114's strict PIM experiment rejected every lifetime that survived 256
returns because its exact escape time was unknown. That zero-censor rule was
conservative, but it also discarded precisely the long-lived points a PIM
construction seeks. The failure does not authorize treating the horizon as an
exact escape time or resolving a flat censored plateau by an arbitrary tie.

For a point that captures before the horizon, the measured capture time is
exact to the declared numerical tolerance. For a point that does not capture,
the measured survival time is only a lower bound on its escape time. Those two
observations define an order-censored PIM decision without estimating an
unobserved lifetime.

## Decision

A contiguous censored block is a certified proper-interior-maximum candidate
only when all of the following hold:

- it is strictly interior to the sampled segment;
- the immediately adjacent points on both sides capture;
- the selected censored lower bound is strictly larger than both adjacent
  exact lifetimes; and
- the resulting endpoint bracket is strictly narrower than its parent.

Boundary-touching censored blocks, integration failures, and blocks without
strict lower-bound dominance remain unresolved. Exact strict local maxima are
still allowed when the center and both neighbors are uncensored. Among all
admissible candidates, the largest observed value wins; the lowest sampled
index is the deterministic tie break. The algorithm records every certified
censored-block selection.

EXP-115 repeats the complete construction at censor horizons of 64 and 128
section returns. Both horizons must independently recover the expected branch
count at both published controls, and their combined normalized critical-point
span must not exceed `0.04`. This nested-horizon condition tests whether the
topology depends on the arbitrary censor ceiling.

## Scope

This is a finite-horizon, order-certified numerical rule. It is not a proof
that a censored point lies forever on the stable set, nor does it convert the
PIM trajectory into a uniformly hyperbolic invariant-set proof. Its purpose is
to preserve the logically valid ordering information in censored escape data
without imputing values that were not observed.
