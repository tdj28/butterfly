# EXP-364 — Fifth homoclinic pseudo-arclength step at half size

Status: failed; narrow first-block residual floor

EXP-363 passes with only `0.665%` matching-gate headroom. EXP-364 therefore
prospectively halves only the desired predictor to `Delta c=0.00025`. It binds
the exact EXP-362 and EXP-363 nodes and retains both free parameters, 128
arcs, the common angle gauge, Radau/manifold settings, analytic sensitivities,
bounds, 40-evaluation cap, and both `1e-8` acceptance gates.

Passing qualifies one additional point closer to exact `a=0.1798`. It does
not by itself qualify that section or establish uniqueness or
computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-364-jones-homoclinic-pseudoarclength-step5-half.json`](../../experiments/manifests/EXP-364-jones-homoclinic-pseudoarclength-step5-half.json).

The reduced step reaches the 40-evaluation cap at
`(a,c)=(0.1800116479651023,10.316485123164421)`. Its maximum matching defect
is `1.093268261414582e-8`, only `9.33%` above the unchanged gate, while the
arclength residual is `-6.703342958838676e-12`. All source, finite-value,
direction, positivity, and boundary checks pass; node margin is `0.95569`.

The failure remains localized in the first shooting block and does not
indicate a branch turn or termination. Because smaller prediction alone does
not restore matching headroom, the next recovery prospectively doubles the
shooting segmentation while retaining the same qualified sources, half-step,
solver tolerances, budget, and acceptance thresholds.

Raw receipt: `artifacts/EXP-364/receipt.json`, 30,348 bytes, SHA-256
`b2bbec2a2ebfa0eee4a5d2a03d835de17e0e74a84ac5b64e6064a2c4043f7c65`.
