# EXP-491: local event-sheet and input-chart probe

Prospective exploratory successor, 2026-09-08. EXP-490 is completed and
unchanged. This study asks why its original candidate intervals cannot all be
treated as smooth fold brackets. It does not retry its Newton searches.

## Complete matrix and numerical question

Use all 26 hash-bound EXP-490 candidate intervals, retaining all sixteen
families. At each original left endpoint, arithmetic midpoint and right
endpoint, perform a complete extremum-partitioned section census in DOP853
and Radau: **26 x 3 x 2 = 156 retained target trajectories**. Initial states
are exactly q0+u*v0. Preserve the original tangent, parameters, return count
and historical-endpoint-derived horizon from the public candidate table.
The endpoints and midpoint are outcome-informed diagnostic inputs, not an
independent confirmatory sample; some midpoint paths were already traversed
by EXP-490's fixed-time shooting.

Use rtol=1e-13, atol=1e-15, max_step=.001, initial guard1e-8 and uncertain-
extremum plane margin1e-10. Retain the entire six-dimensional trajectory,
ordinary solver roots, reconstructed roots, extrema and all later events.
The first m+1 accepted negative crossings define the requested prefix, with
m=4 or8. No target words, curve fits, root correction, alternative samples,
adaptive mesh, sample refill or automatic retry.

At every sample, compare both solvers across the whole selected prefix, not
only the final event. Require angle>=1e-7 and section residual<=1e-8, no
uncertain extremum before the selected return or at a bracket endpoint of a
selected crossing, scaled-state error<=1e-6 with
scales(15,15,.01), and time error<=1e-7. Independently compare event-corrected
tangents and return-time derivatives: relative infinity error<=1e-5, with
denominator max(1,left magnitude,right magnitude) for each event/readout.
Retain each comparison and every failure. Input projection uses the unchanged
scaled gain>=1e-4 and x-fraction>=.001 checks from EXP-490.

## A screening rule, not an interval certificate

For each half-interval and each prefix event, measure its change in return
time and the residual from the trapezoidal derivative prediction

    t(u1)-t(u0) - .5*(t_u(u0)+t_u(u1))*(u1-u0).

A sampled interval is `screened-regular` only if all three points qualify
numerically and in input projection, each solver keeps a nonzero input x
tangent sign, every adjacent prefix-time change is<=1 model-time unit, and
every prediction residual is<=.25 model-time units. The time bounds are
conservative operational screening choices informed by the approximately
6.44-unit jumps in EXP-489; they are not universal dynamical constants or
rigorous continuity bounds. Report the observed maxima beside the bounds.
Report endpoint output-slope reversal separately; it cannot override a cut.

Three samples cannot rule out a hidden pair of boundaries between samples.
Passing means locally consistent sampled geometry only. Failure means
`cut-required-or-unresolved`, not proof of a grazing point or absence of a
fold. Missing/uncertain events, solver disagreement, poor projection,
input-sign reversal and time-coherence failure remain separate flags.
Do not draw a smooth interpolant through failures, certify a whole branch,
count upstream roots as distinct physical critical points, or assign C/D.

The ordinary event list from each same integration is the cheaper-method
comparison. Report any reconstructed prefix event absent from that list;
do not silently replace it. EXP-490's paired fold verdicts remain a separate
prior baseline, not a gate that changes this study's screening rule.

## Controls and audit

Controls traverse the same census, event correction, solver comparison and
interval analysis. The transformed rotation from EXP-490 supplies counts2/3
with: a genuine output fold, a regular no-fold curve, and an input x-projection
turn. Use three points around the exact output/input critical parameter,
respectively, or around zero for the no-fold control, with half-width .02.
All use initial(-4,0,.005), tangent(1,0,.01), k=1e4 except no-fold k=0, decay.03,
and horizon2*pi*count+2.5. The regular and output-fold controls must screen
regular; the input turn must fail input projection. Only the output-fold
control has opposite endpoint output slopes on a screened interval.

A separate analytic grazing field uses x'=0, z'=1 and
y'=d/dz[B(z)*((z-3)^2+x)], B(z)=(z-1)(z-2)(z-4)(z-5).
Initial(x,y,z)=(u,40*(9+u),0), tangent(1,40,0), section y=0 negative,
guard0, horizon5.5, requested count2. At u<0 an extra crossing pair lies at
z=3+-sqrt(-u); at u>0 it is absent. Samples(-1e-4,2e-4,5e-4) must preserve
valid points but fail the time-coherence screen. Samples(-1e-4,0,1e-4)
must explicitly retain the uncertain central tangency and fail the point
gate, regardless of whether roundoff reports an extra pair at that uncertain
center. The two noncentral samples must have three and two accepted crossings.
These two triples add twelve profiles to the 36 rotation profiles.
No target trajectory is used as an analytic control.

Tests cover exact control roots/time derivatives, missing and duplicated
arms, altered settings, input turns, coherent nonlinear curves, event jumps,
and uncertain extrema. A same-agent read-only audit verifies complete raw
inventories, initial identities, independent Rössler event algebra, separately
computed corrected tangents/time gradients, and exact decision replay.
This is not independent peer review or rigorous integration validation.

Pre-outcome code-audit correction: the EXP-490 image selector only tests whether
an uncertain extremum precedes the last selected crossing. A spurious crossing
just before an uncertain minimum can therefore evade that test. This successor
adds the explicit selected-bracket endpoint test above and a regression; the
frozen old selector is not edited. Audit its impact on the retained EXP-490
censuses separately, without new integration or changed old verdicts.

## Resources, failure rules and release

Run serially on the existing local CPU. The previous 1,572.14-second EXP-490
run contained72 censuses plus136 Newton trajectories and its controls. A
deliberately conservative heuristic charging its entire runtime to those
72 censuses, scaling to156 and doubling gives approximately6,812.61 seconds.
This uses already observed operational data, not a new target timing pilot;
input-dependent solver work remains uncertain. The hard whole-run limit is
7,200 seconds, including the48 short analytic control profiles. One execution,
8 GiB output cap, 16 GiB initial free-space reserve and8 GiB free-space floor.
Every successfully returned target integration is retained before interpretation.
If the frozen census helper raises before returning, its incomplete internal
mesh is unavailable; the start record, exception and earlier completed profiles
are preserved and the run is incomplete. Analytic controls
retain complete event/extremum reports rather than their integration meshes.
An integration/storage/
deadline exception preserves its failure record and the partial run, and
stops the remaining matrix. No old marker or attempt is reset.

Freeze and push the complete code, plan, tests and input bindings before
targets; verify the exact live remote hash, then execute in the same turn.
Report all intervals, point failures and method comparisons. Public result
and figure receipts retain every condition. Existing frozen sources stay
unchanged. No paid service, upload, model review, new paper claim, invariant
partition, symbol, arrow, homoclinic or whole-plane conclusion is authorized
by this local probe. Any such expansion requires its own scientific design;
paid reviews additionally require explicit human approval per request.
