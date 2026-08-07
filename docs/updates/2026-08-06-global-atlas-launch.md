# Global-atlas launch

Date: 2026-08-06
Status: first reconnaissance complete; qualification launched

## Scientific decision

The Jones methodology is being extended from a primary-hub raster into a
bounded superstructure atlas. The target explanation has four layers:

1. stable periodic families and their saddle-node/period-doubling boundaries;
2. hub and branch-addition curves in return-map topology;
3. chaotic attractors versus nonattracting chaotic saddles and capture times;
4. global organization by saddle-focus/homoclinic geometry and reinjection.

No finite computation can cover the literal unbounded `(a,c)` plane. Each atlas
release will state its closed search domain. Boundary activity, newly discovered
families per added area, and continuation curves determine whether the domain
must expand.

## New execution item

EXP-013 is frozen as the first high-`a` reconnaissance. It covers
`a in [0.22,0.36]` and `c in [5,15]` at 1,189 points, including the historical
high-`a` Quickstart rectangle. A deterministic component extractor converts
periodic pixels into candidates for refinement and continuation without
mistaking raster adjacency for proof of connectivity.

## Compute authorization

The owner authorized up to USD 100 and invited a larger budget if justified.
The project treats USD 100 as a cumulative hard ceiling, not a target to spend.
Runpod use begins only after an exact production-observable parity test and must
record live price, runtime, estimated and actual spend, artifact hashes, and
verified teardown.

## Next evidence checkpoint

Run EXP-013 locally, summarize every component and near-recurrence, then select
spatially separated high-`a` candidates for convergence and basin qualification.
In parallel in the implementation sequence, upgrade the CUDA path from endpoint
parity to Poincare-crossing and period-classification parity.

## EXP-013 result

The clean `29 x 41` scan completed all 1,189 points with 82 periodic detections,
1,107 unresolved points, and no numerical failures. It produced 52 coarse
same-period components spanning periods 1, 2, 3, 4, 5, 6, 8, and 12. Eight
components touch a rectangle boundary. The first provenance-bound `(a,c)`
figure exposes a diagonal low-period band and separated islands at higher `a`.

EXP-014 now binds the exact aggregate hash and freezes 39 targets across the
diagonal, isolated high-`a` detections, boundaries, and top unresolved
near-recurrences. Its stronger tests use two initial conditions, longer
transients, and full Lyapunov spectra.

EXP-014 qualified 26 consensus-periodic targets and sent four finite-time
multistability labels to EXP-015. Long-transient checkpoints rejected three of
those and confirmed common capture at a fourth boundary case. One candidate at
`(a,b,c)=(0.245,0.2,5.75)` retained distinct period-12 and period-3 endpoints
through transient 19,200. EXP-016 now asks whether both cycles are transversely
stable under independent Floquet diagnostics.

EXP-016 passed both Floquet gates. EXP-017 then sampled a declared `21 x 21`
initial-condition plane: all 441 seeds converged, with 282 period-12 and 159
period-3 outcomes. Nearly half of four-neighbor edges switch basin at this
coarse scale. The next basin task is scale-dependent uncertainty measurement,
not a premature fractal/riddled label.

## EXP-018 GPU qualification

The owner authorized tracked-file-only frozen source export to task-owned
Runpod hosts. The first complete A40 run failed exact period parity and exposed
a numerical weakness: linear section interpolation reduced an RK4 trajectory
to second-order crossing accuracy. We retained the strict recurrence tolerance
and replaced the event calculation with cubic-Hermite dense output plus bounded
Newton refinement.

The corrected NVIDIA L4 run passed every period-1/2/3/7/12 control at
`dt=0.005` and `dt=0.0025`; maximum cyclic orbit errors were `4.633e-6` and
`2.922e-7`, respectively. A 32,768-trajectory raw benchmark sustained 717.1
million Float64 state-steps/second. The final receipt and archive hashes matched
across the local and remote copies, and all pods were terminated. The periodic
Poincare GPU path is now qualified for the next basin-scaling and multi-`b`
atlas experiments, but not for chaotic identity or Lyapunov claims.

## Basin scaling and multi-b atlas

