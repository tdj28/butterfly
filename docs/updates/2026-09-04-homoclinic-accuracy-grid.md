# Homoclinic accuracy grid

Date: 2026-09-04. Branch: `codex/homoclinic-accuracy-grid`, based on current
`main` at `3f026e0a1558f1c0356a87125337bcb864c0d1b5`.

## Outcome

**EXP-476 failed to complete the accuracy grid: five cases passed, one failed,
and three were skipped.** This is a numerical limitation, not a disproof of
Jones's homoclinic claim. The nearby initial candidate remains supported at
the previously stated coarse precision; the radius trend and fine turn remain
unresolved.

The protocol was committed, pushed, and tagged before the single target run:
`exp-476-protocol` at `af90d04e6b484733bb2535a453157c4830691a34`. Both Python
3.12/3.13 CI jobs passed first. The run took 11.14 seconds on the local CPU and
cost $0 in paid compute. All controls passed. The raw receipt and all six
attempted paths are preserved; later cases have explicit skipped records.

Only radius `0.01` has three qualified tolerances. Its successive shifts in
`a` shrink from `4.89e-9` to `3.93e-10`. At radius `0.005`, the finest case
does not meet the collocation residual criterion before the next mesh would
exceed 48,000 nodes. Its good short-arc replay does not override that failure.
The [new manuscript figure](../../paper/figures/fig32-exp476-homoclinic-refinement.png)
shows all nine outcomes and only the qualified refinement comparison.

Read-only mesh inspection reproduces every saved maximum residual exactly.
It finds tiny intervals on which `z` changes by only a handful of floating-point
increments; dividing these changes by tiny time intervals amplifies rounding
in the derivative residual. This points to arithmetic-sensitive overrefinement,
but the final mesh alone cannot reconstruct its iterative cause. No new orbit
was integrated and no acceptance gate was changed for that diagnosis.

An additional 80-digit reevaluation leaves the failed interval's residual
essentially unchanged (`0.00137928` versus `0.00137929`). It is already present
in the interpolant through the saved nodes. A known quadratic solution
demonstrates how rounding endpoint samples on tiny intervals can create this
effect. This identifies a numerical mechanism worth controlling; it neither
recovers lost digits nor proves the adaptive solver's causal history.

The [experiment record](../experiments/EXP-476-homoclinic-radius-tolerance-grid.md)
contains the hashes, numerical table, diagnostic commands, and interpretation
limits. The next task is to understand and control this numerical limitation
before freezing another accuracy experiment—not to spend more on GPU capacity
or continue toward the turn with unresolved accuracy.

The [post-result review](../reviews/2026-09-04-exp476-result-audit.md) independently
checks the raw/compact agreement, figure labels, mesh arithmetic, and publication
scope. It also reproduces the algebraic diagnostics on Python 3.13.11. The
manuscript builds cleanly with 33 figures on 61 pages; all pages were rendered
for layout review and the new result pages inspected at higher resolution.

## Verification and preservation

The final local suite passes **756 tests** on Python 3.13.11, including 22
release-preparation checks. The CPU reference smoke check and manuscript
citations/figures pass. The release helper has validated the three immutable
JSON inputs, diagnostic cross-links, and final PDF, scanned those explicit
assets for common credential patterns, and prepared checksums without copying
or overwriting them. The [separate EXP-476 release](https://github.com/tdj28/butterfly/releases/tag/research-exp476)
preserves the failed result and diagnostics alongside the current manuscript;
the previous core release remains unchanged.

## Preserved pre-run checkpoint

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

At this pre-run checkpoint, the tighter analytic controls passed and no Rössler
target case had yet been run for EXP-476. Source and protocol were then committed
before target execution. All **655 tests passed**, including 80 pure grid-analysis tests and 33 new
runner failure-injection tests. Tests use synthetic or analytic data rather
than the nine research targets. The manuscript citation/figure checker passes.
No GPU, service credentials, upload, or paid resources are used.
