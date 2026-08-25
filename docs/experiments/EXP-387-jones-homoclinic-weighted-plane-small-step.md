# EXP-387 — Small-step weighted homoclinic continuation

Status: frozen; not yet executed

EXP-386 shows that the `7.5e-5` crossing predictor is too aggressive for the
forward-constrained weighted plane: correction returns to the lower `c` wall.
EXP-387 reduces only the desired increment to `2e-5` and the forward optimizer
floor to `1e-7`.  The resulting predictor remains above `a=0.1798`; this is a
continuation recovery step, not a bracket experiment.

The exact EXP-367/368 sources, 512 arcs, weights, analytic sensitivities,
CSR/LSMR solver, Radau/manifold settings, source-centered bounds, 40-evaluation
budget, and `1e-8` matching/arclength gates remain unchanged.  A pass adds a
twelfth qualified curve point and supplies a shorter secant for the next
historical-section attempt.

Manifest:
[`../../experiments/manifests/EXP-387-jones-homoclinic-weighted-plane-small-step.json`](../../experiments/manifests/EXP-387-jones-homoclinic-weighted-plane-small-step.json).
