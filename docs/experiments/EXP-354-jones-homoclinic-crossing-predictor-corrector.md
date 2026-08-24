# EXP-354 — Crossing predictor-corrector

Status: frozen; not yet run

The first exact fixed-`a` formulation reaches the predicted `c` but stalls
with its last five stable-end arcs unresolved. EXP-354 therefore returns to
the last qualified curve point, EXP-350, and corrects its exact 128 nodes at
the prospectively declared crossing `c=10.317135394165936` while solving `a`.

This is not allowed to establish an exact historical-path intersection by
itself. Passing instead supplies a qualified fixed-`c` predictor-corrector
state and measures the remaining `a-0.1798` error. Its corrected nodes can then
seed a much smaller direct fixed-`a` correction.

All physical manifold settings, Radau tolerances, 128-arc segmentation,
40-evaluation budget, and `1e-8` root gate are unchanged. The tested
source-centered node guardrail and explicit margin gate prevent the invalid
trial exposed by EXP-352.

Manifest:
[`../../experiments/manifests/EXP-354-jones-homoclinic-crossing-predictor-corrector.json`](../../experiments/manifests/EXP-354-jones-homoclinic-crossing-predictor-corrector.json).
