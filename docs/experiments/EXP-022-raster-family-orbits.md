# EXP-022 — Corrected cycles along persistent cross-b raster families

Status: preregistered; pending clean local execution
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
