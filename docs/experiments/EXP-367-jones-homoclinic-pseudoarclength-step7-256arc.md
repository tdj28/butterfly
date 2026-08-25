# EXP-367 — Seventh homoclinic pseudo-arclength step

Status: passed

EXP-367 chains exact 256-arc EXP-365 and EXP-366 roots with the unchanged
`Delta c=0.00025`, common gauge, both free parameters, solver/manifold
settings, analytic sensitivities, bounds, 40-evaluation budget, and both
`1e-8` gates.

Passing advances the qualified branch toward a bracket of exact `a=0.1798`.
It cannot alone qualify the section or establish uniqueness or
computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-367-jones-homoclinic-pseudoarclength-step7-256arc.json`](../../experiments/manifests/EXP-367-jones-homoclinic-pseudoarclength-step7-256arc.json).

EXP-367 passes all ten checks at the 40-evaluation cap. It lands at
`(a,c)=(0.17988478554697546,10.316874803725971)` with maximum matching defect
`6.88547679234898e-9`, matching-residual norm `1.853853110124774e-8`, and
arclength residual `-5.018623103897335e-12`. Node margin is `0.85460`.

Its slope `-0.3255563984` projects exact `a=0.1798` at
`c=10.3171352365`. The qualified branch is now `8.47855e-5` above the section.

Raw receipt: `artifacts/EXP-367/receipt.json`, 48,563 bytes, SHA-256
`9bb8300bff8b606a125f235592d4ebaa3415130b96d519a8b67fe9e3745eaf65`.
