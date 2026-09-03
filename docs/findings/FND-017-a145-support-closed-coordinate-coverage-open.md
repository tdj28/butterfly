# FND-017 — `a=0.145` support is closed; fixed-width `z` coverage remains open

Status: strong partial result from a prospectively failed full gate

## Result

EXP-120 increases every corresponding EXP-117 ensemble by a factor of eight,
using 32,768, 65,536, and 131,072 section seeds. The full experiment still
fails, but not for lack of trajectories:

- the smallest later-conditioned run has 323 final survivors and 2726 pairs;
- the largest run has 1962 survivors and 15,940 pairs;
- no trajectory fails numerically;
- maximum survivor-fraction drift is `0.001282`;
- all DOP853/Hermite audits remain orders of magnitude inside tolerance.

## Coordinate diagnosis

Every one of 105 `y` oracle cells resolves as two-branch with full variant
consensus. Maximum across-run critical span is `0.01455`.

In `z`, 84 of 105 cells resolve as two. The remaining 21 are exactly the three
80-bin variants in each of seven runs. Every one fails only the fixed-width
minimum-domain-coverage gate (`0.675` or `0.6875` versus `0.7`) and has one
nominal critical point, hence a nominal two-branch relation. Their critical
locations lie inside the interval from the resolved variants. No `z` cell
returns three, fails graph-likeness, or exhibits a different critical geometry.

This means sample scarcity is no longer an adequate diagnosis. The last gate
is how a coordinate with intrinsically gapped projected support should be
audited at increasingly fine equal-width bins. Simply adding more trajectories
does not populate bins outside the invariant projection.

## Implications

The evidence strongly favors a two-branch saddle at `a=0.145` and therefore a
TBA crossing inside `[0.145,0.149]`, but EXP-120 cannot claim that bracket under
its full two-coordinate/full-variant rule. The failure is valuable: it prevents
a primary-coordinate result from being silently promoted while its
cross-coordinate support assumption is false.

The next prospective gate must distinguish an unresolved coverage censor from
a contradictory topology. It should require new independent ensembles, at
least 12 fully resolved variants per coordinate, no noncoverage failure, one
nominal critical point in every coverage-censored variant, and stable critical
locations including the censored nominal points. It must be tested on the
published two/three controls as well as `a=0.145` before use in continuation.

Raw receipt SHA-256:
`e00d40ab509b1f3cffeb1c20497686a451aa4300986e6d171a9e83226083e3a4`.
