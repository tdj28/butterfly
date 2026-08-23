# EXP-318 freezes a high-precision seventh-birth decision

The eighth-birth methodology exposed a representation-scale problem that also
explains why EXP-299 stopped short: DOP853 and Radau agree that the primitive
period-1536 daughter is strongly stable, but disagree about which side of
`-1` contains the nearly neutral period-768 parent at one shared Float64
coordinate.

EXP-318 avoids classifying that `3e-5` solver split. It binds the passed
8,192-step RK4 3/8 augmented event and the failed-but-qualified EXP-299 source,
then recomputes the parent spectrum using two independent fourth-order
tableaux in 50-digit arithmetic with three resolution levels. The event-side,
convergence, cross-tableau, signal/error, orbit, neutral, cyclic, and
characteristic gates are frozen before execution. Either stability-exchange
direction may pass; a same-side or unresolved result fails.

This is the shortest decisive successor for the only unresolved birth among
the eight exact returning-arm flip events. It uses local CPU arithmetic and
incurs no RunPod cost.

## Result

The run completes in 517.29 seconds and preserves a scientifically useful
failure. Both tableaux place the parent on the stable side, with flip residuals
`+6.4226805e-6/+6.4226424e-6`; the largest empirical arithmetic uncertainty is
`7.7932e-9`, so the side decision clears a factor `824.1`. Every numerical
gate passes, but EXP-299's child is also stable. The required exchange is
therefore absent and the receipt fails without relaxation.

This removes the former solver ambiguity but not the seventh-birth question.
The next experiment must recover the immediate doubled branch in the same
high-precision event representation and distinguish a local subcritical
daughter from a later stable sheet, fold, or restabilization.

## EXP-319 frozen

The successor now uses one shared 50-digit RK4 3/8 discrete map for both the
passed 4,096-step event and its doubled child. A five-variable cyclic Newton
reduction makes a 6,146-variable dense solve unnecessary. Both tangent signs
and two predictor scales are frozen, with quadratic-opening, side,
primitivity, period, Floquet, and stability gates. A pass nominates the local
direction at one resolution; an 8,192-step or independent-tableau replication
remains mandatory before promotion.

## EXP-319 passes; EXP-320 frozen

All four same-map children pass. They are primitive and stable, open toward
lower `a` under both tangent signs, and yield a parameter-amplitude exponent
`2.000728`. Final matching is below `2.84e-21`; child moduli range from
`0.92877` to `0.98228`. This nominates a supercritical seventh birth and
identifies the EXP-299 stable higher-`a` orbit as something other than the
immediate local daughter.

EXP-320 now binds the raw 1.39 MB receipt and repeats the unchanged bilateral,
two-amplitude experiment at 8,192 steps per segment. A pass is required before
the ledger or manuscript promotes the seventh-birth direction.

## EXP-320 passes; seventh birth promoted

The 8,192-step replication passes every unchanged gate. Event-relative
displacement, half-node amplitude, and child modulus reproduce the 4,096-step
results within `9.08e-10`, `9.27e-13`, and `1.41e-10` relative. The repeated
opening exponent is `2.000728180631`; all four children remain stable and open
toward lower `a`.

FND-105 therefore qualifies the seventh birth as locally supercritical. The
returning-arm ledger now contains eight exact events, seven supercritical
births, and a subcritical eighth birth. EXP-318 remains a valid stable/stable
failure and exposes an additional higher-`a` period-1536 sheet whose fold,
restabilization, or connectivity must now be traced.

## EXP-321 frozen

EXP-321 will take six same-map, 50-digit pseudo-arclength steps from the
immediate daughter toward the higher-amplitude regime. It preserves the
4,096-step RK4 3/8 map and records parameter direction, primitive amplitude,
Floquet stability, fold nominations, and phase-invariant distance to the
EXP-299 stable candidate. The pass criteria require a resolved branch segment,
not a fold or target match, so the topology remains outcome-neutral.
