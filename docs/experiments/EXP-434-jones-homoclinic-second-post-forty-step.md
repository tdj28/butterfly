# EXP-434 — Second conservative post-forty-point step

Status: executed; passed every prospective gate

EXP-433 passes at the defect floor, but its minimum singular value is now just
below twice the fixed acceptance floor. EXP-434 binds the exact passed
EXP-432/433 receipts, recomputes the tangent at EXP-433, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold remains
unchanged.

A pass adds the forty-second qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-434 passes every gate in two evaluations:

```text
(a, c) = (0.1798261390174906, 10.317054975789558)
Delta a = +4.757297773494429e-7
Delta c = -1.4645398387358455e-6
signed arclength = 0.004598680736441539
maximum block defect = 3.200024160379091e-9
minimum singular value = 9.90539949285173e-10
node-boundary margin = 0.9918660186727024
```

Raw receipt: `artifacts/EXP-434/receipt.json`, 78,621 bytes,
SHA-256 `9e84a9f5283a81ba21c95bde8b50fb7790b5611d3e40869c181145f2995da628`.
Compact receipt: [`receipts/EXP-434.json`](receipts/EXP-434.json).

Manifest:
[`../../experiments/manifests/EXP-434-jones-homoclinic-second-post-forty-step.json`](../../experiments/manifests/EXP-434-jones-homoclinic-second-post-forty-step.json).
