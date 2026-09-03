# EXP-045 — Refined local fold line of the flip surface

Status: executed; passed
Manifest: `experiments/manifests/EXP-045-refined-flip-fold-line.json`
Claim target: smooth parameter drift of the flip surface's minimum-`b` fold

## Hypothesis and method

Combine the five EXP-043 traces with the EXP-044 extension at `c=5.3`. For
each `c`, use a frozen seven-point stencil around the sampled minimum in `b`,
parameterized by cumulative arclength in the complete nine-dimensional event
variables. Fit a local quadratic in arclength and evaluate its vertex to refine
the fold coordinate.

Fit the five refined `a_fold(c)` and `b_fold(c)` coordinates descriptively with
quadratics centered at `c=5.1`. Produce a provenance-bound three-dimensional
slice/fold-line figure and fold-drift projection.

## Acceptance and limits

All five local fits must have positive `b` curvature. Both fold coordinates
must decrease monotonically with `c`. Each descriptive quadratic must have
`R^2>=0.999` and maximum absolute residual at most `5e-4`.

Passing establishes a smooth sampled local fold line across `c in [4.9,5.3]`.
It does not establish the fold globally, identify a cusp or endpoint, or prove
that the fold line coincides with a shrimp caustic or TBA curve.

## Result

The clean run at commit `3ef01b55276540bddc6d1c8ae6322eb6c48a94ec`
passed every gate. All five local fits have positive `b` curvature, decreasing
smoothly from `0.37335` at `c=4.9` to `0.25354` at `c=5.3`. Both refined fold
coordinates decrease monotonically with `c`:

| `c` | refined `a_fold` | refined `b_fold` |
| ---: | ---: | ---: |
| `4.9` | `0.23092842` | `0.26461918` |
| `5.0` | `0.22468718` | `0.23244125` |
| `5.1` | `0.21874689` | `0.20315177` |
| `5.2` | `0.21308603` | `0.17663802` |
| `5.3` | `0.20768781` | `0.15277654` |

The descriptive quadratic for `a_fold(c)` has `R^2=0.99999956` and maximum
absolute residual `7.93e-6`; the `b_fold(c)` fit has `R^2=0.99999929` and
maximum residual `4.79e-5`. These are description and interpolation aids, not
an asserted global law.

The complete receipt SHA-256 is
`e6bb943a43f2e81a512f124674df1bd1a98eee17672dd482c8662bec87265082`.
The provenance-bound figure is
`artifacts/EXP-045/EXP-045-flip-fold-line.png` (SHA-256
`f24ac0cc3e5c94edc0b7277dec81f3d714407e8c531a169bea4396ed23f74e79`).

## Decision

Accept a smooth local fold line of the period-doubling surface over the tested
`c` interval. This upgrades the repeated-slice observation into a quantitative
three-parameter geometric object. The next decisive test is causal alignment:
overlay this orbit-defined surface/fold line on independent atlas boundaries
and measure whether it predicts period-window edges.
