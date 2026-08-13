# EXP-265 — Exact augmented period-192 flip

Status: frozen — not yet executed

EXP-264 supplies one magnitude-separated real-`-1` bracket on the exact
period-192 branch. EXP-265 phase-aligns and interpolates both bracket endpoint
node fields, then solves the coupled 256-segment orbit, free `a`, normalized
anti-periodic tangent equations.

The independent Radau check uses the identical segmented augmented equations
and four cyclic block-Floquet products. A maximum-evaluation optimizer stop is
accepted only if every unchanged DOP853 science residual passes. Orbit, phase,
tangent, normalization, real-`-1`, cyclic, every proper-subperiod, and exact
`224/256` identity gates remain mandatory.

A pass qualifies a fifth exact returning-arm event and tangent mode for a
separately gated period-384 switch. It does not establish that child or a
limiting scaling law.

Manifest:
[`../../experiments/manifests/EXP-265-jones-period192-augmented-flip.json`](../../experiments/manifests/EXP-265-jones-period192-augmented-flip.json).
