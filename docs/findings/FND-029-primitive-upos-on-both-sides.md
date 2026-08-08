# FND-029 — Primitive UPOs are recovered on both sides of the local boundary

Status: qualified finite orbit substrate from EXP-133 through EXP-135

## Finding

Exact-flow correction of close returns from the independently qualified PIM
saddles recovers unstable periodic orbits on both sides of the `c=20` finite
two/three bracket. Proper-divisor closure and continuous phase alignment reduce
the raw shooting recoveries to defensible primitive families.

At `a=0.148`, nine accepted recoveries remain nine distinct primitive families
with section lags `3,5,7,8,12,13`. At `a=0.14825`, six accepted recoveries
reduce to two primitive families: one lag-4 family represented five times and
one lag-12 family. Two reported lag-8 recoveries are exact double traversals of
the lag-4 family, closing after half-period near `1.1e-11`; they are not counted
as new orbits. Continuous phase alignment merges the different lag-4 phases
with maximum normalized whole-orbit RMS `8.69e-7`.

Every retained EXP-133 recovery first passed exact DOP853 return-map closure,
phase-conditioned flow shooting, section-crossing identity, neutral-multiplier,
and transverse-instability gates. The weakest unstable modulus is `3.484` and
the largest corrected flow closure is `4.31e-11`.

## Mechanism consequence

This closes the finite-orbit-seed prerequisite for manifold work. It does not
identify the event that opens the third branch. The lag-12 class exists among
the recovered families on both sides and is therefore the first candidate for
identity-safe continuation across the narrow bracket. The upper lag-4 family
is a complementary test: continuing it toward the lower side will determine
whether it persists across the branch change or terminates at a distinct orbit
event.

Tracked receipts: `docs/experiments/receipts/EXP-133.json`,
`docs/experiments/receipts/EXP-134.json`, and
`docs/experiments/receipts/EXP-135.json`.
