# EXP-112 — Scrambled-Sobol and Hermite saddle qualification

Status: preregistered under DEC-007; not yet executed

This prospective successor retains EXP-111's topology, survival, critical-
drift, and short-horizon tolerances while changing only the two diagnosed
mechanics.

Seven ensembles are run at each published period-4 control: three independent
8192-point scrambled Sobol samples; a nested scramble at 4096, 8192, and 16384
points; half-step integration; and later survivor conditioning. Each run must
recover two branches at `a=0.118` and three at `a=0.149` in both coordinates
through all 15 oracle variants and 50 bootstraps per variant.

All common-checkpoint survivor fractions must remain within `0.05` of the
8192-point seed-112 baseline. Within-run critical-location span must be no more
than `0.03`, across-run span no more than `0.04`, and every run must remain
finite with at least 100 final survivors and 1000 within-trajectory pairs.

Cubic Hermite section roots are audited on five fixed Sobol seeds per control
against DOP853 for the first five returns. Maximum scaled section-state error
must not exceed `0.001`; maximum time error must not exceed `2e-5`.

Failure is retained by gate. Passing qualifies only the finite-time CPU
sprinkler control reconstruction; an independent saddle method and GPU parity
remain mandatory before plane-scale continuation.
