# EXP-024 — Refined Floquet stability boundaries in b

Status: preregistered; pending clean local execution
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
