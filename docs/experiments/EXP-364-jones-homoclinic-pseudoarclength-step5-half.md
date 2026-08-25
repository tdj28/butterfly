# EXP-364 — Fifth homoclinic pseudo-arclength step at half size

Status: frozen; not yet run

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
