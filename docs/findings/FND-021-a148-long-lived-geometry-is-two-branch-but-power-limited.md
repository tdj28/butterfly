# FND-021 — Long-lived `a=0.148` geometry is two-branch but power-limited

Status: retained negative qualification result with a positive mechanistic
constraint

## Finding

EXP-124 fails its preregistered requirement that all eight runs and both
coordinates choose one common branch count. It therefore does not label
`a=0.148` or narrow `[0.147,0.149]`.

The failure is not evidence for a three-branch long-lived saddle. No run or
variant selects three. Twelve of 16 run--coordinate decisions select two and
228 of 240 oracle variants resolve as two. The 12 remaining cells are exactly
the 80-bin variants in four decisions with low effective survivor power. They
are bootstrap-unstable, not contradictory.

## Evidence pattern

- The 360-unit and baseline 420-unit runs select two in `y` and `z`.
- Two independent 420-unit Sobol scrambles select two in both coordinates.
- The `2^17` 420-unit run selects two in both coordinates with 607 final
  survivors.
- The 480-unit run retains 121 survivors and 1061 pairs. Its 20--60-bin cells
  resolve as two, while both coordinates' 80-bin cells are bootstrap-unstable.
- The half-step and `2^15` 420-unit runs select two in `z`; only their 80-bin
  `y` cells are unstable. Their final survivor counts are 307 and 164.
- Every period, survival, integration, and DOP853/Hermite comparison gate
  passes.

## Implication

EXP-123's three-branch geometry belongs to the less strongly conditioned
population. Among returns from trajectories that remain through 360--480 time
units, every resolved observation is two-branch. This was initially consistent
with a faster-escaping third-branch region of the chaotic saddle. It also shows why a
sprinkler alone cannot yet define the infinite-lifetime topology near this
boundary: survivor attrition couples the apparent branch count to statistical
power.

The next discriminating test should avoid exponential survivor depletion. A
censor-aware PIM-straddle construction at `a=0.148`, followed by branch-
conditioned escape statistics, can test the two-branch long-lived saddle
without declaring bootstrap instability to be confirmation.

EXP-127 subsequently rejects faster capture in restricted mean lifetime. It
qualifies a crossing-survival pattern instead: the extra branch delays capture
but has no residual tail past 180 units, whereas the two persistent domains
capture earlier on average while retaining rare survivors past 270. The
long-horizon two-branch result remains valid; its mechanism is now described as
bounded extra-branch residence rather than faster mean escape.

Raw receipt SHA-256:
`8328cebb89fd74c095269fb87c02b2120184d920a6e3eec883841f2cd7e10447`.
