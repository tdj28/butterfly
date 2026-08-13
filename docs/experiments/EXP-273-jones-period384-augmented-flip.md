# EXP-273 — Exact period-384 augmented flip solve

Status: completed — passed

EXP-272 isolates one real-`-1` bracket on the exact primitive period-384
branch. EXP-273 jointly corrects 512 orbit nodes, period, free `a`, and 512
normalized anti-periodic tangent nodes from a nodewise secant seed.

The reference DOP853 solve and independent segmented Radau replay both use
maximum step `0.01`. Both direct-product flip residuals must pass the same
`1e-7` gate, alongside orbit/tangent residual, four-shift cyclic consistency,
primitivity, and exact `448/512` section identity. A maximum-evaluation stop is
accepted only if every frozen science residual passes.

A pass qualifies a sixth exact event only. A period-768 switch and stability
exchange remain separate prospective experiments.

Manifest:
[`../../experiments/manifests/EXP-273-jones-period384-augmented-flip.json`](../../experiments/manifests/EXP-273-jones-period384-augmented-flip.json).

## Result

The optimizer terminates normally by `xtol` after 48 evaluations at
`a=0.24070100830924687`, period `2861.933213133024`. DOP853 orbit/tangent
residuals are `1.64e-11/4.66e-13` and its flip multiplier is
`-0.99999999867`; segmented Radau gives residuals `2.26e-11/2.52e-11` and
multiplier `-1.00000003625`. Both multiplier residuals pass the symmetric
`1e-7` gate, and cyclic spreads remain below `9.71e-11`.

The minimum proper-subperiod closure is `2.03e-5`, and exact `448/512`
identity passes. This qualifies a sixth exact returning-arm event and tangent
mode. EXP-274 separately freezes the period-768 switch.

Raw receipt: `artifacts/EXP-273/receipt.json`, 104,643 bytes, SHA-256
`31f1fd0d2db4ca9b58909e9eda14b4a5c41a382f98647feb27114921d211d265`.
Compact receipt:
[`receipts/EXP-273.json`](receipts/EXP-273.json).
