# EXP-124 — Nested conditioning horizons at `a=0.148`

Status: preregistered; not executed

## Question

Does the blind two-branch geometry seen after 360 time units persist as the
survivor conditioning horizon grows, or does the three-branch geometry return?

## Frozen design

New Sobol seeds 132--134 are conditioned through 360, 420, and 480 time units.
Each 60-unit return window remains centered at half the final horizon:
`[150,210]`, `[180,240]`, and `[210,270]`. The 420-unit profile includes step
halving, two independent scrambles, and a `2^15,2^16,2^17` sample-size ladder.
The 360- and 480-unit profiles use `2^16` states.

Every run and coordinate must blindly and uniquely select the same candidate
count under the EXP-121 rule. The original floors of 100 final survivors and
1000 pairs, all drift and survival gates, the period-4 reference, and the
DOP853/Hermite audit remain unchanged. A pass qualifies only finite-horizon
conditioning stability over 360--480. A failure remains unlabeled and does not
move `[0.147,0.149]`.

Immutable manifest:
`experiments/manifests/EXP-124-a148-conditioning-horizons.json`.
