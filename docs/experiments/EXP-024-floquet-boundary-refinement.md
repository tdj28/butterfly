# EXP-024 — Refined Floquet stability boundaries in b

Status: executed; three period-doubling refinements passed; +1 gate failed
Manifest: `experiments/manifests/EXP-024-floquet-boundary-refinement.json`
Claim target: P1-005 boundary seeds

## Purpose and method

Refine the four signed real-multiplier crossings bracketed by EXP-023. At each
midpoint in `b`, phase-conditioned shooting corrects the flow orbit and full
variational integration recomputes the nontrivial multiplier. Signed bisection
targets `-1` for three period-doubling candidates and `+1` for one saddle-node
candidate.

The manifest binds the exact EXP-023 receipt hash. It freezes the four coarse
brackets, DOP853 tolerances, a `1e-9` stopping width, and at most 30 iterations.
Every result must finish with bracket width `<=1e-8`, best signed multiplier
residual `<=1e-6`, and orbit closure `<=1e-9`.

## Limits

This is a scalar boundary solve along a fixed-`(a,c)` orbit branch. It provides
accurate seeds and types for codimension-one continuation but does not yet
continue those boundaries in `(a,b,c)`, prove genericity, or survive a branch
fold by construction.

## Result

The clean run at commit `1715c1e` refined every numerical `b` bracket to about
`5.96e-10`, but the overall gate correctly failed.

The three `-1` crossings passed:

- period-3 period-doubling: `b = 0.17682798296`, best multiplier residual
  `3.04e-8`, closure `5.97e-14`;
- lower period-5 period-doubling: `b = 0.14431134194`, residual `2.89e-8`,
  closure `2.34e-14`; and
- middle period-5 period-doubling: `b = 0.18346759051`, residual `5.17e-9`,
  closure `1.37e-13`.

The period-5 `+1` candidate failed. Scalar bisection narrowed around
`b=0.27809081823`, but corrected shooting alternated between branches and the
best stored nontrivial multiplier was `1.52999`, leaving residual `0.52999`.
A small parameter bracket is therefore not evidence of a solved saddle-node.
That number must not be cited as a boundary location.

The receipt SHA-256 is
`e9d3250cd368c8110b61dc78ed52d673e1ef28c2e0ae4dfcaaaff379fc2e9ab8`.

## Decision

Promote the three period-doubling values as refined numerical boundary seeds,
not yet continued curves. Reject the scalar `+1` refinement and route it to
pseudo-arclength/coupled bifurcation treatment. The failed gate demonstrates
why natural parameter continuation alone is inadequate near the candidate
fold or branch interaction.
