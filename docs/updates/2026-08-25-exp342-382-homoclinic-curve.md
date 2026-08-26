# EXP-342--382: qualified homoclinic curve and honest section gap

## What is now established

The revised-coordinate homoclinic candidate is no longer an isolated numerical
root.  EXP-342, EXP-347, and EXP-350 qualify three natural-continuation points;
EXP-360--363 and EXP-365--368 add eight chained, gauge-aligned
pseudo-arclength points.  All eleven roots pass the prospective
`1e-8` maximum matching-block gate.  The last accepted point is

```text
(a, c) = (0.1798174978856614, 10.317081488741884)
maximum block defect = 9.999341431358164e-9
```

It lies `1.74978856614e-5` above Jones's printed `a=0.1798` section.
The last qualified secant has `da/dc=-0.3255565528874298` and projects a
local crossing at `c=10.317135236348886`.

This is good evidence for Jones's proposed homoclinic organizing mechanism:
the nearby connection persists as a smooth parameter curve and approaches the
historical section.  It is also a coordinate correction.  The exact printed
point `(0.1798, 10.3084)`, the exact fixed-`a` intersection, and uniqueness on
any declared segment remain unqualified.

## Preserved failures

- EXP-369 finds a sub-gate root that moves backward in `c`, so it is not an
  accepted successor.
- EXP-370--375 expose a forward conditioning wall: enforcing the physical
  continuation direction can close the arclength equation without closing all
  matching blocks.
- EXP-376--377 show that an accurately solved sparse Newton step is not a
  descent direction even under a deep line search.
- EXP-382 rejects standard unconstrained `solve_bvp` collocation for this long
  unstable orbit: it escapes catastrophically even on the zero-step EXP-368
  positive control.

None of these failures falsifies the eleven receipt-bound roots.  They reject
specific successor formulations and require the next attempt to retain bounded
multiple shooting.

## Manuscript checkpoint

Figure 5 (`fig30-exp342-382-homoclinic-continuation.png`) now displays the full
qualified curve, the remaining historical-section gap, and the failed-gate
diagnostics.  The abstract, results, and conclusion all use the same eleven-root
count and explicitly withhold the exact intersection claim.  The 54-page PDF
passes the bibliography gate, compiles without layout warnings, and was
visually checked at the abstract, homoclinic figures, and conclusion.

## Weighted-plane control

Keep the EXP-367/368 512-arc warm start and bounded analytic-variational
multiple shooting, but replace the rank-deficient pure `(a,c)` arclength plane
with a weak full-state plane.  The node, angle, and flight-time contributions
must be scaled only enough to regularize the near-null direction; the physical
`(a,c)` secant must remain dominant.  EXP-383 freezes nuisance weights at
`0.01` relative to unit `a/c` weights and passes the zero-step 512-arc control.
It halves the maximum defect to `5.10888e-9`, holds `c` within `1.69e-9`, and
lifts the smallest Jacobian singular value by `6.63x`.  EXP-384 is the frozen
`7.5e-5` forward crossing step using the unchanged weights and gates.  It
aborts before solving because the exact warm start is outside its forward
optimizer wall.  Unwalled EXP-385 reaches a sub-gate root, but it is backward
in `c` and above the historical section.  EXP-386 retains the forward wall and
starts at the full-state predictor; neither failed attempt changes the eleven
qualified branch points.  EXP-386 holds the forward wall but finishes at a
`6.19e-7` matching floor exactly on that wall.  EXP-387 reduces the forward
increment to `2e-5`.  It improves the wall-limited matching floor by about one
order of magnitude to `6.13e-8`, but again lands exactly on its prospective
forward wall.  This makes the next controlled variable the plane orientation,
not another blind step reduction: lower the nuisance weights toward the pure
physical plane, first on a zero-step positive control, while retaining enough
regularization to avoid the earlier node-dominated near-null mode. EXP-388
freezes nuisance weight `0.003` and requires a minimum Jacobian singular value
of `5e-10`, nearly twice the pure-plane measurement, before a new forward step
is licensed. It passes in three evaluations with `5.10870e-9` maximum defect
and a `1.76697e-9` minimum singular value. The lower-weight plane is therefore
licensed for one prospectively frozen forward step; the qualified branch-point
count remains eleven until that step passes. EXP-389 executes the licensed
step but still lands on the forward wall at `5.81828e-8`, while its
`1.24573e-9` minimum singular value passes. The evidence now points to the
full-state predictor basin, not inadequate conditioning or plane weighting;
the next test holds nuisance variables at the qualified current root and
extrapolates only `(a,c)`. EXP-390 freezes exactly that predictor-only change
with every EXP-389 scientific and conditioning gate retained. It closes the
matching blocks to `6.27539e-9` with tiny node motion but still lands on the
forward wall. The remaining secant plane is being replaced by a local tangent
from the EXP-368 matching Jacobian. EXP-391 freezes the zero-step control with
a bordered analytic-Jacobian solve and a prospective `1e-8` tangent-residual
gate. It passes at `1.40565e-16` tangent residual and `4.58480e-9` maximum
orbit defect. The measured tangent is overwhelmingly node-dominated, so the
first licensed forward increment is reduced to `5e-7`, a normalized tangent
step of `0.09015`, without changing any scientific gate. EXP-392 keeps the
tangent and conditioning gates but reaches both its forward-`c` and angle
walls at `1.17380e-7` maximum defect. One prospectively wide-angle repeat now
separates an active nuisance bound from a genuinely excessive local step.
EXP-393 removes the angle wall but exhausts all 40 evaluations on the
forward-`c` wall at `8.85139e-8` maximum defect; its minimum singular value is
`4.51824e-10`, just below the prospective `5e-10` floor. This cleanly licenses
EXP-394's frozen quarter step (`Delta c=1.25e-7`, normalized `0.02254`) while
retaining the wide angle interval and every scientific acceptance threshold.
EXP-394 then terminates normally in seven evaluations with `7.14831e-9`
maximum block defect and `1.88806e-9` minimum singular value, but exposes a
protocol incompatibility: its predictor is only `1.225e-7` from the forward
optimizer wall, inside the unchanged `1e-6` forbidden global margin. It cannot
be counted. The runner now preflights that geometry, and EXP-395 freezes the
same quarter-step replay without the optimizer wall while retaining the final
`c>current` direction gate and all scientific thresholds.
EXP-395 then converges to an interior root-nominated solution at `2.33861e-9`
maximum block defect, but it lies `7.03286e-8` backward in `c` and its
`4.95816e-10` minimum singular value misses the prospective floor by `0.84%`.
Its `0.47244`-radian angle change nominates the rotated weighted closing normal,
not the machine-accurate local tangent, for the next control. EXP-396 freezes a
zero-step plane whose normal is the normalized local tangent itself, with all
scientific gates retained.
EXP-396 passes every gate in four evaluations: `4.00845e-9` maximum block
defect, `5.33666e-14` plane residual, `1.69490e-9` minimum singular value, and
`0.002005` normalized node motion. EXP-397 now freezes the licensed wall-free
quarter step with that standard tangent normal and every scientific threshold
unchanged.

