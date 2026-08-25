# FND-108 — Jones homoclinic mechanism qualifies at a revised coordinate

Status: qualified numerical finding; bounded uniqueness and rigorous proof open

At fixed `(b,c)=(0.2,10.3084)`, a 16-arc DOP853 boundary-value solve first
nominates an equilibrium homoclinic connection. Independent 32-arc Radau
shooting reproduces the root, and Radau corrections persist when the nonlinear
stable-manifold matching sphere shrinks from radius `0.03` to `0.025` and
`0.02`.

Across the qualified roots, `a` remains near `0.182643608174`; the two smaller
radii differ from their sources by `1.30e-13` and `4.34e-13`. Maximum arc
defects are `1.08861e-9`, `5.49708e-9`, and `5.60724e-9`. Preserved failures
EXP-343 and EXP-345 show that departure angle is a nearly null nuisance gauge:
it drifts to prospective boundaries while `a` and the manifold match remain
stable. Exact-node successors EXP-344 and EXP-346 validate the roots without
further optimization under corrected gauges.

## Consequence for Jones

The proposed saddle-focus homoclinic organizing mechanism receives strong
modern numerical support. The printed point does not: at the printed
`c=10.3084`, the qualified root is about `0.00284361` above `a=0.1798`, far
beyond four-decimal rounding. The natural next test is to continue the
homoclinic curve in `(a,c)` and determine whether it crosses the historical
fixed-`a=0.1798` path near the earlier scan minimum around `c=10.319`.

Two qualified local continuation steps now sharpen that test. EXP-347 passes
at `(a,c)=(0.1819925796550,10.3104)`, and EXP-350 passes at
`(0.1806904556213,10.3144)`. Their successive secant slopes are
`-0.3255142594` and `-0.3255310084`, predicting the historical-path
intersection near `c=10.3171354`. This agreement supports a smooth local root
curve but does not replace the required direct intersection solve.

Direct fixed-`a` attempts do not currently qualify that intersection.
EXP-351 and EXP-358, the latter seeded from curve-corrected nodes only
`1.749e-5` away in `a`, both return near `c=10.317127` with a stable-end
maximum defect about `2.10e-4`. Fixed-`c` predictor corrections EXP-354--357
approach `a=0.17981749` but reach a `3.76e-6` conditioning floor above the
gate. This repeated behavior leaves two live explanations: a local
fold/termination before exact `a=0.1798`, or a singular endpoint formulation.
It is not evidence against the already qualified revised-coordinate roots,
but it prevents promoting the secant crossing to a Jones-path result.

The first gauge-aligned two-parameter pseudo-arclength step now passes at
`(a,c)=(0.1805321204707,10.3148863716751)`, with maximum matching defect
`6.77e-9` and arclength residual `3.43e-12`. Its local slope is `-0.325544`,
again projecting the historical crossing near `c=10.31713529`. This
demonstrates that the prior fixed-coordinate floor is not an immediate branch
termination and favors a coordinate-conditioning explanation locally. It
does not exclude a later fold before `a=0.1798`, so the exact Jones-path
intersection remains unqualified.

A second chained step, EXP-361, passes at
`(a,c)=(0.1803726464063,10.3153762378641)` with maximum defect `7.51e-9`.
Its slope `-0.32554618` projects the historical crossing at `c=10.31713527`,
only `1.83e-8` from the EXP-360 projection. Two consecutive
pseudo-arclength roots now support a smooth local branch beyond the
fixed-coordinate stall.

EXP-362 supplies a third chained root at
`(a,c)=(0.1802255499680,10.3158280790748)`. It terminates normally after five
evaluations with maximum defect `8.48e-9`; its slope `-0.32554896` projects
the crossing at `c=10.317135256`. The agreement now persists across three
independently corrected pseudo-arclength secants.

