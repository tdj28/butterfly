# DEC-006 — Use perturbation-stable critical points and statistical saddle convergence

Status: accepted prospectively after the retained EXP-110 failure

## Context

EXP-110 exposes the shallow added maximum at the published `a=0.149` saddle
control, but its preregistered global prominence of 3 percent removes that
feature. It also shows that individual finite-time capture labels diverge
between fixed-step RK4 and DOP853 after dozens of chaotic returns.

Neither issue licenses relabeling EXP-110. They identify better observables for
a new prospective experiment.

## Decision

For shallow return-map branches, use a low numerical prominence floor only as
an initial candidate filter. Qualify a critical-point count by requiring it to
survive a declared matrix of bin counts and spline smoothing values, bootstrap
resampling within every matrix cell, both nondegenerate section coordinates,
and bounded critical-location drift. The resulting location ranges are
numerical-sensitivity intervals, not statistical confidence intervals.

For chaotic-saddle integration, separate two questions:

- Short-horizon numerical correctness is tested pointwise against DOP853 before
  exponential trajectory separation dominates.
- Long-horizon saddle convergence is tested statistically through survivor
  fractions at frozen checkpoints, branch topology, invariant-domain coverage,
  graph-likeness, and critical-location stability across step, conditioning
  horizon, grid phase, and grid resolution.

EXP-111 freezes these gates. It must recover two branches at `a=0.118` and
three at `a=0.149` in every run and coordinate. Its baseline, half-step,
later-conditioning, shifted-grid, and coarser shifted-grid ensembles are all
evaluated, not selected after plotting.

## Supersession boundary

This decision prospectively supersedes DEC-005's requirement for pointwise
long-horizon fixed-step/DOP853 capture identity and its analogous proposed GPU
identity gate. It does not change EXP-110's failed status. The repeated-cycle
capture definition, within-trajectory pairing, final-survivor conditioning,
and prohibition on retrospective rescue remain in force.

CPU-to-GPU qualification must likewise compare short-horizon trajectories and
long-horizon ensemble distributions and topology. It may additionally compare
same-kernel labels as a debugging diagnostic, but label identity is not an
invariant scientific acceptance criterion for chaotic trajectories.