EXP-405 passes every coordinate-free gate in two evaluations at
`(a,c)=(0.1798174936753,10.3170815017034)`. Its signed full-state progress is
`0.00114967018416`, maximum block defect `4.00407e-9`, plane residual
`5.41e-14`, and minimum singular value `1.68263e-9`. This adds the fourteenth
qualified point. Because `a` has turned upward from EXP-403, the first local
turn does not reach exact `a=0.1798`; a later return remains possible and must
be tested by chained full-state continuation.

EXP-406 freezes that first chained test from the exact passed EXP-403/405
pair. It recomputes the matching-Jacobian tangent at EXP-405, aligns it with
the previous full-state secant, and retains the same normalized step and every
numerical gate.

EXP-406 passes the first genuine chained secant-aligned step in two
evaluations at `(a,c)=(0.1798174943028,10.3170814997428)`. Signed progress is
`0.00114967018417`, maximum defect `4.00143e-9`, and minimum singular value
`1.67974e-9`. Both its recomputed predictor and corrected root move toward
larger `a`, strengthening the local-minimum interpretation while leaving later
turns open. EXP-407 freezes a fourfold-larger normalized step under the same
coordinate-free gates.

EXP-407 passes the fourfold step at
`(a,c)=(0.1798175017665,10.3170814834324)`, adding the sixteenth point. Its
`Delta a=+7.46365e-9`, `Delta c=-1.63104e-8`, `4.00127e-9` maximum defect, and
`1.67271e-9` minimum singular value resolve the local minimum on both sides.
EXP-408 freezes one more fourfold arclength increase to trace the outgoing
branch efficiently.

EXP-408 passes at normalized step `0.0183947` in four evaluations, reaching
`(a,c)=(0.1798176031556,10.3170811650024)`. It adds the seventeenth point with
`Delta a=+1.01389e-7`, `3.20148e-9` maximum defect, `1.26420e-9` minimum
singular value, and `0.9630` node margin. EXP-409 freezes another same-scale
chain to test whether the outgoing trend persists.

EXP-409 continues strongly outward to
`(a,c)=(0.1798178629840,10.3170803672769)` with `2.33839e-9` maximum defect and
positive signed arclength, but its minimum singular value `4.22399e-10` falls
below the prospective `5e-10` floor. Conditioning is its sole failed gate.
EXP-410 halves the step with all thresholds unchanged and passes in two
evaluations at `(a,c)=(0.1798177050799,10.3170808940738)`. Its `3.20048e-9`
maximum defect, `1.24926e-9` minimum singular value, and `0.9813` node margin
add the eighteenth qualified point. The conditioned outgoing branch remains
above and moves farther from the historical fixed-`a` section; this resolves
the first local minimum, not global nonintersection.

