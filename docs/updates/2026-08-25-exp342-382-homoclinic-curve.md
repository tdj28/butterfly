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
