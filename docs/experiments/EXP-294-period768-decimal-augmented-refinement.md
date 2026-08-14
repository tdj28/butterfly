# EXP-294 — Resolution refinement of the augmented seventh-event candidate

Status: frozen before execution

EXP-293 proves that the 50-digit augmented equations can converge without
falling onto the period-384 double cover, but its 1,024-step coordinate lies
outside the narrow physical bracket and its pointwise tangent field leaves the
source gate. EXP-294 preserves that failed level and warm-starts new corrections
at 2,048 and 4,096 classical-RK4 steps on every segment.

The three `a` values and periods must converge with fourth-order ratios in
`[12,20]`. Both the 4,096-step coordinate and its order-four Richardson
extrapolation must enter the untouched EXP-280 bracket. The finest orbit,
tangent field, and period must pass the original EXP-293 source-neighborhood
limits, all augmented residuals must be below `1e-22`, and half-orbit RMS must
remain above `2e-6`.

A pass qualifies a resolution-converged classical-RK4 augmented event
representation only. A separately frozen RK4 3/8 correction must agree before
the seventh event can be restored.

Manifest:
[`../../experiments/manifests/EXP-294-period768-decimal-augmented-refinement.json`](../../experiments/manifests/EXP-294-period768-decimal-augmented-refinement.json).
