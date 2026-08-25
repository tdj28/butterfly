# EXP-372 — Wide-angle projected-arclength section bracket

Status: completed; failed prospectively frozen root and termination gates

EXP-371's projected physical closure stops exactly on its nuisance departure-
angle lower bound. EXP-372 repeats the same qualified sources, deterministic
512-arc subdivision, predictor, `(a,c)` closing plane, `Delta c=0.00015`,
solver/manifold settings, sensitivities, node and other global bounds,
40-evaluation budget, and scientific gates. Only the angle half-width changes
from `0.5` to `2.0`.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or
computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-372-jones-homoclinic-projected-arclength-wide-angle.json`](../../experiments/manifests/EXP-372-jones-homoclinic-projected-arclength-wide-angle.json).

## Result

The solve reaches the 40-evaluation cap at
`(a,c)=(0.1798197154185,10.3172977923453)`. Its maximum matching defect is
`1.0913843303069732e-5`, matching norm is `1.3164158804789263e-5`, and
projected arclength residual is `-3.694972950563265e-5`. It therefore fails
the unchanged `1e-8` root and arclength gates. All source, initial-residual,
finite-state, direction, node-bound, global-bound, flight-time, and evaluation-
budget checks pass.

The angle is `2.3153598876`, leaving `1.34913` radians of margin inside the
widened bound. EXP-371 and EXP-372 nevertheless stop at the same physical
point and residual floor to the shown precision. The former angle wall was
therefore a symptom, not the cause. The final Jacobian's smallest singular
value is `2.70368e-10`; the next recovery changes the numerical linear algebra
and equation scaling, not the scientific acceptance thresholds.

This is not evidence against the eight qualified pseudo-arclength roots
through EXP-368, and it does not qualify the exact `a=0.1798` intersection.

Raw receipt: `artifacts/EXP-372/receipt.json`, 85,444 bytes, SHA-256
`77c83645abcf89e2ba5d7c4af687dd84f7e4d8ef237acab3a1ebbd5c3d24a875`.