EXP-411 recomputes the tangent at EXP-410 and repeats the conditioned
`0.00919736` step. It passes every unchanged gate in two evaluations at
`(a,c)=(0.1798178421312,10.3170805092773)`, with `3.81275e-9` maximum defect,
`1.23425e-9` minimum singular value, and `0.9814` node margin. This nineteenth
qualified point reproduces the outgoing trend rather than merely replaying a
single recovery tangent. EXP-412 freezes the next identical-gate step.

EXP-412 passes the next step in two evaluations at
`(a,c)=(0.1798180156211,10.3170800076436)`. Its `5.34249e-9` maximum defect,
`1.21918e-9` minimum singular value, and `0.9815` node margin add the twentieth
qualified point. The outgoing trend persists; EXP-413 freezes a fourth
identical-gate half-step.
EXP-397 converges to an interior, well-conditioned root with `2.80316e-9`
maximum block defect and `1.04563e-9` minimum singular value, but it lies
`1.16506e-7` backward in `c`; direction is its only failed check. Its tangent
was still evaluated at inherited EXP-368. EXP-398 therefore freezes one
chained replay from the passed corrected 512-arc EXP-396 root, recomputing the
standard-plane tangent there before any further step reduction.
EXP-398 converges in four evaluations with `3.70048e-9` maximum block defect,
`1.53020e-9` minimum singular value, and every gate except direction passing;
the root is `5.46911e-8` backward in `c`. Corrected-source representation is
therefore not the primary cause at normalized step `0.0183947`. EXP-399 freezes
the licensed fourfold reduction to `Delta c=3.125e-8` and normalized step
`0.00459868`, with every other setting and acceptance gate unchanged.
EXP-399 passes every gate in two evaluations. It reaches
`(a,c)=(0.1798174938833,10.3170815075378)` with `2.58018e-8` forward `c`
motion, `4.00839e-9` maximum block defect, `4.09723e-14` plane residual, and
`1.68796e-9` minimum singular value. This adds the twelfth qualified curve
point and resolves EXP-397/398's backward roots as finite-step curvature at the
local resolution. EXP-400 freezes the same-size chained successor from this
new passed root; the manuscript figure/count update follows that checkpoint.
EXP-400 preserves an interior, conditioned backward root and exposes the
reason: the scaled local `c` tangent falls by `4.27x`, inflating the unchanged
physical request to normalized step `0.0196159`. Fixed `Delta c` is therefore
not a stable continuation controller here. The runner now supports exactly one
of physical-`c` or normalized-arclength stepping and passes all 396 tests.
EXP-401 freezes the adaptive replay at the previously passed normalized step
`0.00459868`, deriving its physical request from the new tangent. It converges
in two evaluations with `4.00829e-9` maximum block defect, `5.05e-14` plane
residual, and `1.68098e-9` minimum singular value, but moves `1.10392e-9`
backward in `c`; direction is its sole failed gate. Fixed-normalized stepping
therefore fixes EXP-400's inflation but reveals that this previously passed
scale still crosses a very small local positive-`c` turning radius. EXP-402
freezes the licensed fourfold normalized-step reduction with all scientific
settings and acceptance gates unchanged. EXP-402 also closes in two
evaluations with all root-quality, interiority, tangent, and conditioning gates
passing. It moves `4.97815e-9` backward in `c` but `3.46464e-10` downward in
`a`, toward Jones's fixed-`a` section. Positive `c` is therefore not a valid
monotone continuation coordinate at this local fold. The runner now supports
explicit tangent orientation plus independent `a` and `c` direction gates;
EXP-403 freezes a decreasing-`a`, unconstrained-`c` replay at the same
normalized step and unchanged scientific thresholds. It passes every gate in
two evaluations at `(a,c)=(0.1798174935369,10.3170815025596)`, with
`4.00637e-9` maximum block defect, `5.07e-14` plane residual, `1.68536e-9`
minimum singular value, and `1.09e-16` local-tangent residual. This is the
thirteenth qualified curve point and the first qualified step through the
local `c` fold. The historical fixed-`a` gap is now `1.74935e-5`; exact
intersection and uniqueness remain open.

The manuscript now carries all thirteen points in its global curve panel and
resolves EXP-368/399/403 plus the adjacent rejected controls in a nanoscopic
fold inset. The figure and receipt are bound to the clean source commit, and
the rebuilt 54-page PDF passes visual QA. EXP-404 freezes the first genuine
chained successor from EXP-399/403: it recomputes the local tangent at EXP-403,
retains decreasing-`a` orientation and the passed normalized step, and leaves
all scientific gates unchanged.

EXP-404 converges in two evaluations with `4.00407e-9` maximum block defect,
`5.44e-14` plane residual, and `1.68263e-9` minimum singular value, but `a`
rises by `1.38407e-10` while `c` falls by `8.56270e-10`; decreasing `a` is its
sole failed gate. The full-state signed arclength is nevertheless forward by
`0.00114967018416`. Neither displayed parameter is therefore a valid local
orientation coordinate. The runner now supports tangent alignment with the
previous full-state secant and an independent signed-arclength direction gate;
EXP-405 freezes the coordinate-free replay with every numerical threshold
unchanged.