EXP-019 resolved all 57,344 period-3/period-12 uncertainty pairs but showed
coarse-scale saturation. Its disclosed four-smallest-scale fit suggested a
fractal boundary. EXP-020 then prospectively froze seven smaller scales and new
seeds: 57,342/57,344 pairs resolved, uncertain fractions fell from `0.3236` to
`0.05657`, and the all-scale fit gave `alpha=0.4264`, pair-bootstrap interval
`[0.4094,0.4442]`, and `R^2=0.9976`. This supports a fractal, non-riddled basin
boundary in the declared plane; the numerical dimension remains provisional.

EXP-021 completed 296,241 `(a,b,c)` points across eleven `b` frames from 0.10
through 0.30. All frames passed, with a single numerical-failure pixel in the
entire slab. The fixed-color contact sheet and GIF show coherent motion of the
low-period band, nested shells, organizing spine, and higher-period windows.
The Jones section/recurrence method therefore scales to bounded 3-D atlas
reconnaissance. Same-period component tracking and true continuation are next;
the raster is not itself a bifurcation explanation.

EXP-021's 3-D same-period adjacency produced 5,142 raster components; 46 span
all eleven frames. EXP-022 selected internal period-3 and period-5 candidates
and replaced pixel evidence with phase-conditioned shooting. All 22 sampled
cycles corrected below `9.6e-12` flow closure, recovered neutral multipliers
within `1.4e-10`, and remained transversely stable. This directly supports two
persistent periodic families along moving `(a,c)` paths for `b in [0.1,0.3]`.
Pseudo-arclength continuation of orbit and bifurcation boundaries remains
necessary before claiming a unique hub drift or global organizing surface.

## First continuation geometry

EXP-023 naturally continued fixed-`(a,c)` period-3 and period-5 cycles in `b`.
EXP-024 refined three period-doubling crossings at `b=0.17682798` for period 3
and `b=0.14431134`, `0.18346759` for period 5. A scalar period-5 `+1` solve
switched orbit branches and was rejected rather than reported as a false
boundary.

EXP-025 through EXP-027 then traced the local period-5 family with exact
state-transition and parameter-sensitivity Jacobians at three successively
finer pseudo-arclength steps. Their descriptive `+1` estimates converge from
`0.27219295` to `0.27227869` to `0.27228272`; every trace has zero reversals in
`b`. EXP-027 missed its frozen 40-point threshold by three points because it
left the declared guard, so its formal gate remains failed. The replicated
smooth geometry nevertheless rejects a saddle-node of the traced branch and
turns the next task into a coupled `+1` eigencondition plus explicit
second-branch calculation. The generic interaction type remains unresolved.

EXP-028 then solved the orbit and nontrivial `+1` eigencondition together at
`b=0.272284059793`, explicitly excluding the autonomous flow-neutral mode.
EXP-029 used the resulting two-dimensional shooting null space to switch and
continue both coordinate signs. Its preregistered gates passed, but a
post-result phase check exposed that coordinate distance alone double-counted
one orbit at different phases.

EXP-030 corrected that weakness prospectively at a fresh `b=0.2730`. The two
switched representations align to whole-trajectory RMS `5.43e-7`, while the
primary-secondary RMS is `0.2003` and their periods differ by `0.01078`. The
primary multiplier is `1.0621` and the secondary multiplier `0.8787`. This
establishes two distinct invariant cycles and a stability exchange above the
event. EXP-031 now freezes the square-root branch-separation and multiplier-
ratio tests needed for a supercritical pitchfork-like normal-form assessment.

EXP-031 passed that prospective assessment across six frozen offsets above the
event. Phase-invariant branch separation scales with exponent `0.4989577` and
`R^2=0.99999916`; the median ratio of secondary multiplier deficit to primary
multiplier excess is `1.98050`, approaching two toward the event. All six
points show the primary unstable and secondary stable, with closure below
`1.21e-13`. The result is strong numerical evidence for a supercritical
pitchfork normal form after quotienting flow phase. Project prose retains
“pitchfork-like” pending symmetry identification and validated local reduction.

