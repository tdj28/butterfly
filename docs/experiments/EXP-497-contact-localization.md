# EXP-497: bounded localization within the qualified contact endpoint pair

Prospective exploratory successor to EXP-496, 2026-09-09. Parent outcomes inform
the selection and initial interval; this is not an independent confirmation.
No new target result has been measured for this successor.

## Eligibility and question

Retain both original parameter cases and all 26 parent candidate identities.
A case is eligible only if EXP-496 reports opposite-sign endpoints across
all four history/direction representations. This selects local-a025-c083,
a in [.21545,.21575], b=.2, c=7.212. The second case remains explicitly
ineligible because its depth-eight endpoint representations are unqualified.
Do not replace those representations or present the first case as independent
replication of the second.

Can at most three prospective scalar refinements locate a primitive periodic
cycle whose fixed event-3 input and next return meet the existing full-state
proximity criterion to every measured right-fold representation?

## Fixed refinement rule

For each qualified endpoint, average all sixteen signed input-x residuals:
four curve representations, two solvers and two repeat windows. Propose the
false-position parameter
`a_new = a_low - r_low*(a_high-a_low)/(r_high-r_low)`.
Require a finite strictly interior value; do not clip, substitute a midpoint,
change c, restart, or add an alternative seed. Each new point is dependent on
the retained prior result and is labeled accordingly. Maximum three points.

At every proposed parameter, correct the periodic orbit separately with DOP853
and Radau, using the SAME original EXP-494 base DOP853 state and period as the
phase reference/seed at every level. This keeps a common phase convention
rather than choosing a convenient shifted cycle index. Reuse EXP-494's complete
corrector, observation, repeat, primitive-period, historical-six/Barrio-eight
and paired gates unchanged. Save every returned corrector mesh and the full
2.5-period observation with dense coefficients. If the paired primitive cycle
fails, do not run that point's folds or any later point in the case.

For all four original first-case curve representations, retain initial x/z and
tangent, shift initial y to the section offset at a_new, and linearly interpolate
the endpoint mean root u/time using the same a fraction. Both fold solvers get
the same seed. Reuse EXP-496's new-box convention (u +/- .02, t +/-1, horizon
t+3, epsilon1e-6), eight Newton iterations and all EXP-490 fold/event/conditioning
and paired thresholds unchanged. Recompute all four representations; never use
an old fold's physical coordinates as the new fold.

For every qualified fold, compare all six correctly ordered cycle input/next
pairs using scales(15,15,.01), both solvers and windows(.25,1.25). The primary
event remains zero-based3, with full-state radius1e-4 and the complete
1e-6/1e-5/1e-4/1e-3 sensitivity ladder reported. No phase permutation, nearest
alternate index, x-only rescue or favorable representation subset is allowed.

Stop successfully if event3's full-state pair distance is <=1e-4 in all sixteen
variants. This is operational proximity to finite-image-curve geometry, NOT
exact membership, superstable flow eigenvalues, an invariant quotient, C/D,
a second critical point, a source word/arrow, or a homoclinic connection.

Otherwise continue only if every fold qualifies and all sixteen new residuals
have the same sign with magnitude >=1e-6. Replace the endpoint with that sign
using the complete newly measured fold/cycle record; retain the other endpoint.
Mixed or unresolved signs, unqualified folds, a failed primitive cycle or an
invalid interpolation stops the case unresolved. Three unsuccessful points
exhaust the study. No automatic extra point. Later levels stay explicit in the
six-row two-case/three-level ledger as unrun, with the exact stopping reason.

## Controls, freeze, audit and resources

Before targets, run twelve existing actual fold controls and four actual
one-/two-traversal periodic-circle controls. Add tests for full endpoint
eligibility, deterministic interpolation, unchanged phase seed, all-variant
stopping, sign/primitive failures, complete blocked-level retention, source/input
binding and scalar raw-data replay. Freeze and push source and all input hashes
before any successor target integration; no paid review is requested.

The local runner binds a clean live pushed source SHA and import closure, checks
resources, then creates one exclusive consumed-attempt witness. Retain all
started records, returned meshes, terminal profiles, failures and inventory.
Exceptions never authorize a resumed attempt. The separate auditor checks the
complete adaptive ledger, actual interpolation/seeds, all Newton/curve meshes,
periodic closure and dense-coefficient event/primitive-period replay, paired
qualification, and independently coded scalar contact arithmetic. It must not
call a numerical integrator during replay.

At most24 fold profiles and6 periodic profiles for the one eligible case;
maximum512 retained target IVPs and at most72 additional tiny fold census-guard
IVPs. Serial local CPU, 3600-second wall ceiling, 2GiB output cap, 12GiB initial
free-space reserve and 8GiB execution floor. The storage reserve is prospective
and reflects the already-retained EXP-496 archive/replay copies; no scientific
accuracy bound is relaxed. Preserve failed partial output on resource limits.
No GPU rental, paid API review or restricted source/data upload is involved.
