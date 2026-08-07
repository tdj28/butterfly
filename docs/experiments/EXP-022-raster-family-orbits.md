# EXP-022 — Corrected cycles along persistent cross-b raster families

Status: executed; all 22 corrected cycles passed
Manifest: `experiments/manifests/EXP-022-raster-family-orbits.json`
Claim target: cross-`b` persistence beneath EXP-021

## Purpose

Test whether two all-frame EXP-021 raster components contain genuine stable
periodic cycles at representative points in every `b` frame. This replaces
pixel color with phase-conditioned flow shooting, exact variational Jacobians,
and Floquet multipliers.

## Frozen families and method

The selected candidates are component 803 (period 3, low `c`) and component
2208 (period 5, middle `c`). Each contributes one actual periodic raster pixel
nearest its component centroid in all eleven frames. For each point, DOP853
recomputes the attractor after transient 2,400, verifies the recurrence period,
and seeds a four-variable shooting solve for state and flow period.

The corrector solves three flow-closure equations plus a normalized hyperplane
phase condition. Its Jacobian uses the integrated state-transition matrix and
the terminal vector field. The corrected orbit is reintegrated with the full
variational equations for Floquet multipliers.

Every point must retain its expected recurrence period, correct to flow closure
`<=1e-9` and phase residual `<=1e-10`, recover the neutral multiplier within
`1e-6`, and have all nontrivial multipliers strictly inside the unit circle.

## Limits

Passing would confirm stable periodic cycles along these representative moving
paths and materially strengthen the interpretation of cross-`b` persistence.
It is not pseudo-arclength continuation of an orbit or of its saddle-node and
period-doubling boundaries; those remain the next geometric layer.

## Result

The clean run at commit `45e8eaff2d25efdd808a1305bb079096652f4844`
passed all 22 representative points in 50.97 seconds. Every raster point
reproduced its expected recurrence period, and every shooting solve converged
in one or two evaluations.

For the period-3 path:

- flow closure ranged from `7.27e-15` to `4.02e-12`;
- neutral-multiplier error ranged from `7.69e-12` to `4.88e-11`;
- maximum transverse multiplier modulus ranged from `0.0253` to `0.4148`; and
- flow period ranged from `19.6602` to `19.9337`.

For the period-5 path:

- flow closure ranged from `9.95e-15` to `9.53e-12`;
- neutral-multiplier error ranged from `2.33e-11` to `1.31e-10`;
- maximum transverse multiplier modulus ranged from `0.0509` to `0.6430`; and
- flow period ranged from `32.1474` to `32.7172`.

The receipt SHA-256 is
`bc0f1501e96f8f5cf1a08173ea392c4abcb4f5f717de2b8f60e9af23f5679d28`.

## Decision

These two moving structures are no longer supported only by raster adjacency:
they contain strongly closed, transversely stable period-3 and period-5 cycles
at every sampled `b`. This is orbit-level evidence for persistent families
within `b in [0.1,0.3]`. Because `(a,c)` also moves along each representative
path, the result is not yet a unique continuation curve or proof of hub drift.
Pseudo-arclength continuation of the orbit and its bifurcation boundaries is
the next required step.
