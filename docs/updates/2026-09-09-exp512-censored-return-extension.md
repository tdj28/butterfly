# EXP-512: resolve finite observation-window censoring

## Current checkpoint

The successor is implemented and its 13 target-free tests pass. An isolated
128-file source/input consumer passes, and the unchanged dense capture/replay
producers pass replay of EXP-511's six analytic profiles without new IVPs.
The full regression suite passes: 2,638 tests, one Linux-only skip, 313.88
seconds. No EXP-512 target has been exposed. The branch is based on fresh
main `72883c948390539234b1f674289cff650a3f8940`, after PR #77 passed all four
final-head push/PR Python checks and merged normally.

The fixed selection is **all seven** EXP-511 paired samples that recorded
eight of the required nine accepted returns before the horizon, not a
selected promising subset. Increase each horizon by exactly 15 time units
and retain the complete trajectory from its unchanged initial data. Two
solvers, seven samples, guard plus main: at most 28 new IVPs. The target
remains local, with no paid API review or cloud worker.

Every previously recorded eight-return prefix must agree in state, time and
tangent, with no added or missing accepted event or uncertain extremum before
the old horizon. A matching prefix does not imply that the ninth return was
observed: the controller records these as separate outcomes. Failed prefix
checks prevent admission to a qualifying pair and do not delete evidence.

## Why this is the next test

[EXP-511](2026-09-09-exp511-direct-curve-coverage.md) gave us a complete,
audited finite grid but no qualified sampled fold bracket. Seven samples
were censored by time, while two other samples reproduced the collapsed
input tangent. We must separate observation-window limitations from genuine
return-domain or finite-curve coverage changes before claiming either.

The new diagnostic will explicitly combine 33 unchanged EXP-511 samples
with seven extended samples. It does not reset or relabel EXP-511. The two
collapsed inputs remain rejected. Any new opposite-sign endpoints still need
event-sheet continuity and actual fold qualification before receiving a
critical symbol; a bracket spanning a grazing discontinuity is not a fold.

## Evidence contract and next action

See the [prospective protocol](../experiments/EXP-512-censored-return-extension.md).
Limits are 28 IVPs, 900 seconds and 512 MiB total output, including final
summary. Initial/continuing free-space requirements are 9/8 GiB, with a
1 MiB failure reserve and exclusive one-attempt marker. Every new guard/main
mesh and main dense polynomial is retained and must pass raw replay.

Manifest SHA-256: `bb37c10e80f31745425c6fe8cc5ba9e8ab967ff553a64bbe21f9e4cc7739aa84`.
The source closure contains 117 paths; the actual copied consumer uses 128
source/input files. Preflight startup and control replay receipts are in
`artifacts/EXP-512/`.

Next: freeze and push the exact tested source, run the bounded matrix,
then audit and publish its complete outcome. Jones's chains remain unresolved.