EXP-032 through EXP-034 began lifting the isolated event into parameter space.
EXP-032 solved nine smooth points but honestly failed a narrowly frozen lower
`b` guard. EXP-033 showed that doubling the natural `a` step loses the branch.
EXP-034 restored the qualified `0.0025` spacing: thirteen coupled events pass
from `(a,b)=(0.235,0.238415)` through the source to
`(0.265,0.347875)` at fixed `c=5.1`, with residuals near `1e-12`. Its declared
seventeen-point gate remains failed because the downward corrector at
`a=0.2325` is invalid. The accepted bounded curve is now evidence; continuation
below it and surface construction in `c` require full event-system pseudo-
arclength rather than further natural-step tuning.

EXP-035 implemented that full event-system pseudo-arclength. All thirty frozen
steps passed below `1.9e-12` closure and crossed the failed fixed-`a` region.
The curve reverses first in `b` near `(a,b)=(0.218513,0.203170)` and later in
`a` near `(0.214320,0.231695)`. A single fixed-`c` event curve can therefore
intersect constant-parameter slices multiple times, providing a concrete local
mechanism for repeated stability exchanges in the larger shrimp
superstructure. Normal-form identity away from the EXP-031 source and
continuation under `c` remain prospective requirements.

EXP-036 continued the coupled event transversely at fixed `a=0.245`, passing
thirteen `c` values from `4.8` to `5.4`. EXP-037 then attempted a first local
surface graph and honestly failed one coarse lower-`a` corner. EXP-038 retained
the same domain, halved the `a` step, and passed all 45 coupled events over
`a in [0.24,0.25]`, `c in [4.9,5.3]`, with maximum closure `3.81e-12`.

This is the first explicit orbit-defined bifurcation surface component in the
program. Near the source, `b*` rises steeply with `a` and falls with `c`; a
descriptive quadratic fits the patch with `R^2=0.999818`. The patch does not yet
show that the EXP-031 pitchfork-like normal form persists everywhere, nor does
it identify the return-map TBA surface.

EXP-039 tested whether that mechanism persists at a separated point of the
surface rather than being exceptional at `c=5.1`. At
`(a,b,c)=(0.245,0.2975539193,4.9)`, both switched coordinates again identify
one secondary cycle, the primary/secondary stability exchange holds at every
frozen offset, separation scales with exponent `0.4986728`
(`R^2=0.9999989`), and the median multiplier ratio is `1.9851`. The
pitchfork-like quotient normal form is therefore supported at two separated
surface points. Symmetry proof and behavior near the folded portion remain
open.

EXP-040 moved the identical qualification to the minimum-`b` fold of the
fixed-`c` event curve at `(a,b,c)=(0.2185131,0.2031698,5.1)`. It again recovered
one secondary geometric cycle from two phase representations, all-point
stability exchange, separation exponent `0.4928778` (`R^2=0.9999691`), and
median multiplier ratio `1.99691`. The fold therefore changes slice
multiplicity without destroying the tested local mechanism. The outstanding
theory problem is why the phase-fixed shooting system realizes this
pitchfork-like square-root structure despite no established exact spatial
symmetry.

### EXP-041 correction: the surface is a fundamental flip surface

A post-EXP-040 diagnostic exposed closure at half the stored parent period. We
therefore froze EXP-041 before the decisive calculation and audited the source,
separated-`c`, and minimum-`b` fold events. All three passed. Half-period
closures are at most `5.17e-10`; the nontrivial half-period multipliers are
`-1` to within `3.87e-10`; the doubled-period multipliers are `+1` to within
`2.57e-11`; and doubled monodromy agrees with the square of half-period
monodromy to at most `1.19e-9`. Closures at all other tested divisors `3..10`
remain above `2.92`.

This supersedes the earlier “pitchfork-like pending symmetry” interpretation.
The stored parent was traversed twice. Its fundamental flip multiplier `-1`
squares to the observed `+1`; the two switched arms are half-period phase
copies of one period-doubled child. The square-root opening, ratio-two scaling,
and stability exchange measured in EXP-031/039/040 are retained and now have
the standard second-iterate explanation.

