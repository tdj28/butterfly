# EXP-205 — Lower-c period-6 flip refinement

Status: prospectively frozen before root refinement

## Question

Is EXP-203's high-`a` stability boundary a reproducible real `-1` Floquet
crossing of the corrected period-6 flow orbit?

## Frozen design

Seven fixed-`c` slices are selected from declared adjacent EXP-203 endpoints
that both correct successfully and bracket dominant real multiplier `-1`.
They cover `c=7.192,7.208,7.224,7.244,7.264,7.284,7.288`. Each event is
bisected in `a` with fresh DOP853 orbit correction and monodromy integration.

All seven must reach `a` bracket width `1e-9`, multiplier residual `1e-5`,
closure `1e-9`, neutral-multiplier error `1e-5`, real-multiplier tolerance
`1e-7`, and retain exactly six historical plus eight Barrio section phases.

Manifest:
[`../../experiments/manifests/EXP-205-lower-c-period6-flip-refinement.json`](../../experiments/manifests/EXP-205-lower-c-period6-flip-refinement.json).

## Claim boundary

A pass establishes seven precise period-doubling event seeds. It does not yet
establish a continuous curve, child branch, normal-form criticality, return-map
topology change, or double superstability. Those require separately frozen
coupled continuation and branch-switching tests.
