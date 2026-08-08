# EXP-123 — Blind saddle midpoint at `a=0.148`

Status: executed; failed blind cross-conditioning consensus

EXP-123 repeats the qualified blind coverage-censor classifier at the midpoint
of EXP-122's `[0.147,0.149]` bracket. No expected branch label is encoded.
Candidate counts two and three must be uniquely and unanimously selected
across all seven runs and both coordinates.

New scrambled-Sobol seeds 129--131 use a `2^13,2^14,2^15` ladder. This scale is
prospectively reduced by one power because EXP-122's weakest run retained 350
survivors and 3008 pairs at twice these sizes. The original floors of 100
survivors and 1000 pairs remain binding; failure is retained if the reduction
is inadequate.

A two result narrows the sampled bracket to `[0.148,0.149]`; a three result
narrows it to `[0.147,0.148]`. No result establishes a continuous TBA curve.

Immutable manifest:
`experiments/manifests/EXP-123-blind-a148-saddle.json`.

## Result

EXP-123 fails from clean commit `a23770a` in `180.91 s`. Six standard-horizon
runs select three in all 90 `y` variants and all 72 adequate-resolution `z`
variants. Their 20-bin `z` cells are unstable or under-resolve as two. The
later-conditioned 360-unit survivor subset instead selects two in all 30
coordinate variants. Every support and numerical gate passes, so no blind label
is assigned and `[0.147,0.149]` is retained.

Raw receipt SHA-256:
`73f7d6be60afcc70cb72f902f4b48063e647bff2d22d01a5f3be1c551cf1f3d6`.
