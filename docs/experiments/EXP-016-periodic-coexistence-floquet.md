# EXP-016 — Period-12/period-3 coexistence and Floquet gate

Status: passed; basin mapping and continuation pending
Manifest: `experiments/manifests/EXP-016-periodic-coexistence-floquet.json`

## Purpose

Test the sole EXP-015 persistent-multistability candidate at
`(a,b,c)=(0.245,0.2,5.75)` by recovering both long-lived cycles and computing
flow closure and Floquet multipliers. The two initial states remained on period
12 and period 3 respectively through transient 19,200.

## Method and acceptance gate

Both basin probes are reintegrated after transient 9,600 with tighter DOP853
tolerances (`rtol=1e-11`, `atol=1e-13`, `max_step=0.025`). Up to 384 section
crossings are collected over 3,000 time units. Period classification requires
12 repeats at stricter recurrence tolerances.

Each recovered cycle must have the expected distinct period, flow closure error
at most `1e-7`, a neutral autonomous-flow multiplier within `1e-5` of one, and
all nontrivial Floquet multipliers strictly inside the unit circle.

Passing supports two stable coexisting periodic attractors for the sampled
basins. Basin-boundary mapping, exact shooting/collocation correction,
continuation of both families, and interval validation remain required for a
world-class persistent-multistability claim.

## Result

The clean run from commit `8c4e1c3` passed every prospective gate.

| Cycle | Period time | Flow closure error | Neutral multiplier | Leading transverse multiplier |
| --- | ---: | ---: | ---: | ---: |
| period 12 | 95.3558413 | `4.44e-12` | `0.999999999983` | `0.3140431051` |
| period 3 | 16.7881107 | `6.73e-12` | `1.000000000007` | `-0.8806869672` |

Both recurrence errors were approximately `1.5e-11`, and both nontrivial
multiplier moduli were strictly below one. Together with EXP-015 persistence
through transient 19,200, this is strong numerical evidence for two coexisting
stable periodic attractors at `(a,b,c)=(0.245,0.2,5.75)` for the sampled
basins.

The extremely small third multipliers are below reliable direct determinant
recovery in Float64; the divergence-integral determinant is therefore retained
separately. This does not affect the resolved leading transverse stability.

The checked-in receipt is [`receipts/EXP-016.json`](receipts/EXP-016.json).
