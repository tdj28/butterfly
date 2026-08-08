# EXP-117 — Prospective saddle-defined path through period-4 cells

Status: preregistered; not executed

## Question

Does the qualified finite-time chaotic-saddle construction produce an ordered
two-to-three topology path inside the stable period-4 cells hidden from the
attractor-only EXP-109 scan?

## Frozen path and blind labels

At `b=0.2,c=20`, evaluate `a=0.118,0.120,0.140,0.145,0.149`. EXP-109
independently classified every attracting orbit as period 4. The published
Figure 2 controls retain their expected labels: two branches at `a=0.118` and
three at `a=0.149`. The three interior labels are deliberately absent from the
manifest and must be discovered by the frozen oracle.

This is the first prospective use of the qualified saddle sampler away from
its two training controls. It is a path test, not a fitted TBA curve: no
interpolation or boundary location is permitted.

## Frozen construction

Each of the five cells repeats the complete EXP-112 construction unchanged:

- independent adaptive-DOP853 recovery of the stable period-4 cycle;
- seven scrambled/nested/step/horizon sprinkler ensembles;
- middle-time pairs formed only within final-survivor trajectories;
- both `y` and `z` section coordinates;
- 15 branch-oracle variants with 50 bootstrap refits each;
- survivor-fraction, within/across-run critical-drift, minimum-support, and
  short-horizon DOP853/Hermite parity gates.

## Acceptance

Every run and coordinate at a cell must resolve to one common allowed count,
two or three, without inspecting neighboring cells. The published endpoint
controls must reproduce. Ordered by `a`, the five discovered counts must be
nondecreasing, contain both two and three, and have exactly one transition.
All EXP-112 numerical thresholds remain unchanged.

Passing will yield a held-out saddle-defined transition bracket among these
five period-4 samples. It will not establish a continuous codimension-one TBA
curve, identify the crossing between samples, prove infinite-time invariance,
or justify extrapolation away from `c=20,b=0.2`.

The immutable manifest is
`experiments/manifests/EXP-117-sprinkler-saddle-a-path.json`.
