# EXP-201 — Jones critical smoothing-scale audit

Status: prospectively frozen; prepared for secure GPU execution under the
owner's standing sub-`$30` authorization

## Question

Is EXP-200's shallow second critical a reproducible finite-data object with a
stable smoothing-transition scale, or does its identity drift under step size
and nested trajectory support?

## Frozen design

The candidate selector retains the complete 104-point set for which all four
EXP-200 baseline variants return three branches and the high-smoothing variant
returns two at both RK4 steps. It changes no orbit data. EXP-201 then integrates
the same 8,192 initial conditions at `dt=0.01` and `dt=0.005`. Each run yields
two nested rectangular supports: the full grid and a deterministic every-other
grid containing 2,048 initial conditions.

At each candidate, step, and support, a fixed 25-bin oracle is evaluated at
seven logarithmically spaced smoothing values from `1e-6` through `1e-4` with
unchanged prominence, spread, coverage, and bootstrap gates. A candidate
qualifies only if all four step/support combinations contain a monotone
resolved three-to-two transition, their transition indices span at most two
ladder steps, their normalized second-critical locations span at most `0.03`,
and all nested return-pair gates pass. At least 70 of 104 candidates must
qualify.

Selection manifest:
[`../../experiments/manifests/EXP-201-smoothing-sensitive-candidate-selection.json`](../../experiments/manifests/EXP-201-smoothing-sensitive-candidate-selection.json).
Audit manifest:
[`../../experiments/manifests/EXP-201-jones-critical-smoothing-scale-audit.json`](../../experiments/manifests/EXP-201-jones-critical-smoothing-scale-audit.json).

## Claim boundary

A pass qualifies a finite-data scale transition and critical identity. It does
not decide which smoothing limit represents invariant topology, prove that the
critical survives infinite data at zero smoothing, or nominate a superstable
center. A failure prevents further signed-residual continuation under this
scalar oracle until the critical is reconstructed by a different representation
or regularization model.

Prepared artifact: `artifacts/EXP-201/candidates.json`, 164,041 bytes, SHA-256
`79065c539cd6c3ae16ea2ed6b5dc627e8a2322d6de950295f56f43d42b747ed0`.
