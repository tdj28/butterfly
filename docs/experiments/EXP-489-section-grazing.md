# EXP-489: is the failed left-region event a section tangency?

Prospective exploratory mechanism test, 2026-09-08; no paid review. This is
not a retry of EXP-488's failed event-accuracy criterion. Fixed-time shooting
avoids the division by normal velocity that makes near-tangent event locations
sensitive. Both outcome-informed EXP-487 witnesses are retained, regardless of
the mixed EXP-488 result. No old gate, run or verdict is modified.

## Geometric question

For the original witness initial state q and initial tangent v, define
`h(delta,t)=n·phi_t(q+delta*v)-offset`. A simple section tangency solves
`h=0`, `h_t=n·f=0`, with nonzero unfolding `h_delta=n·w` and curvature
`h_tt=n·Jf`, where w is the integrated fixed-time variational vector.
Newton's two-by-two matrix is `[[n·w,n·f],[n·Jw,n·Jf]]`.
This Newton correction selects an initial displacement and elapsed time;
**DOP853 or Radau still integrates the ODE**. It does not replace integration.

At the historical plane, h_t=x+a*y_small. Hence tangency lies on the
half-plane gate boundary x=-a*y_small. It is not itself an accepted transverse
return. If `h_delta*h_tt != 0`, local Taylor expansion predicts a crossing
pair on exactly the side where `h_delta*delta*h_tt < 0`, and temporal pair
separation proportional to the square root of displacement. One of the two
crossings has the accepted negative orientation. These predictions, not a
smooth fitted curve through a return-time jump, are the target.

## Frozen matrix and decisions

Use the hash-bound EXP-487 states/tangents and nearest normal-velocity extremum
to its fifth accepted finest-Radau event as the initial time. Start displacement
zero, use two solvers, rtol=1e-13, atol=1e-15 and max step .001. Four root
shootings, at most eight IVPs each, no line search or alternative seed. Keep
every iterate and complete six-dimensional integration path. Stop a root
unresolved if the displacement leaves ±1e-4, time leaves ±.1 of its seed,
Newton is singular, integration fails or eight iterations are exhausted.
Residual thresholds: |h|≤1e-10 and |h_t|≤1e-9. Require |h_delta|≥1 and
|h_tt|≥1. The two solver roots must agree within displacement 1e-9, time 1e-8
and scaled state infinity error 1e-7, using scales (15,15,.01).

For **each** converged solver root, integrate all four initial displacements
relative to that root: -1e-6,-1e-7,+1e-7,+1e-6. Use the unchanged EXP-487
census, horizon 50, guard 1e-8, extremum margin 1e-10, retaining ordinary roots
and all augmented trajectories. Within a fixed ±.05 time window of the root,
require exactly two crossings (one accepted) on the predicted side and none
on the other, no uncertain extrema, residual ≤1e-8 and crossing angle ≥1e-7.
Every side must retain exactly four accepted crossings before that window;
report the next accepted event as well, linking the local pair to the selected
fifth return. The analytic control has zero preceding accepted crossings.
The separation ratio for doses 1e-6 and 1e-7 on the pair side must agree with
sqrt(10) to 5% relative error. This is a local asymptotic consistency check,
not an interval proof or an independently sampled population.

All checks for both solvers must pass for a case to support a simple numerical
grazing mechanism. Failed roots retain four explicit skipped-side records;
missing cells never imply no crossing. Both cases pass/one pass/neither pass
are positive/mixed/unresolved. A positive result identifies the selected
local itinerary boundary, not every candidate in EXP-486 and not a generating
partition or a refutation of Jones's paper.

## Controls, audit and execution

Before targets exercise both solvers on the exact normal form
`x'=1, y'=2x, z'=0`, initial `(-.5,.25+1e-5,0)`, tangent `(0,1,0)`, seed
time .498. Exact root is delta=-1e-5,t=.5; h_delta=1,h_tt=2. All four sides
must reproduce the predicted hidden pair/no-pair and square-root scaling.
Control horizon is 1, otherwise use the actual solver settings. Synthetic
tests check Jacobian finite differences, incorrect counts, tangency uncertainty,
search-box failure and missing arms. Tests and local source audit precede
the pushed exact source freeze; execute immediately once green.

The read-only same-agent audit reconstructs all cases/solvers/doses, checks
raw endpoint identities, separately recomputes the Rössler residual and
Newton matrix from retained state/tangent data, checks Newton update arithmetic,
replays side counts and ratio decisions, and verifies full input/source/output
hashes and consumed marker. It is not independent peer review or reintegration.
One attempt, ≤48 target IVPs (32 root +16 side), ≤1,800 seconds, ≤512 MiB;
no remote compute, paid review or external upload. Any needed new paid service
or materially expanded scientific target goes to the human, not an implicit
budget escalation. A numerical failure remains a documented failure.

Extremum-bracketed detection already exists in this repository's period-six
grazing helper. We test its relevance to the current failed geometry rather
than claim a new root-finding algorithm.
