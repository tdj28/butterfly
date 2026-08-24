# Printed-hub homoclinic angle scans

Date: 2026-08-23

## Result

The first direct global-manifold discovery scans at Jones's approximately
printed hub coordinate pass their execution gates but nominate no homoclinic
return. This is a useful negative search result, not a rejection of Jones's
claim.

EXP-329 launches 96 midpoint angles from a radius-`1e-7` circle in the
two-dimensional unstable eigenspace. Every orbit exits radius `0.01` and is
followed for 400 time units. The closest sampled return reaches
`0.01047463129580855`, but is `0.9992900383572414` transverse to the unique
stable eigendirection. EXP-331 then binds that raw receipt and resolves one
coarse angular spacing on either side with 257 rows. It improves the distance
only to `0.010451007332282615`; the approach remains `0.9992956826043482`
transverse. No row meets both the `0.01` distance and `0.1` transverse-ratio
gates.

EXP-328's NumPy-boolean serialization failure and EXP-330's direct-execution
import failure are preserved. Their successors change only the administrative
defect, not the science configuration.

## Interpretation for Jones

- The local saddle-focus prerequisite remains verified.
- The finite-period family reaching the hub remains distinct from a putative
  equilibrium homoclinic orbit.
- The first finite unstable-manifold scans find close recurrent flybys, but
  their geometry is overwhelmingly transverse rather than stable-aligned.
- The printed coordinate is only approximate and a homoclinic connection is
  codimension one. Failure at exactly `(0.1798,0.2,10.3084)` cannot reject a
  nearby connection on the intended transition segment.
- Uniqueness has not been tested at all.

## Next gate

Replace fixed-coordinate angular gridding with a two-variable
manifold-matching solve in departure angle and `c` at fixed
`(a,b)=(0.1798,0.2)`. Construct both nonlinear local stable-manifold branches
by backward integration, record inward intersections of the returning unstable
manifold with the same sphere, and solve their two tangential mismatch
components. Repeat over shrinking spheres and with an independent integrator
before qualifying a connection. Only after one root is continued over the
declared historical segment can uniqueness receive a bounded test.

## EXP-332 parameter-aware pilot

The first implementation of that gate now passes. Nine `c` slices and 96
angles per slice produce 223 inward intersections with the radius-`0.02`
matching sphere. No direct chord candidate or signed-zero cell is present.
However, the best stable-target chord mismatch decreases monotonically from
`0.0156595` at `c=10.3044` to `0.00656684` at the upper boundary
`c=10.3124`; both signed tangent residuals shrink together and remain
positive. This is the first coherent parameter-direction signal, but not a
root. Hash-bound EXP-333 prospectively extends the unchanged scan through
`c=10.3224`.

## EXP-333 first manifold nominations

The unchanged extension passes with 369 inward sphere intersections. It finds
25 direct chord candidates over `c=10.3184--10.3204`; the best mismatch is
`0.00133787` at `c=10.3194`, about 6.69% of the matching radius. Three coarse
cells contain zero separately in both residual-component ranges. This is the
first encouraging parameter-aware evidence for a nearby connection, but the
componentwise cell rule is not a degree test and two cells have large corner
return-time spreads. EXP-334 therefore freezes an immutable residual-polygon
winding audit before any coupled solve or claim promotion.

## EXP-334 coarse-cell rejection and EXP-335 response

EXP-334 passes and exactly reproduces the three coarse hull cells, but every
residual polygon has winding number zero. Even the cell with only `0.05745`
time units of corner return spread fails the degree test. This rejects the
independent-coordinate rectangle criterion, not the 25 direct near matches.
Because only 28 cells had four radius-`0.02` returns, EXP-335 prospectively
enlarges the sphere to `0.025`, doubles angular resolution, halves `c` spacing,
and builds winding plus a one-time-unit continuity gate directly into the
scan.

## EXP-335 larger-sphere result and orthogonal slice

