# EXP-124 — Nested conditioning horizons at `a=0.148`

Status: executed; failed the frozen all-run consensus gate

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

## Result

EXP-124 completes from clean commit `1116860` in `505.33 s` and fails. No run
or oracle variant selects three branches. Twelve of 16 blind run--coordinate
decisions select two; the other four are unassigned. Across all 240 oracle
variant cells, 228 resolve as two and the remaining 12 are the three 80-bin
variants in each unassigned decision. Those cells fail bootstrap stability at
the available rare-survivor support; none returns a contrary count.

The 360- and baseline 420-unit profiles, both independent 420-unit scrambles,
and the doubled `2^17` 420-unit profile select two in both coordinates. The
480-unit profile is unassigned in both coordinates with 121 final survivors
and 1061 pairs. The half-step and `2^15` 420-unit profiles retain 307 and 164
survivors respectively; both select two in `z` while their 80-bin `y` variants
are bootstrap-unstable. The fine 420-unit profile restores unanimous two-branch
decisions with 607 survivors.

The period-4 reference, survival, and numerical audits pass. Maximum survivor-
fraction drift is `0.00223`; maximum DOP853/Hermite scaled-state and crossing-
time errors are `2.471e-6` and `7.052e-8`. The result supports a two-branch
geometry among sufficiently long-lived returns and rejects a reappearance of
resolved three-branch geometry through 480 time units, but it does not satisfy
the preregistered finite-horizon qualification. `a=0.148` remains unlabeled and
the sampled bracket remains `[0.147,0.149]`.

Tracked compact receipt: `docs/experiments/receipts/EXP-124.json`. The raw
receipt SHA-256 is
`8328cebb89fd74c095269fb87c02b2120184d920a6e3eec883841f2cd7e10447`.
