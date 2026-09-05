# Homoclinic accuracy grid

Date: 2026-09-04. Branch: `codex/homoclinic-accuracy-grid`, based on current
`main` at `3f026e0a1558f1c0356a87125337bcb864c0d1b5`.

## Pre-run checkpoint

The next [planned study](../plans/2026-09-04-homoclinic-refinement.md) is now
implemented as [EXP-476](../experiments/EXP-476-homoclinic-radius-tolerance-grid.md):
three radii by three collocation tolerances, with separate technical,
discretization and endpoint-resolution outcomes.

Independent pre-run review identified orchestration gaps: a clean worktree
did not guarantee that the selected manifest was committed; per-case time
limits omitted seed construction and replay; and replay exceptions could
lose a previously computed path. v2 closes these paths, refuses nonfinite
passing evidence, and requires an actual numerical negative-control rejection.
The old frozen evidence is unchanged.

The tighter analytic controls pass. No Rössler target case has yet been run
for EXP-476; source and protocol will be committed before target execution.
All **655 tests pass**, including 80 pure grid-analysis tests and 33 new
runner failure-injection tests. Tests use synthetic or analytic data rather
than the nine research targets. The manuscript citation/figure checker passes.
No GPU, service credentials, upload, or paid resources are used.
