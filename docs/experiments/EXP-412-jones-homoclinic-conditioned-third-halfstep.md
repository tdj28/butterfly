# EXP-412 — Third conditioned outgoing half-step

Status: executed; passed every prospective gate

EXP-411 passes the repeated half-step from a recomputed tangent. EXP-412 binds
the exact passed EXP-410/411 pair, recomputes the tangent at EXP-411, and
repeats normalized arclength `0.009197361472878517` with every gate unchanged.

A pass adds a twentieth qualified point and tests persistence of the outgoing
trend. It does not establish global nonintersection, uniqueness, proof, or
topology.

## Result

EXP-412 passes every gate in two evaluations:

```text
(a, c) = (0.1798180156211375, 10.317080007643572)
Delta a = +1.7348997496946517e-7
Delta c = -5.016336945828925e-7
signed arclength = 0.00919736147286265
maximum block defect = 5.342493884393814e-9
minimum singular value = 1.2191835614229898e-9
node-boundary margin = 0.9815385963540848
```

The twentieth qualified point preserves more than twice the fixed
conditioning floor and continues toward larger `a` and smaller `c`. This
extends the first outgoing arm but does not rule out later turns or branches.

Raw receipt: `artifacts/EXP-412/receipt.json`, 78,534 bytes,
SHA-256 `acbe4d63d62c9a9ba80c01755f9c663f56afd41f3d40185201ae82eb9729d5fc`.
Compact receipt: [`receipts/EXP-412.json`](receipts/EXP-412.json).

Manifest:
[`../../experiments/manifests/EXP-412-jones-homoclinic-conditioned-third-halfstep.json`](../../experiments/manifests/EXP-412-jones-homoclinic-conditioned-third-halfstep.json).
