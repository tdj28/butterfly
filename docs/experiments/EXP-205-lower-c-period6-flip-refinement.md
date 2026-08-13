# EXP-205 — Lower-c period-6 flip refinement

Status: completed; all seven frozen flip refinements passed

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

## Result

All seven events pass. The refined `a` values decrease from
`0.2157982842636108` at `c=7.192` to `0.2157187472915650` at `c=7.288`.
Every final bracket is `7.63e-11` wide. The maximum absolute real-multiplier
residual is `2.02e-7`, all imaginary parts are zero to reported precision,
maximum closure is `2.83e-13`, and maximum neutral-multiplier error is
`1.20e-9`. Every refined orbit retains exactly six historical and eight Barrio
section phases.

The sampled high-`a` edge of the EXP-203 stable strip is therefore a real
period-doubling boundary seed set rather than a raster or stability-threshold
artifact. The next tests are coupled continuation of this curve, switching to
and qualifying the period-12 child, and then evaluating scale-aware critical
residuals on the boundary and child family.

Raw receipt: `artifacts/EXP-205/receipt.json`, 6,080 bytes, SHA-256
`42580233a066dc3dee8766f7fab75202ff4594b99cd74f0047e9966a0af22ee0`.
Compact receipt: [`receipts/EXP-205.json`](receipts/EXP-205.json).
