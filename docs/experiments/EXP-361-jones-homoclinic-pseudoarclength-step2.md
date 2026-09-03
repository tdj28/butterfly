# EXP-361 — Second homoclinic pseudo-arclength step

Status: passed

EXP-361 tests whether the qualified EXP-360 branch continues another local
step toward the historical `a=0.1798` section. It binds the exact 128-arc
nodes from EXP-350 and EXP-360 and constructs a fresh tangent after expressing
both departure angles in the same eigenspace gauge.

Both `a` and `c` remain free. The desired `Delta c=0.0005`, Radau tolerances,
stable/unstable manifold radii, analytic `a/c` sensitivities, source-centered
node guardrail, global bounds, 40-evaluation budget, `1e-8` matching gate, and
`1e-8` arclength gate are unchanged from EXP-360.

A pass supplies a second pseudo-arclength point and further tests whether the
historical-section approach is smooth. It cannot by itself establish the
intersection, exclude a later fold, prove uniqueness, or supply a
computer-assisted existence proof.

Manifest:
[`../../experiments/manifests/EXP-361-jones-homoclinic-pseudoarclength-step2.json`](../../experiments/manifests/EXP-361-jones-homoclinic-pseudoarclength-step2.json).

The run passes all ten frozen checks at
`(a,c)=(0.18037264640633813,10.315376237864077)`. The maximum matching defect
is `7.513531688686202e-9`, the matching-residual norm is
`1.3726958851162062e-8`, and the pseudo-arclength residual is
`-4.389255484679028e-11`. The root gate is satisfied when the optimizer reaches
the 40-evaluation cap; this outcome is explicitly allowed by the frozen
termination check. The node-boundary margin remains `0.93840`.

The corrector realizes `97.97%` of the requested `Delta c`. Its local slope
from EXP-360 is `da/dc=-0.3255461756`, projecting `a=0.1798` at
`c=10.3171352707`. The projection agrees with EXP-360 to about `1.83e-8` in
`c`. This qualifies a second chained pseudo-arclength point but not the
historical intersection.

Raw receipt: `artifacts/EXP-361/receipt.json`, 30,235 bytes, SHA-256
`85104fe7396008b728f54e2982a1baabde21873a7412dc0b205658a6dfe2283f`.