The scientific object produced by EXP-035/036/038 is therefore an
orbit-defined period-doubling surface component with projection folds. This is
stronger and more directly aligned with Jones's period-doubling organization
than the provisional pitchfork language. It does not yet show that this single
component explains every shrimp or the full `(a,c)` superstructure. The next
frozen check audits parent and offspring fundamental periods off the surface;
global continuation and atlas/TBA overlays follow.

Full EXP-041 receipt SHA-256:
`66cc557c0c554d2c47ea1fe42cf2ff274840f13ca2d9c230257c331bc84b5e88`.

EXP-042 then performed the frozen off-event check at `b-b*=0.0004`. All three
parents close at half-period below `4.87e-12` and have unstable fundamental
transverse moduli from `1.00505` to `1.01713`. The three children miss
half-period closure by `0.15867` to `0.23338`, close at full period below
`2.35e-13`, have stable moduli from `0.93178` to `0.97979`, and have
child/parent-fundamental period ratios from `1.999642` to `2.000004`. The local
supercritical period-doubling classification is therefore independently closed
at the source, separated point, and projection fold.

Full EXP-042 receipt SHA-256:
`51b4d48b2f6711d7e18655339c3c6639d373120341f81b757aab6917aaae0eff`.

EXP-043 next traced 60 full coupled-event pseudo-arclength points at each of
five fixed `c` values. It remains formally failed: although four slices
reversed in `b`, the `c=4.9` curve reversed in `a` at `a=0.226896` before the
separately frozen `a<=0.225` gate, and `c=5.3` had not reversed within its
first 60 steps. Residuals remained below `3.80e-12` for closure and
`8.01e-13` for the eigencondition. EXP-044 prospectively extended only the
unresolved `c=5.3` trace by 30 points and passed, locating its `b` reversal.

EXP-045 then refined all five sampled minima with seven-point local quadratic
fits in full event-variable arclength. The fold line moves monotonically from
`(a,b,c)=(0.2309284,0.2646192,4.9)` to
`(0.2076878,0.1527765,5.3)`. Descriptive quadratic fits have
`R^2=0.99999956` for `a_fold(c)` and `0.99999929` for `b_fold(c)`, with maximum
residuals `7.93e-6` and `4.79e-5`. This establishes a smooth local fold line on
the period-doubling surface; atlas-boundary alignment remains the next causal
test.

EXP-046 performed that independent screen and failed its preregistered
period-5/10 hypothesis in all six frames. The orbit-defined predictions were
`6.64`–`7.32` cells from period 5 and `7.22`–`8.59` cells from period 10; the
plots instead placed every prediction in a period-3/6 band. EXP-047 froze that
post-result alternative and passed directly: all three corrected parents are
fundamental period 3 and all three children period 6, with recurrence errors
below `1.65e-12`.

The local flip, scaling, surface, and fold line are retained. Their family
identity is corrected from period 5/10 to period 3/6. The continuation from the
period-5 raster seed switched families before EXP-028; locating that first
identity change is the next provenance task.

EXP-048 attempted that audit with multi-period recurrence and failed because
unstable exact cycles shed roundoff over the observation horizon. EXP-049
replaced it with accepted section counts during exactly one stored closed
traversal. The result is decisive: EXP-023's named period-5 trace contains 40
six-crossing rows, five five-crossing rows (`b=0.175..0.195`), and one
four-crossing row (`b=0.2`). Its first corrected row is already six-crossing.

Therefore EXP-023's period-5 continuation claim is rejected: the unconstrained
corrector hopped among nearby closed orbits. Downstream global provenance from
that trace is invalid. The local period-3/6 flip surface remains supported by
its later independent recurrence, scaling, stability, and multi-point checks.
The next implementation must enforce recurrence identity at every accepted
continuation step.

EXP-050 implemented that safeguard from the independently verified EXP-022
period-5 seed. All 19 accepted points have exactly five crossings and closure
below `9.30e-12`, spanning `b=0.173669..0.204808` at fixed
`(a,c)=(0.245,5.1)`. Repeated six-crossing corrector roots at both ends are
recorded and rejected. The rebuilt branch has a genuine `-1` Floquet bracket
`[0.1825,0.185]`. Thus the period-5 branch and the separately validated
period-3/6 folded surface are distinct dynamical objects.
