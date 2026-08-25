# EXP-361 — Second homoclinic pseudo-arclength step

Status: frozen; not yet run

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
