# EXP-354 — Crossing predictor-corrector

Status: failed; preserved for exact-node correction

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

The first correction exhausts 40 evaluations and is preserved as failed. It
reduces maximum defect from `0.00874733` to `3.83423e-5`, moves to
`a=0.17997882758465047`, and retains `0.67218` normalized node margin. Twelve
of 128 blocks remain above `1e-8`, with the largest defect in block 126.

Unlike the fixed-`a` floor, optimizer optimality remains high at `2.85e-6` and
the residual is still falling. This prospectively supports an exact-node
same-`c` warm restart before changing step length. The apparent
`a-0.1798=1.78828e-4` is diagnostic only until the curve point passes.

Raw receipt: `artifacts/EXP-354/receipt.json`, 31,939 bytes, SHA-256
`fcc1449d2b375f3e15274ee7aa4b8311a0c9ae56773d2a3d11f70a55d74f1edf`.
