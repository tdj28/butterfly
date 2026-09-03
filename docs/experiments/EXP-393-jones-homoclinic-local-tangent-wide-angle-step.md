# EXP-393 — Wide-angle local-tangent homoclinic step

Status: executed; failed prospectively

EXP-392 preserves a machine-accurate local tangent and passing conditioning,
but stops simultaneously on its forward-`c` and departure-angle walls.  The
angle wall is independently active to `5.15e-11` normalized margin.

EXP-393 widens only the angle half-width from `0.25` to `1.0`.  The measured
local tangent, `Delta c=5e-7` (`0.09015` normalized step), 512 arcs, passed
`0.003` metric, analytic sensitivities, CSR/LSMR corrector, Radau/manifold
settings, all other bounds, budget, and every tangent, root, arclength,
conditioning, direction, and margin gate remain unchanged.

A pass adds a twelfth qualified above-section point.  A failure away from the
angle wall licenses a smaller normalized tangent step; neither outcome alone
qualifies the historical section, uniqueness, proof, or global topology.

## Result

EXP-393 does not pass, but it resolves the angle-bound diagnostic.  The
corrector terminates after the frozen 40-evaluation budget at

```text
(a, c) = (0.17981808360672594, 10.31708149874189)
maximum block defect = 8.851385164851165e-8
matching norm = 1.0704164752366382e-7
arclength residual = 4.4212810496047084e-13
```

The departure angle is now well interior, with normalized margin `0.53470`.
Only the prospective `c=current+1e-8` floor remains active, to
`5.33e-15` normalized margin.  The minimum measured singular value is
`4.51824e-10`, narrowly below the prospective `5e-10` gate, and the optimizer
exhausts all 40 evaluations.  The tangent itself remains machine-accurate at
`1.40565e-16` residual.

Widening the angle interval therefore removes that nuisance wall but does not
make the `0.09015` normalized step a root.  Under the frozen decision rule,
the next experiment reduces the step by four while keeping the wide angle
interval and every scientific threshold unchanged.

Raw receipt: `artifacts/EXP-393/receipt.json`, 86,906 bytes,
SHA-256 `b554cb5079314b62de05f0f40f0f4e7c8e940f3cd2d73c7bbc5bb6563b501ec7`.
Compact receipt: [`receipts/EXP-393.json`](receipts/EXP-393.json).

Manifest:
[`../../experiments/manifests/EXP-393-jones-homoclinic-local-tangent-wide-angle-step.json`](../../experiments/manifests/EXP-393-jones-homoclinic-local-tangent-wide-angle-step.json).
