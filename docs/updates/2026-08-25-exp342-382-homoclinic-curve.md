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
`7.5e-5` forward crossing step using the unchanged weights and gates.