EXP-335 passes 2,496 rows with 977 inward returns, clearing its coverage gate
at `0.3914`. It finds 141 direct near matches and a best chord mismatch of
`0.00129410` at `c=10.3189`, consistent with the radius-`0.02` minimum, but
all four componentwise hull cells have winding zero. No fixed-`a` root cell is
nominated. The source labels both coordinates approximate and supplies no
endpoint table, so EXP-336 prospectively fixes the printed `c=10.3084` and
scans `a` across `[0.1758,0.1838]` under identical radius, resolution, degree,
and continuity rules.

## EXP-336 coverage failure and sharper orthogonal near miss

EXP-336 completes all 3,264 launches but preserves its sole failed gate: only
309 inward returns give `9.47%` coverage against the frozen 20% requirement.
The broad lower-`a` half supplies no returns. Among completed rows, the
orthogonal slice reduces the best chord to `0.00034435` at `a=0.1828`, 3.76
times below EXP-335's fixed-`a` minimum and only 1.38% of the radius. No degree
cell exists. EXP-337 binds the failed receipt and narrows to the observed
returning band while increasing the matching radius to `0.03`; EXP-336 remains
failed and unreclassified.

## EXP-337 coverage recovery and smooth shooting target

EXP-337 passes with 544 inward returns (`18.89%`) and 32 direct candidates.
Its best chord is `0.000162262` at `a=0.18255`, only `0.54%` of the matching
radius; one tangential component is already `-1.38e-6`. The two coarse hulls
still have winding zero, and the closest row is isolated under first-return
selection. EXP-338 therefore freezes the smooth three-equation endpoint match
in departure angle, `a`, and total flight time. A root remains a multiple-
shooting nomination, not a homoclinic qualification.

## EXP-338/339 shooting administration and Jacobian diagnosis

EXP-338's completed solve loses its receipt to a final NumPy boolean; unchanged
EXP-339 passes execution but remains unresolved at residual `0.000158819`. Its
receipt shows that the requested relative finite-difference scale collapses to
about `1.49e-8` at the zero normalized start, contaminating the long-trajectory
Jacobian. EXP-340 binds the unresolved result and freezes explicit absolute
central steps of `0.001`; all science variables, bounds, and gates are
unchanged.

## EXP-340 single-shooting stall and representation switch

EXP-340 preserves a sole `optimizer_terminated` failure after all 60 frozen
function evaluations. The corrected Jacobian reduces the mismatch by `16.73%`,
from `0.000162262469` to `0.000135120195`, and the result remains interior to
all three bounds. Its scaled singular values are `6.83669`, `1.54626`, and
`4.65403e-5`, giving a condition ratio near `1.47e5`. The corrected derivative
therefore helps, but does not cure the sensitivity of a single 234-time-unit
flow map.

The result neither proves nor rejects Jones's equilibrium homoclinic claim.
The frozen successor changes the numerical representation rather than the
physical endpoint problem: it seeds segmented multiple shooting from
EXP-340's final angle, `a`, and flight time, and matches a chain of short arcs
between the same unstable departure and nonlinear stable-manifold target.

## EXP-341 first segmented root nomination

The 16-arc solve reduces the maximum block defect to `2.66211e-9`, below the
prospective `1e-8` gate, at `a=0.18264360814275696`. This is the first numerical
root nomination in the Jones homoclinic chain. It remains formally failed only
because the optimizer continues beyond the first gated root and exhausts all
60 evaluations rather than reporting termination.

The same solution diverges under a single 234-time-unit initial-value replay,
reaching endpoint mismatch `2.05988`. That is expected for an unstable orbit:
the multiple-shooting Jacobian itself has condition ratio near `1.51e10`, and
the recorded replay discrepancy grows monotonically across the nodes. The
matched-arc residual is the relevant boundary-value diagnostic; an independent
segmented solver is the required cross-check. EXP-341 therefore strengthens
Jones's homoclinic claim from an unresolved near miss to a precise candidate,
but does not yet qualify it or its uniqueness.

## EXP-342 independent Radau reproduction

