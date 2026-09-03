# EXP-204 — Lower-c scale-ensemble residual replay

Status: prospectively frozen; prepared for secure GPU execution

## Question

Do fresh trajectories over all 551 individually qualified EXP-203 stable
period-6 orbits produce a scale-, support-, and step-stable direct double-
critical nomination or a strict two-residual bracket?

## Frozen design

The deterministic selector retains every EXP-203 candidate that passed all
orbit gates; it changes no scientific data. Each candidate receives fresh
8,192-trajectory RK4 integrations at `dt=0.01` and `dt=0.005`. The same runs
yield nested 2,048- and full 8,192-trajectory supports. At each support and
step, the branch oracle uses the three EXP-202 low-smoothing values
`4.6416e-6`, `1e-5`, and `2.1544e-5`.

Eligibility requires all 12 reconstructions to resolve three branches, use one
ordered pair of orbit phases, keep each normalized critical-location span
within `0.03`, pass both return-pair gates, and agree in survivor fraction
within `0.03`. At least 250 candidates must remain eligible.

A direct nomination requires both signed residuals within `0.02` in every
reconstruction. A bracket requires a complete four-corner lattice cell with a
common assignment and both residuals bracketing zero separately in every
reconstruction. Either nomination passes the experiment after coverage.

Selection manifest:
[`../../experiments/manifests/EXP-204-lower-c-candidate-selection.json`](../../experiments/manifests/EXP-204-lower-c-candidate-selection.json).
Audit manifest:
[`../../experiments/manifests/EXP-204-lower-c-scale-ensemble-residual-gpu.json`](../../experiments/manifests/EXP-204-lower-c-scale-ensemble-residual-gpu.json).

Prepared artifact: `artifacts/EXP-204/candidates.json`, 867,378 bytes, SHA-256
`71aab52016abc8163887b2bdfd4e8124bde0e436be2239751f19d29bed490012`.

## Claim boundary

A pass nominates a point or cell for fresh zero-slope and DOP853/Radau
confirmation; it does not establish double superstability. A failure rejects
only this bounded, coverage-failed stable strip. Fold-following and unstable
continuation remain separate and necessary.
