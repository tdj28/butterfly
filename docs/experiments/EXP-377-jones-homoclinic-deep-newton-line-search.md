# EXP-377 — Deep Newton line-search audit

Status: completed; all prospectively frozen Newton fractions rejected

EXP-376 solves the column-scaled Newton equation accurately but the near-null
step is so large that its first two bound-limited trials increase the nonlinear
defect before reaching the prospectively frozen `2^-12` minimum fraction.
EXP-377 binds that preserved state and changes only the minimum line-search
fraction to `2^-20`. Every attempted objective is now serialized.

The qualified sources, exact 512-node start, reduced physical plane, common
gauge, analytic derivatives, integration/manifold settings, source-centered
bounds, CSC/SuperLU solve, Armijo and boundary controls, 24-evaluation budget,
and every scientific gate remain unchanged. If no meaningful descent exists
at this scale, direct-Newton restarts are retired in favor of finer
segmentation or a better-conditioned boundary formulation.

Manifest:
[`../../experiments/manifests/EXP-377-jones-homoclinic-deep-newton-line-search.json`](../../experiments/manifests/EXP-377-jones-homoclinic-deep-newton-line-search.json).

## Result

The audit evaluates ten factor-two fractions from `5.41071e-4` through
`1.05678e-6`. Every objective exceeds the starting `1.9736827552e-11`. The
lowest trial cost is the final `1.9738089299e-11`, still `6.39e-5` relatively
above the start. No step is accepted, and the exact initial state is retained.

The directly factored linear residual remains `2.57761e-13`, so this is not a
linear-solver failure. Descent lies below the reliable nonlinear/integration
scale along a step whose scaled norm is `1522.68`. Direct-Newton restarts are
therefore retired. The successor changes representation to adaptive
collocation, eliminating the free multiple-shooting-node near-null coordinates
while preserving the physical continuation and manifold boundary conditions.

Raw receipt: `artifacts/EXP-377/receipt.json`, 80,710 bytes, SHA-256
`a51a048538709add996ade7e96e6fae720e5dd26d2204f6f0d570724d4a4a7d9`.
