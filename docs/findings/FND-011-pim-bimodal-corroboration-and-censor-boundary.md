# FND-011 — PIM independently corroborates the bimodal saddle and exposes a censor boundary

Status: qualified partial result from a prospectively failed experiment

## Result

EXP-114 fails its complete two-control gate. All five frozen lines at the
unimodal `a=0.118` control encounter at least one candidate that remains
uncaptured through the declared 256-return ceiling, so no unimodal PIM
straddle is admitted. Two of five lines at the bimodal `a=0.149` control hit
the same ceiling. There are zero adaptive integration failures.

The other three bimodal lines complete strict DOP853 PIM constructions. Each
keeps its normalized endpoint bracket below `1e-7` for 1200 returns and retains
1000 middle points after burn-in. Their pooled 2997 consecutive pairs recover
three branches in both `y` and `z`; all 15 oracle variants agree. The maximum
within-PIM critical spans are `0.01252` and `0.01123`, and the combined
EXP-112/PIM spans are `0.01263` and `0.01122`, all far below the frozen gates.

## Interpretation

This is genuine independent corroboration of the published bimodal chaotic
saddle. It uses a single-trajectory Nusse-Yorke restraint construction and
adaptive DOP853 return map, not the scrambled survivor ensemble or fixed-step
RK4 used by EXP-112/113. Agreement in branch count and critical locations is
therefore stronger than another backend-parity test.

It is not yet the required two-control corroboration. The absence of an
admitted unimodal straddle does not contradict the two-branch saddle: the PIM
search repeatedly found points with lifetime lower bounds beyond 256 returns,
which the frozen rule prohibited even though long survival is the target
signal.

## Diagnosed replacement

The zero-censor rule is internally overstrict for dynamic restraint. A
censored interior candidate can still certify a PIM ordering when its lifetime
lower bound exceeds the exactly observed lifetimes of bounding candidates.
The successor must treat censoring as interval information:

- exact capture gives a point lifetime;
- censoring gives a lower bound, not an invalid value;
- a contiguous censored interior block bracketed by captured points defines a
  certified proper-interior-maximum segment;
- a block touching a segment boundary or lacking strictly lower captured
  endpoints remains unresolved; and
- nested censor horizons must reproduce accepted straddles before topology is
  classified.

This change is a prospective treatment of right-censored escape data, not a
permission to relabel EXP-114 as passed.
