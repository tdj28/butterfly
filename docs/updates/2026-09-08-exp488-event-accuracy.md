# EXP-488: tighter tolerances give a mixed result

All twelve integrations completed in 78.17 seconds on the local CPU. No paid
service was used. **The first witness passes; the second remains unresolved
under the complete frozen refinement criterion.** EXP-486/487 are unchanged.

| Witness (b=.2, c=7.212) | Accepted crossings, all six profiles | Largest fine-pair scaled-state difference | Fine pairs passing |
| --- | ---: | ---: | ---: |
| a=.21575 | 7 | 5.272e-8 | 6/6 |
| a=.21577 | 9 | 1.156e-6 | 3/6 |

The state threshold was 1e-7, ten times stricter than EXP-487; time threshold
was 1e-9. Every profile passed count, transversality, residual and uncertain-
extremum checks. Every pair passed timing. The second case's state disagreement
involves Radau at rtol=1e-12. At rtol=1e-13 the two solvers agree to 1.336e-8,
but selecting that favorable pair would violate the all-fine-pairs criterion.
All three DOP853 tolerance profiles produced identical accepted event data
at the fixed 0.001 maximum step; tolerance labels alone do not guarantee a
different numerical trajectory or an independent accuracy check.

The old coarse EXP-486 Radau event was retained as a diagnostic, not assumed
exact. Its discrepancies are in every profile's public receipt. Removing it
from the new convergence criterion did **not** automatically rescue the second
case. These are floating-point consistency measurements, not error bounds.

## Scientific implications

We have a real missed-crossing mechanism and remaining near-grazing numerical
sensitivity. We cannot replace the failed left-region folds with repaired folds
or assign symbolic letters. Next solve the plane residual and its time derivative
simultaneously, then test for a crossing-pair birth/death on the two sides.
A section tangency would explain a discontinuity in the selected return event;
it would not by itself refute Jones's symbolic proposal.

## Evidence

- [Prospective design](../experiments/EXP-488-event-accuracy.md), with counts,
  tolerances, pairwise tests, controls and failure limits fixed first.
- Source freeze `7649f93103d60a829df261876fff71eb00b60d32`, pushed and matched
  against the live remote before targets.
- Raw run `artifacts/EXP-488/target-7649f93`; summary SHA-256
  `6e94e8283f3db0bf1950d4d8a35c1c4db3f30dad80caac1aacb1f417617895b1`.
- [Full audited result](../experiments/receipts/EXP-488-event-accuracy-result.json),
  SHA-256 `5df5b04ae4caace0cbc9f80c701d589361aeab26efc5a505be6b274a84a6d031`.
  The same-agent read-only audit checks source/input hashes, every profile,
  sign-change brackets, separate section algebra, retained raw trajectories
  and exact decision replay. It is not independent peer review.
- Before targets: 1,906 tests passed, one existing Linux-only skip, six
  hidden-crossing controls and six nonlinear analytic accuracy profiles passed.
  The preflight receipt preserves an initial control-output-directory error;
  it consumed no target authority.

Jones's flow-level words and chain arrows remain **unverified, not debunked**.
