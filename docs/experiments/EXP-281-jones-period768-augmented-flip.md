# EXP-281 — Exact period-768 augmented flip solve

Status: completed — failed one independent multiplier gate

EXP-280 isolates one real-`-1` bracket on the exact primitive period-768
branch. EXP-281 jointly corrects 1,024 orbit nodes, period, free `a`, and
1,024 normalized anti-periodic tangent nodes from a nodewise secant seed.

The reference DOP853 solve and independent segmented Radau replay both use
maximum step `0.01`. Both direct-product flip residuals must pass the same
`1e-7` gate, alongside orbit/tangent residual, four-shift cyclic consistency,
primitivity, and exact `896/1024` section identity. A maximum-evaluation stop
is accepted only if every frozen science residual passes.

A pass qualifies a seventh exact event only. A period-1536 switch and
stability exchange remain separate prospective experiments.

Manifest:
[`../../experiments/manifests/EXP-281-jones-period768-augmented-flip.json`](../../experiments/manifests/EXP-281-jones-period768-augmented-flip.json).

## Result

At the frozen 60-evaluation ceiling, the 6,146-variable correction reaches
`a=0.2407010081734325`, period `5723.866415965068`. DOP853 orbit/tangent
residuals are `8.61e-11/2.31e-12`, and its direct-product flip multiplier is
`-1.00000000535`. The optimizer status is accepted because every reference
science residual passes.

Segmented Radau independently preserves orbit/tangent residuals of
`8.90e-11/3.80e-11`, cyclic-product spread `2.25e-10`, and a real multiplier,
but gives `-0.99999967774`: residual `3.22e-7` versus the unchanged `1e-7`
gate. This is the sole failed check. The minimum proper-subperiod closure is
`7.54e-6`, and exact `896/1024` section identity passes.

No seventh event is promoted from this receipt. EXP-282 freezes a tighter-step
re-evaluation of the immutable EXP-281 nodes, tangent nodes, period, and `a`
under both solvers. If that unchanged representation still fails, a new
coupled correction—not a relaxed gate—will be required.

Raw receipt: `artifacts/EXP-281/receipt.json`, 200,490 bytes, SHA-256
`b31c07081892d09bf37d53b949b4fb6365ae86ae18f54ba65a2dcc672437a790`.
Compact receipt:
[`receipts/EXP-281.json`](receipts/EXP-281.json).
