# EXP-294 — Resolution refinement of the augmented seventh-event candidate

Status: completed — failed only the original tangent-source neighborhood gate

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

## Result

Both new discrete systems converge. The 2,048-step level reaches orbit/tangent
residuals `1.33e-33/5.95e-33` in three updates; the 4,096-step level reaches
`7.89e-28/1.32e-26` in two. Their coordinates are
`0.24070100794764657896` and `0.24070100821945929997`. Together with EXP-293,
the `a` convergence ratio is `15.7178`; the period ratio is `15.7060`. The
order-four Richardson coordinate is `0.24070100823758014804`.

Both the finest and extrapolated coordinates lie inside the untouched EXP-280
bracket. The finest state and period displacements pass at `4.79e-5` and
`5.00e-6`, while half-orbit RMS remains `2.58e-5`. Thus correction,
fourth-order `a` and period convergence, both coordinate bounds, and
primitivity all pass.

The sole failure is the unchanged pointwise tangent-source gate:
`4.162 > 0.1`. It is essentially constant across all three resolutions rather
than decreasing. The normalized base tangent differs by only `2.24e-4`, the
median pointwise direction cosine is `0.99999987`, and the global field cosine
is `0.99724`; large disagreement is localized after long transient tangent
amplification. EXP-294 therefore qualifies a resolution-converged classical
augmented representation except for identity with the old Float64 tangent
field. It does not restore event seven. An independent tableau must converge
to the new orbit and tangent line before that source representation can be
superseded.

Raw receipt: `artifacts/EXP-294/receipt.json`, 359,216 bytes, SHA-256
`08ebfdb13fdf24a63873ed51481e82fb2ecf41b772f6cc1c145f6096d0024449`.
Compact receipt:
[`receipts/EXP-294.json`](receipts/EXP-294.json).