The doubled 32-arc Radau solve passes all gates at maximum block defect
`1.08861e-9`. Its corrected `a=0.1826436081740286` differs from the DOP853
candidate by only `3.13e-11`; its angle and time also clear prospective
agreement bounds by wide margins. The initial Radau split seed itself already
retains a sub-`1e-8` defect, so the result is not manufactured by a long drift
to another solution.

This materially strengthens Jones's proposed homoclinic mechanism. It also
sharpens the coordinate issue: the independently reproduced connection
candidate is about `0.00284361` above the paper's printed `a=0.1798`, far more
than four-decimal rounding. Shrinking-radius persistence is now the next gate
for distinguishing a true invariant-manifold connection from a finite-radius
boundary-value coincidence.

## EXP-343 radius persistence with a nuisance-gauge failure

At radius `0.025`, Radau again solves the matched arcs below the root threshold:
maximum defect `5.49708e-9`. More importantly, the inferred parameter changes
by only `1.30e-13`. The frozen run still fails because its nearly null
angle/time coordinates shift by `0.04983` and `0.10973`, with angle landing at
the old search-box boundary. This failure is preserved and is not counted as a
passing persistence test.

The result is favorable to the invariant-manifold interpretation but exposes a
bad gauge choice. The next successor widens only the nuisance angle/time box,
keeps the exact matched nodes, and retains the parameter and residual gates.

## EXP-344 first shrinking-radius step passes

The exact EXP-343 nodes pass a one-evaluation validation at maximum defect
`5.49708e-9` under the prospectively widened nuisance gauge. No further
optimization is allowed in this audit. The root is interior and preserves
`a=0.18264360817415815`, only `1.30e-13` from the radius-`0.03` value.

This qualifies persistence across radii `0.03` and `0.025`. It strengthens the
case that the root is an invariant-manifold connection rather than a
finite-radius endpoint coincidence; radius `0.02` remains the next frozen
test.

## EXP-345 radius-0.02 match and repeated gauge boundary

The radius-`0.02` Radau correction again falls below the root threshold at
maximum defect `5.60724e-9` and preserves `a` within `4.34e-13`. It is formally
failed because the nearly null angle coordinate reaches even the wider frozen
boundary and the optimizer exhausts its budget without an interior root
nomination.

This repeat makes the separation unusually clear: the scientific invariant
and manifold equations persist, while only the gauge coordinate drifts. The
exact nodes will be validated prospectively under a still wider angle box with
no further optimization.

## EXP-346 three-radius sequence qualifies

The exact radius-`0.02` nodes pass at maximum defect `5.60724e-9` and are
interior under the corrected gauge. Across radii `0.03`, `0.025`, and `0.02`,
the inferred `a` remains near `0.182643608174` to about `1e-12`; independent
DOP853/Radau and 16/32-arc representations agree.

This now strongly qualifies Jones's proposed homoclinic mechanism near the hub
height. It does not validate the printed point: at `c=10.3084`, the root lies
about `0.00284361` above printed `a=0.1798`. The next computation continues the
homoclinic curve toward the historical fixed-`a` path and tests whether it
crosses near the fixed-`a` scan minimum around `c=10.319`.

## EXP-347 first homoclinic-curve secant

At `c=10.3104`, the 32-arc Radau correction passes at maximum defect
`5.11943e-9` and gives `a=0.18199257965495652`. The first local secant has
`da/dc=-0.3255142594`; extrapolation reaches `a=0.1798` at
`c=10.3171357407`. This agrees closely enough with the earlier fixed-`a`
near-miss band to motivate a bounded second curve step, but it is not yet the
intersection solve.

## EXP-348 second-step residual stall

The `c=10.3144` correction remains interior and reaches
`a=0.18069045562011257`, nearly exactly on the first secant, but exhausts 40
evaluations at maximum defect `2.51470e-8`. It is therefore preserved as
failed; the apparent unchanged slope is diagnostic only. A same-`c`
failure-bound corrector is required before intersection targeting.

## EXP-349 segmentation recovery remains just above gate