EXP-363 passes a fourth chained point at
`(a,c)=(0.1800825699757,10.3162672724116)`. Its slope `-0.32555137` projects
the crossing at `c=10.317135246`. The maximum defect `9.93350e-9` is close to
the unchanged gate, so later steps reduce predictor size rather than weaken
the acceptance criterion.

The reduced 128-arc EXP-364 step narrowly fails at `1.09327e-8`, but the
segmentation-only 256-arc EXP-365 repeat passes normally at
`(a,c)=(0.1800152045459,10.3164741984457)` with defect `5.16572e-9`. Its
slope `-0.32555319` projects the crossing at `c=10.317135241`. This confirms
the narrow floor was representation-limited and leaves the branch only
`2.15205e-4` above exact `a=0.1798`.

EXP-366 passes the next 256-arc step at
`(a,c)=(0.1799473576083,10.3166826033527)` with defect `5.88416e-9`. Its slope
`-0.32555346` projects `c=10.317135241`, leaving `1.47358e-4` in `a` before
the historical section.

EXP-367 passes at `(a,c)=(0.1798847855470,10.3168748037260)`, maximum defect
`6.88548e-9`. Its slope `-0.32555640` projects `c=10.3171352365`; only
`8.47855e-5` remains before exact `a=0.1798`.

EXP-368 passes inside the former fixed-coordinate stall band at
`(a,c)=(0.1798174978857,10.3170814887419)`, maximum defect `9.99934e-9`. Its
slope `-0.32555655` projects exact `a=0.1798` at `c=10.3171352363`, only
`5.37476e-5` farther in `c`. The point remains above the section, so no bracket
or exact historical-path result is yet claimed.

Four prospectively preserved crossing attempts then separate branch evidence
from solver behavior. EXP-369 finds another sub-`1e-8` root on the wrong side
of the full-state hyperplane; EXP-370 sticks to a forward `c` wall. Projecting
the closing plane onto `(a,c)` in EXP-371 avoids both outcomes but stalls at a
nuisance angle bound. EXP-372 widens that bound by a factor of four and reaches
the same physical point and residual floor with ample angle margin. Thus these
failures do not falsify the qualified curve; they diagnose a poorly scaled,
ill-conditioned dense formulation near the desired section. The exact
historical-path intersection remains open and must still pass unchanged gates.

Subsequent sparse trust-region and direct-Newton audits enforce the projected
plane but isolate a node-dominated near-null mode; ten Newton fractions through
`1.06e-6` fail to decrease the objective. Standard adaptive collocation then
fails even on a zero-step positive control at EXP-368, escaping catastrophically
before encountering a singular Jacobian. These are negative method results,
not negative branch results. They narrow the viable successor to bounded
multiple shooting with a weak regularizing gauge or an equivalent constrained
block formulation.

EXP-383 supplies the required bounded-multiple-shooting positive control.  A
prospectively fixed hybrid plane with unit `(a,c)` weights and `0.01`
node/time/angle weights reproduces EXP-368 at 512 arcs, halves the maximum
defect to `5.10888e-9`, and holds `c` within `1.69e-9`.  The smallest measured
Jacobian singular value rises from `2.70368e-10` for the pure physical plane to
`1.79318e-9`, while the normalized closing direction remains dominated by
`a` and `c`.  This is a positive method result and licenses a forward crossing
step; it does not add a twelfth curve point or close the historical section.

The first licensed forward attempt separates residual convergence from branch
direction.  EXP-384 aborts before solving because its exact warm start lies
below a prospective forward optimizer wall.  The unwalled EXP-385 successor
then converges below both residual gates, but to the backward, above-section
point `(a,c)=(0.1798213190,10.3170697519)`.  This is another plane intersection,
not a qualified curve point.  EXP-386 keeps the forward wall and instead
starts from the forward predictor.

