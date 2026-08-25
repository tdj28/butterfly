# EXP-369 — 512-arc homoclinic section bracket

Status: frozen; not yet run

EXP-368 qualifies a point only `1.74979e-5` above exact `a=0.1798` but uses
`99.993%` of the 256-arc root gate. EXP-369 prospectively subdivides exact
EXP-367 and EXP-368 roots to 512 arcs and reduces the desired predictor to
`Delta c=0.00015`.

Segmentation and predictor size are the only changes. Both free parameters,
the common gauge, solver/manifold settings, sensitivities, bounds,
40-evaluation budget, and both `1e-8` gates remain fixed. Passing below
`a=0.1798` forms a qualified branch bracket; it does not itself solve the
exact section or establish uniqueness or computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-369-jones-homoclinic-pseudoarclength-section-bracket-512arc.json`](../../experiments/manifests/EXP-369-jones-homoclinic-pseudoarclength-section-bracket-512arc.json).
