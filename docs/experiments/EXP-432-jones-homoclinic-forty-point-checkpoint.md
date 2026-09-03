# EXP-432 — Conservative forty-point checkpoint step

Status: executed; passed every prospective gate

EXP-431 returns to the persistent defect floor, but the branch's minimum
singular value continues its gradual decline. EXP-432 binds the exact passed
EXP-430/431 receipts, recomputes the tangent at EXP-431, and holds normalized
arclength at `0.0045986807364392585` rather than doubling prematurely. Every
acceptance threshold remains unchanged.

A pass adds the fortieth qualified point and triggers a receipt-bound figure
and manuscript checkpoint. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-432 passes every gate in two evaluations:

```text
(a, c) = (0.17982520436676064, 10.317057856064773)
Delta a = +4.424269505198808e-7
Delta c = -1.3701338588134604e-6
signed arclength = 0.004598680736465057
maximum block defect = 3.200038739115917e-9
minimum singular value = 1.005439505600949e-9
node-boundary margin = 0.9917635578112183
```

This fortieth qualified point remains on the smooth outgoing arm. Its defect is
at the persistent numerical floor, while the smallest measured singular value
remains just over twice the frozen conditioning gate. The result triggers the
planned receipt-bound figure and manuscript checkpoint before continuation
resumes.

Raw receipt: `artifacts/EXP-432/receipt.json`, 78,567 bytes,
SHA-256 `58112e78d9347ac83931a5a2773072dea12109a802327e9b9863d5cd0bc93bb9`.
Compact receipt: [`receipts/EXP-432.json`](receipts/EXP-432.json).

Manifest:
[`../../experiments/manifests/EXP-432-jones-homoclinic-forty-point-checkpoint.json`](../../experiments/manifests/EXP-432-jones-homoclinic-forty-point-checkpoint.json).
