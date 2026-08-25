# EXP-377 — Deep Newton line-search audit

Status: frozen; not yet run

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
