# EXP-371 — Projected-arclength homoclinic section bracket

Status: failed; nuisance-angle bound active

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

EXP-371 reaches the 40-evaluation cap at its departure-angle lower bound
`2.466234829099821`. The final point is
`(a,c)=(0.17981971540812622,10.317297792331855)`, but maximum matching defect
is `1.0913841108642891e-5` and projected arclength residual is
`-3.694972193048207e-5`. Root, global-margin, and termination checks fail;
nodes and the other global variables remain interior.

The physical projection prevents a wrong-side root, but the narrow nuisance
angle gauge blocks closure. The successor widens only that angle half-width
from `0.5` to `2.0`, consistent with earlier angle-null audits, while retaining
512 arcs, the same projected plane, budget, tolerances, and scientific gates.

Raw receipt: `artifacts/EXP-371/receipt.json`, 85,445 bytes, SHA-256
`7586b03673ded87e7bef91f8b5d5422392c0013e854a04a9e4336f7e01844aec`.
