# EXP-000 - Recovered repository audit

Experiment ID: EXP-000
Date: 2026-08-06
Purpose: determine which numerical claims from the 2012 paper are implemented
in the recovered repository.

## Result

The recovered `master` branch contains an MPI Rössler parameter-map program. It
implements the vector field, fixed-step RK4 integration, a Poincaré-section
sampler, and recurrence-based period classification through period 11.

It does not implement:

- Lyapunov exponent calculation;
- AUTO/PyCONT continuation;
- Hopf or homoclinic curve detection;
- logistic-map caustics or kneading analysis;
- return-map branch classification;
- reinjection-angle measurement;
- symbolic sequence generation;
- periodic-orbit continuation or Floquet multipliers; or
- recreation of Figures 1, 2, 4, 5, and 6.

The code hard-codes a `500 x 500` grid rather than the paper's claimed
`5000 x 5000` grid. Repository history and local branches contain newer MPI,
CUDA, and heatmap work, but no implementation of the missing analyses.

## Code-level cautions

- Worker ranks send `period` using the MPI floating-point datatype while the
  root receives it as an integer datatype.
- Parameter-grid upper endpoints are excluded.
- Section crossings are not interpolated.
- Some nonreturning trajectories can leave the section loop without a bounded
  timeout.
- The newer branch's active classifier stops at the first recurrence match,
  which can report a multiple of the fundamental period.
- No convergence, multistability, or false-classification study accompanies the
  implementation.

## Verification performed

- Inspected all tracked source and documentation on `master`.
- Inspected full Git history and all local branches.
- Compiled current and newer MPI source directly with `mpicc`; compilation
  succeeded with warnings.
- Attempted a reduced MPI diagnostic. The installed OpenMPI runtime failed
  during library initialization before the program entered its own logic, so a
  runtime classification result was not obtained in this environment.

## Interpretation

The recovered code is useful historical input and a candidate comparison
implementation. It is not a complete reproduction package and should not be
used as the numerical reference until its behavior is characterized against a
new serial implementation.

Linked claims: CLM-001, CLM-013.
