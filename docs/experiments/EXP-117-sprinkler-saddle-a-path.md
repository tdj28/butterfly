# EXP-117 — Prospective saddle-defined path through period-4 cells

Status: executed; failed complete gate with one qualified held-out saddle cell

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

## Result

The clean run at `8cb8bfa` completed in `759.27 s` and failed the full ordered
path gate. The observed robust counts are `2,2,2,unresolved,3` at
`a=0.118,0.120,0.140,0.145,0.149`.

The blind `a=0.140` case passes completely: all seven ensembles and both
coordinates return two branches, all 210 oracle variants agree, the smallest
run supplies 438 final survivors and 3697 pairs, and maximum across-run
critical drift is `0.013925`. With the passed three-branch right control, this
narrows the resolved saddle bracket to `[0.140,0.149]`.

The `a=0.145` case is support-unresolved. Final survivors range from 33 to 231
and pairs from 284 to 1872. Of 90 variants attempted on the three runs with at
least 1000 pairs, 72 resolve as two, none as three, and 18 fail coverage or
bootstrap stability. This is not promoted to a label.

The `a=0.120` topology itself is unanimous--210/210 variants return two--but
the case fails its cycle-reference gate because 2000 time units are too short
for the declared repeated-block test. A post-result 3000-unit diagnostic finds
period 4 and matches the four cycle states used for capture to `1.06e-9` in the
scaled metric. EXP-117 remains failed. Raw receipt SHA-256:
`893c0a6d4983b3af5b59ce4f296d75eb174f65f3dd655a25150e356faed8da0f`.
