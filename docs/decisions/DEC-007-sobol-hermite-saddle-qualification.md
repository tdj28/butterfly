# DEC-007 — Remove lattice aliasing and linear event error from saddle qualification

Status: accepted prospectively after the retained EXP-111 failure

## Context

EXP-111 qualifies its entire 300-cell topology component but misses two
non-topology gates. Regular-grid phase and resolution move survivor fractions
by up to `0.07962`, and one linearly interpolated crossing time misses the
short-horizon DOP853 tolerance.

## Decision

Replace regular section lattices in the convergence gate with scrambled Sobol
ensembles. Use three independent scrambles at 8192 samples and one nested
scramble at 4096, 8192, and 16384 samples. Retain the half-step and later-
conditioning runs on the baseline scramble. Compare survival fractions at the
same frozen checkpoints and retain the existing absolute `0.05` gate.

Replace linear within-step section interpolation with a cubic Hermite
interpolant built from the RK4 step endpoints and their vector fields. Locate
the negative-to-positive root by bisection on that interpolant. This does not
replace RK4 as the ensemble integrator and is unrelated to periodic-orbit
Newton correction.

EXP-112 repeats the complete two-control, two-coordinate, 15-variant topology
gate along with the short-horizon DOP853 audit. The prior `a=0.11` calibration
after implementing Hermite gives maximum scaled state error `2.11e-5` and time
error `1.05e-5`, within the unchanged `0.001` and `2e-5` limits.

## Consequences

A pass would qualify the finite-time CPU sprinkler sampler at the two published
controls. It would not make the survival curve an invariant escape-rate
estimate, establish the TBA curve, or replace an independent PIM/stagger-and-
step saddle reconstruction. GPU parity remains subsequent.

## Validation outcome

EXP-112 passes all gates. Across 14 ensembles, maximum survivor-fraction drift
is `0.01135`, maximum normalized critical drift is `0.01485`, and all 420
topology cells return the expected counts. Hermite/DOP853 errors remain below
`2.46e-6` in scaled state and `3.16e-6` in time. The finite-time CPU sampler is
therefore qualified at the two controls under this decision's stated boundary.
