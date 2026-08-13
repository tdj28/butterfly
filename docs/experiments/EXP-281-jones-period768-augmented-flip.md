# EXP-281 — Exact period-768 augmented flip solve

Status: frozen — not yet executed

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
