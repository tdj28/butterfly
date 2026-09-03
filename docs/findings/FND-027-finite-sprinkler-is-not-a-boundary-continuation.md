# FND-027 — Finite sprinklers do not continue the saddle boundary

Status: qualified negative result from prospective EXP-130

## Finding

A large, deeply conditioned Float64 GPU sprinkler remains reliable away from
the branch-opening boundary but becomes oracle-dependent at the two local
PIM-qualified boundary controls. Increasing survivor power is therefore not a
valid substitute for constructing the nonattracting invariant set.

EXP-130 ran 36 ensembles without an integration failure or crossing-buffer
saturation. Every run retained at least 121 survivors and 1002 return pairs.
The published `a=0.118` and `a=0.149` controls pass at both fresh Sobol seeds
and at half step. In contrast, the PIM-qualified `a=0.148125` two-branch and
`a=0.14825` three-branch controls are unresolved in every profile: branch
counts vary across the frozen oracle family and lower-support slope fits cross
zero or fall below the frozen magnitude floor.

That contrast localizes the problem to invariant-set access near the boundary,
not RK4 speed, event interpolation, raw sample count, or numerical failure.
The same finite cloud mixes support that adaptive PIM access separates. This
is a negative result for sprinkler-based continuation and positive evidence
for retaining PIM as the claim-bearing method.

## Transverse information retained without promoting it to a claim

The failed pilot still supplies prospectively selected PIM endpoints:

- at `c=19.8`, `a=0.145` is the lower/two candidate and `a=0.148` is the
  upper/three candidate; the upper point has positive slope in both
  coordinates, both seeds, and the half-step repeat, while its branch count is
  deliberately unresolved;
- at `c=19.9`, `a=0.145` is the lower/two candidate and `a=0.150` is a fully
  resolved two-seed three-branch endpoint; and
- `c=19.8, a=0.149` fails the high-accuracy stable period-4 gate despite its
  coarse-atlas recurrence label, so it cannot be used as a regular-window
  saddle control.

These are frozen predictions for adaptive-DOP853 PIM validation, not observed
TBA points. EXP-130 does not establish either transverse bracket.

Tracked receipt: `docs/experiments/receipts/EXP-130.json`.
