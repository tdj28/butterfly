# EXP-258 — Segmented period-96 flip scan

Status: completed — passed

EXP-257 supplies nine exact primitive period-96 rows from stable birth to a
strongly unstable endpoint. EXP-258 computes four cyclic block-Floquet
products at every row and selects the uniquely larger-modulus non-neutral
eigenvalue under the same eight-orders separation rule that repaired EXP-242.

A pass requires a real `-1` bracket between the stable first row and negative
unstable terminal row, with all matching, reality, point-count, separation,
and cyclic calculations retained. It nominates an exact period-96-to-192 event
solve; it does not establish the event or a period-192 child.

Manifest:
[`../../experiments/manifests/EXP-258-jones-period96-segmented-flip-scan.json`](../../experiments/manifests/EXP-258-jones-period96-segmented-flip-scan.json).

## Result

The magnitude-separated mode is real at all nine rows and remains at least
`1.38e18` larger than the collapsed transverse mode. Exactly one real-`-1`
bracket is retained over
`a in [0.24070100367571418,0.24070101194748178]`, with endpoint multipliers
`-3.289238` and `-0.348481`. Cyclic real spreads stay below `2.44e-10`.

EXP-259 freezes a 128-segment augmented orbit/tangent solve with a nodewise
secant seed and an independent segmented Radau representation.

Raw receipt: `artifacts/EXP-258/receipt.json`, 22,169 bytes, SHA-256
`f81780ae78787e15697374cd32a9a34c21d1dd08cb89fe91adb29db07227b30a`.
Compact receipt:
[`receipts/EXP-258.json`](receipts/EXP-258.json).
