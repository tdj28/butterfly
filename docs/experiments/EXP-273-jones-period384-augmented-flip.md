# EXP-273 — Exact period-384 augmented flip solve

Status: frozen — not yet executed

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