EXP-386 executes that forward-predictor test and reaches the full 40-evaluation
budget.  The plane residual closes to `1.10e-13`, but the point lands on the
prospective `c=current+1e-6` wall with maximum matching defect `6.19e-7` and
remains above the historical section.  EXP-387 reduces the forward increment
to `2e-5` and improves that floor by about one order of magnitude to
`6.13e-8`, but it too lands on its prospective `c=current+1e-7` wall.  The
paired failures show useful step-size convergence without a qualified root;
they now motivate changing the closing-plane orientation instead of merely
shrinking the step.  Neither is evidence of branch termination.

EXP-388 passes the resulting lower-nuisance-weight zero-step control.  With
node/time/angle weights reduced from `0.01` to `0.003`, it reproduces EXP-368
at `5.10870e-9` maximum defect and retains a `1.76697e-9` minimum Jacobian
singular value, comfortably above the prospectively frozen `5e-10` floor.
This licenses a forward step under a more physically aligned plane; it is a
method control, not a twelfth curve point or a historical-section result.

The licensed EXP-389 forward step still lands on
`c=current+1e-7`, at `5.81828e-8` maximum defect, despite passing the new
conditioning gate at `1.24573e-9`.  Together with EXP-387, this rejects
insufficient nuisance down-weighting as the main cause of wall capture.  The
next successor changes predictor initialization while preserving the passed
plane and all scientific gates.

EXP-390's physical-only predictor then reduces node motion by roughly `46x`
and closes every numerical residual gate, including a `6.27539e-9` maximum
block defect, but still lands exactly on the forward `c` wall.  Its departure
angle changes by `0.141677` radians while `c` advances only `1e-7`, showing
that the secant-defined plane still admits nuisance-gauge compensation.  The
next method upgrade is a local tangent computed from the EXP-368 matching
Jacobian, with the same scientific gates.

EXP-391 passes that local-tangent zero-step control.  The bordered solve has
`1.40565e-16` tangent residual; the corrected orbit has `4.58480e-9` maximum
defect and `1.93538e-9` minimum singular value.  Its scaled local tangent is
`99.9992%` node motion in norm, quantifying why a conservative normalized step
is required.  This is a positive method result, not a twelfth curve point.

The first nonzero local-tangent step, EXP-392, keeps the tangent and
conditioning gates but reaches both its forward-`c` and departure-angle walls
at `1.17380e-7` maximum defect.  It does not qualify a curve point.  The angle
bound is independently active, so one wide-angle repeat precedes any further
step reduction.

That repeat, EXP-393, moves the departure angle well interior but exhausts its
40 evaluations on the forward-`c` wall at `8.85139e-8` maximum defect.  Its
`4.51824e-10` minimum singular value narrowly misses the prospective `5e-10`
gate.  This licenses a quarter local-tangent step with unchanged scientific
thresholds; it still does not add a twelfth curve point.

The quarter step, EXP-394, terminates normally in seven evaluations at
`7.14831e-9` maximum block defect and `1.88806e-9` minimum singular value.
However, its predictor starts only `1.225e-7` from the forward optimizer wall,
inside the unchanged `1e-6` forbidden boundary margin.  It is preserved as an
administrative acceptance-geometry failure, and a new preflight prevents this
incompatibility from recurring.  A wall-free replay retains the independent
final forward-direction gate.

That wall-free replay, EXP-395, converges to an interior root-nominated
boundary-value solution with `2.33861e-9` maximum block defect and passing
global/node margins.  It nevertheless lies `7.03286e-8` backward in `c` and
its `4.95816e-10` minimum singular value narrowly misses the prospective
conditioning floor.  Its `0.47244`-radian departure-angle shift nominates the
weighted closing-plane metric for a standard local-tangent-normal control.

## Limits

This is not a computer-assisted existence proof and does not establish a
unique root on any declared parameter segment. Direct long initial-value
replay diverges because the orbit is extremely unstable; the qualified object
is the matched boundary-value solution. Pseudo-arclength or collocation
continuation, an explicit phase/gauge condition, and eventually validated
numerics remain required.

Evidence: EXP-341 through EXP-395, including preserved negative results and
their hash-bound compact receipts.
