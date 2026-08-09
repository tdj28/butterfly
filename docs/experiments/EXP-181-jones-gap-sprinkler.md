# EXP-181 — Jones support-gap survivor reconstruction

Status: executed; failed fixed-step/DOP853 long-time label audit

## Question

Can a prospectively defined transient-survivor cloud restore return-map domain
support at EXP-180's sole `a=0.156` gap and recover the physical critical
location predicted from its two neighboring path points?

## Frozen design

EXP-181 was committed and pushed before execution. Two independent long
DOP853 trajectories calibrated and validated the banded attracting cloud on
the negative, gated historical Jones section. A fixed-step Float64 RK4
`128 x 64` section ensemble was then evolved to time 300. A trajectory was
captured only after eight consecutive accepted returns within scaled distance
`0.0002` of the calibration cloud. Only middle-time return pairs belonging to
final survivors could vote.

Both x and z required 1000 pairs, all seven locally bootstrapped variants,
70% domain coverage, and agreement with physical critical predictions frozen
from the `a=0.1555/0.1565` EXP-180 flanks. A 16-seed long-horizon pointwise
capture-label audit against DOP853 had to agree at least 90%.

Manifest:
[`../../experiments/manifests/EXP-181-jones-gap-sprinkler.json`](../../experiments/manifests/EXP-181-jones-gap-sprinkler.json).

## Result

The clean run at source commit
`b6cb854a9f8fd9fc7e536eecce04a7be7b0d1870` failed overall after `64.99`
seconds. The independent attractor-reference gate passes: both integrations
succeed with 951/952 crossings, neither resolves a period under the frozen
recurrence test, and the maximum symmetric scaled cloud distance is
`0.000115331 < 0.0002`.

The ensemble has no numerical failures. Survivor counts decay as
`8192, 8163, 7992, 7855, 7707, 7552`, and final survivors supply 64,571 return
pairs per coordinate. The local observable passes every variant:

| coordinate | survivor domain | physical critical | frozen prediction | absolute error | joint normalized span |
|---|---|---:|---:|---:|---:|
| `x` | `[-28.7550,-7.85623]` | `-18.5765441` | `-18.5753408` | `0.00120335` | `0.0195938` |
| `z` | `[0.00410315,0.00718230]` | `0.00518224715` | `0.00518306415` | `8.17e-7` | `0.0175670` |

The global branch count remains unresolved, as intended, because variants
split between two, three, and unresolved labels.

The experiment fails only the frozen long-time capture-label audit: agreement
is `10/16 = 0.625`. All eight fixed-step survivors remain survivors under
DOP853, but only two of eight fixed-step captured seeds retain that label.
This asymmetric failure is preserved.

## Interpretation

EXP-181 supplies exceptionally close prospective geometric evidence at the
missing parameter point, but the accepted experiment is still failed. In a
chaotic flow, long-time trajectory identity after changing integrator is not a
valid parity observable; EXP-113 already avoided this by requiring statistical
survival/topology parity plus short-horizon trajectory agreement before
decorrelation. A retrospective control confirms that all 128 validation-cloud
seeds are captured by fixed-step time 75, so the capture definition is not
simply blind to the attractor. That diagnostic does not rescue EXP-181.

The unchanged scientific target requires a prospectively frozen resolution
comparison: survivor fractions and critical locations must agree between two
RK4 steps, attractor seeds must be captured, and DOP853 must match only over a
short horizon where statewise comparison remains meaningful.

Raw receipt SHA-256:
`6b59c47d75d0c14fbe6ad46c3e601def0ca695c7472e8efe9d8ef0e83df5905b`.
State artifact SHA-256:
`23fb0dc5914d7933f3da16cc97935b5ce5d2f9eabd5f5d3df8fc3cd55916fd7c`.
Compact receipt:
[`receipts/EXP-181.json`](receipts/EXP-181.json).
