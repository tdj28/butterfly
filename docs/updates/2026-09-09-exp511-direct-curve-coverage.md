# EXP-511: test curve coverage instead of repeating Newton

## Current checkpoint

The direct-curve diagnostic is implemented; target execution is pending the
exact-source freeze. The full suite passed: 2,607 tests, one Linux-only skip,
225.96 seconds. It will sample both depth-eight
curves at the failed EXP-510 parameter, with 20 fixed nodes per curve and both
DOP853/Radau (80 profiles, at most 160 IVPs). No paid API calls or cloud workers.

The distinction matters: a Newton zero with a collapsed input tangent is not
a fold. Direct sampling can reveal whether another regular part of the curve
reaches the intended fold, or whether a different finite-curve representation
is needed. A finite grid cannot prove that no such part exists between nodes.

## Verified before target exposure

- Thirty new/related target-free tests pass, including dense-data tampering,
  omitted products, solver disagreement, input turns, missing samples and
  preservation of a failed guard before the collector raises.
- Six analytic profiles (12 IVPs) pass closed-form state, time and tangent
  checks, and their saved dense polynomials replay successfully.
- An isolated startup using 119 copied source/input files passes without
  access to the local raw target artifacts.
- The full regression suite passes (2,607 tests, one Linux-only skip). The
  manuscript citation/figure check and generated symbolic control table pass.
- Earlier failures and frozen sources remain unchanged. The extracted EXP-510
  collapsed-root witness is diagnostic input, not a qualified Newton seed.

The first target-free control implementation exposed a units mismatch: its
unscaled analytic z coordinate failed the unchanged target projection gate.
The control was conjugately rescaled to z=0.01 units (k=10000) and checked
against the corresponding closed form. No target was run and no target
threshold was changed. All final analytic controls then passed.

Control summary SHA-256:
`6e7ad59ec7e39e715da2abc69d891141d8e14f3deb7ee2c1b13f96a7d2be7714`.
Collapsed-root input SHA-256:
`5b271195075b337b72b09552c5b86f707f2e68595a7f8974262a1cbce7518df9`.

## Execution and evidence contract

See the [frozen protocol](../experiments/EXP-511-direct-curve-coverage.md).
The runner defaults to validation; only explicit execution consumes the one
attempt. It retains guard/main trajectories, full dense coefficients, solver
event lists, reconstructed events and corrected tangents. The audit replays
those products and separately checks scalar distances and bracket decisions.
All raw products and the final summary share a pre-write 2 GiB quota.

The next action is the bounded target run, then full local raw audit, compact
public replay and an interpretation of sampled coverage. Jones's flow-level
chains remain unresolved; this work does not silently promote a root, a grid
bracket or a projection artifact into a verified symbolic chain.
