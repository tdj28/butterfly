# EXP-371 — Projected-arclength homoclinic section bracket

Status: frozen; not yet run

EXP-369's full-state hyperplane selects a backward root; EXP-370's directional
wall then becomes active without recovering the root. EXP-371 retains the
same qualified sources, deterministic 512-arc subdivision, full-state secant
predictor, `Delta c=0.00015`, both free parameters, solver/manifold settings,
analytic sensitivities, bounds, budget, and acceptance gates. It changes only
the closing pseudo-arclength equation, projecting its tangent onto `(a,c)` so
nuisance nodes, time, and departure angle cannot select the branch side.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or
computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-371-jones-homoclinic-projected-arclength-section-bracket.json`](../../experiments/manifests/EXP-371-jones-homoclinic-projected-arclength-section-bracket.json).
