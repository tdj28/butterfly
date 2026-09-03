# FND-014 — A held-out saddle point narrows the bracket and exposes a conditioning hole

Status: partial positive result from a prospectively failed full-path gate

## Result

EXP-117 is the first use of the qualified sprinkler method away from the two
published controls. Its complete five-cell gate fails, but one blind target
passes every frozen requirement:

- `a=0.140` has a stable period-4 attractor and a two-branch chaotic saddle in
  all seven ensembles and both coordinates;
- its smallest ensemble result retains 438 final survivors and 3697
  within-trajectory pairs;
- all 210 oracle-variant cells return two branches, maximum across-run critical
  drift is `0.013925`, and no integration or DOP853 audit fails.

Together with the independently qualified three-branch saddle at `a=0.149`,
this narrows the resolved saddle-defined bracket on the frozen `c=20,b=0.2`
path from the two controls `[0.118,0.149]` to `[0.140,0.149]`. It does not locate
the TBA inside that interval.

## Why the complete gate fails

At the blind `a=0.145` cell, survivor decay is much faster. Depending on the
ensemble, only 33--231 trajectories survive to the final horizon and only
284--1872 return pairs remain. The three runs that clear 1000 pairs each give
12 of 15 oracle variants as two-branch in both coordinates; the remaining
three variants miss the frozen invariant-domain coverage gate. Across the cell,
72 attempted variants resolve as two, none as three, and 18 remain unresolved.
This is strong directional evidence but not a branch qualification.

At `a=0.120`, all 210 oracle cells agree on two branches with strong support,
but the complete case fails because the frozen 2000-time-unit cycle reference
does not contain enough repeated blocks to classify. A post-result diagnostic
at 3000 time units classifies period 4, and its final cycle matches the cycle
actually used by EXP-117 to `1.06e-9` in the scaled capture metric. This
diagnoses the gate failure but does not retrospectively relabel EXP-117.

## New continuity question

The new saddle sequence must not yet be spliced uncritically to EXP-109's
attractor-only sequence. The qualified three-branch saddle at `a=0.149` is
followed by a two-branch aperiodic candidate at `a=0.150` in the earlier,
shorter attractor scan. That object remains nonperiodic after burn-ins through
10000 time units in a post-result recurrence diagnostic, so a simple rapid
capture explanation is not yet available. It may reflect an invariant-set
identity change, a second TBA crossing, an incomplete scalar projection, or a
finite-horizon artifact. A frozen multi-burn-in topology and Lyapunov audit at
`a=0.150` must resolve this before a single monotone path is asserted.

## Claim boundary

EXP-117 supports a new held-out saddle point and a narrower finite-sample
bracket. It does not qualify `a=0.145`, pass the five-cell ordered-path gate,
establish continuity, prove template equivalence, or explain the apparent
`0.149`/`0.150` topology reversal.

EXP-118 now resolves the immediate diagnostic priority without changing
EXP-117's status. The `a=0.150` set persists as Lyapunov-positive chaos, but its
branch label splits exactly by resolution: 20-bin variants see two while every
resolved 30--80-bin variant sees three. The apparent reversal is therefore not
qualified; FND-015 records the successor evidence and remaining convergence
gate.

Raw receipt SHA-256:
`893c0a6d4983b3af5b59ce4f296d75eb174f65f3dd655a25150e356faed8da0f`.
