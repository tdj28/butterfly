# EXP-259 — Exact augmented period-96 flip

Status: frozen — not yet executed

EXP-258 supplies one magnitude-separated real-`-1` bracket on the exact
period-96 branch. EXP-259 phase-aligns and interpolates both bracket endpoint
node fields, then solves the coupled 128-segment orbit, free `a`, normalized
anti-periodic tangent equations.

The independent Radau check uses the identical segmented augmented equations
and four cyclic block-Floquet products, avoiding the long-period single-shot
conditioning already exposed by EXP-250. A maximum-evaluation optimizer stop
is accepted only if every unchanged DOP853 science residual passes. Orbit,
phase, tangent, normalization, real-`-1`, cyclic, every proper-subperiod, and
exact `112/128` identity gates remain explicit.

Manifest:
[`../../experiments/manifests/EXP-259-jones-period96-augmented-flip.json`](../../experiments/manifests/EXP-259-jones-period96-augmented-flip.json).
