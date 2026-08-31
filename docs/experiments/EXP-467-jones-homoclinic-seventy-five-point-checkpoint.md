# EXP-467 — Seventy-five-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-466 passes at the defect floor, but its minimum singular value is only
`1.62x` the fixed conditioning floor. EXP-467 therefore binds the exact passed
EXP-465/466 receipts, recomputes the tangent at EXP-466, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-fifth qualified point and triggers a receipt-bound
figure and manuscript refresh. A failure is preserved. Neither outcome
establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-467 passes every gate in two evaluations:

```text
(a, c) = (0.17985311795555772, 10.316972100406758)
Delta a = +1.1697615204253609e-6
Delta c = -3.593706239257699e-6
signed arclength = 0.004598680736500587
maximum block defect = 3.199797489863061e-9
minimum singular value = 8.093294806532229e-10
node-boundary margin = 0.9939041000360378
```

Raw receipt: `artifacts/EXP-467/receipt.json`, 78,682 bytes,
SHA-256 `66942bb2bdd9a3b057eb6b4155edb712e24ac9109a07702fd068b9a55d1f9586`.
Compact receipt: [`receipts/EXP-467.json`](receipts/EXP-467.json).

Manifest:
[`../../experiments/manifests/EXP-467-jones-homoclinic-seventy-five-point-checkpoint.json`](../../experiments/manifests/EXP-467-jones-homoclinic-seventy-five-point-checkpoint.json).