The 64-arc Radau recovery lowers the maximum defect from `2.51470e-8` to
`1.18448e-8` and preserves `a` within `3.13e-14`. It remains formally failed,
missing the unchanged gate by `18.45%`. The monotone conditioning improvement
supports one final 128-arc recovery; no threshold is relaxed.

## EXP-350 second continuation point qualifies

The hash-bound 128-arc Radau successor passes at maximum block defect
`6.12599e-9` and gives `a=0.18069045562126884` at `c=10.3144`. It preserves
the 64-arc source parameter within `1.12e-12`; all prospective checks pass.

The qualified EXP-347-to-EXP-350 secant is `da/dc=-0.3255310084`, extremely
close to the preceding `-0.3255142594`. It predicts `a=0.1798` at
`c=10.3171353942`. This is now a well-controlled direct-solve target, but the
crossing itself remains open until a boundary-value solution at the historical
fixed-`a` path passes the unchanged root gate.

## EXP-351 direct fixed-a correction remains unresolved

The first direct solve holds `a=0.1798` exactly and solves `c`. It exhausts 40
evaluations at maximum defect `2.09830e-4`, so it is preserved as failed. The
run nevertheless reduces its initial defect by more than two orders of
magnitude and remains at `c=10.3171274773`, only `7.92e-6` from the qualified
secant prediction.

The failure is sharply localized: 121/128 block defects already pass `1e-8`,
while five of the seven failures occupy the final five arcs beside the stable
target. EXP-352 binds all exact failed nodes for a same-geometry warm restart;
no scientific threshold is relaxed.

## EXP-352 unbounded trial abort

EXP-352 accepts its source binding and initial evaluation but aborts before a
receipt when an unbounded internal-node trust-region trial makes Radau report
that its required step is below machine spacing. This is an execution abort,
not a scientific negative result.

EXP-353 prospectively adds a `+/-0.5` source-centered component box to every
internal node and requires a `0.01` normalized node-boundary margin. All
physical, residual, segmentation, tolerance, and budget gates remain fixed.

## EXP-353 fixed-a warm restart stalls safely

The node-bounded run completes and leaves `0.9982` normalized node margin, but
the maximum defect changes only from `2.098300e-4` to `2.098247e-4`. The
guardrail is not active and the same-point warm restart is preserved as
failed.

EXP-354 returns to qualified EXP-350 and performs a fixed-`c` correction at
the prospectively predicted crossing. A pass will provide corrected local
nodes and quantify the remaining `a-0.1798` error before exact fixed `a` is
reimposed; it cannot itself qualify the intersection.

## EXP-354 predictor-corrector remains active but unresolved

The first crossing correction reduces maximum defect from `8.74733e-3` to
`3.83423e-5`, remains well inside the node box, and moves to diagnostic
`a=0.1799788276`. It is preserved as failed because 12/128 blocks remain above
the gate. Optimizer optimality is still `2.85e-6`, unlike the fixed-`a`
residual floor, so EXP-355 freezes an exact-node same-`c` warm restart.

## EXP-355 crossing correction continues

The exact-node restart reduces maximum defect to `8.30202e-6` and moves to
diagnostic `a=0.1798386481`, only `3.86481e-5` above the historical value.
Nine blocks remain above the gate and optimizer optimality is still
`9.76e-7`; EXP-356 preserves every exact node for a second same-`c`
correction.

Tracked receipts: [`../experiments/receipts/EXP-329.json`](../experiments/receipts/EXP-329.json)
and [`../experiments/receipts/EXP-331.json`](../experiments/receipts/EXP-331.json).
Later compact receipts in this chain include
[`../experiments/receipts/EXP-340.json`](../experiments/receipts/EXP-340.json).
The independent root reproduction is tracked in
[`../experiments/receipts/EXP-342.json`](../experiments/receipts/EXP-342.json).
The second qualified continuation point is tracked in
[`../experiments/receipts/EXP-350.json`](../experiments/receipts/EXP-350.json).
Frozen execution commits: `4376c567db9554e858f20a823544996700236abc`
and `f223c95b4f6a2976115e7cff104a52be487f3a00`.
