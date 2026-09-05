# EXP-476 result and diagnostic audit

Date: 2026-09-04. This is a post-result review, not an amended target protocol.

## Evidence reviewed

- Clean experiment source `af90d04e6b484733bb2535a453157c4830691a34`, preserved
  by the pre-run `exp-476-protocol` tag and frozen manifest.
- Full raw receipt SHA-256
  `c9818275ed3c585934cdeaa85857b04a5e9a6e1a6400f426a5cbf6e06d5b95bc`.
- Compact summary, figure generation, saved-mesh inspection, 80-digit
  fixed-interval arithmetic, and synthetic quadratic controls.

The raw receipt remains failed: five passes, one failure, three skips. The
original parameter estimates, meshes, controls, gates, and receipt bytes were
not changed. Post-result diagnostics never call an integrator or optimizer.

## Findings and corrections

1. The first plot validator checked the grid outcome and parameter differences
   but trusted control/budget labels printed by the figure. It now validates
   the frozen source and protocol fields, analytic control gates, target
   qualification flags and scalar diagnostics, node-cap failure identity,
   and skipped records. Sixty-eight focused tests protect those statements.
   The corrected validator produces the same scientific image bytes.
2. The compact summary matches every included raw scalar, control, status,
   sensitivity comparison, and input hash. Only the radius `0.01` parameter
   shifts are plotted as qualified. Endpoint comparisons remain unavailable.
3. Independent algebraic reconstruction exactly reproduces all six stored
   maximum residuals and the node accounting: `43,719 + 31,054 = 74,773`,
   above the frozen 48,000 cap. Stopping with fewer than 48,000 stored nodes
   is therefore correct.
4. The 80-digit implementation follows the cubic-Hermite and Lobatto residual
   definitions. It preserves archived binary64 inputs exactly before higher-
   precision arithmetic, rather than treating extra output digits as recovered
   data. Eleven polynomial/control tests pass. This is arbitrary-precision
   arithmetic, **not rigorous interval arithmetic or an error enclosure**.
5. In-memory reevaluation on Python 3.13.11 reproduces all six mesh cases,
   both selected arithmetic cases, and both synthetic controls field-for-field.
   SciPy helper source hashes match. The original diagnostics record their
   Python 3.12.14 execution; metadata differences must not be hidden.
6. Tiny-interval state quantization is a demonstrated possible mechanism,
   not a uniquely established history of the adaptive failure. The failed
   residual persists at 80 digits; intervals outside the chosen `h<1e-10`
   threshold still exceed tolerance. No reclassification or parameter bound
   follows from the inspection.

The first combined local suite passes 734 tests on Python 3.12.14; the
subsequent release-preparation checks are recorded in the execution update.
The citation/figure check finds 16 cited bibliography entries, all 15 required
citations, and 33 figures. The PDF builds without final-pass warnings; all
61 pages were rendered for layout overview, with the changed main-result
pages inspected at higher resolution.

## Publication boundary

The three JSON assets total 8,798,168 bytes. Scoped checks found no common
credential patterns, absolute machine paths, remote endpoints, or private-key
blocks. This is a bounded check, not a guarantee against every possible secret.
Publish them as the separate `research-exp476` checkpoint with checksums and
the updated manuscript. Retain the original protocol revision separately
from the later diagnostic/release-source revision, and leave
`research-core-v1` unchanged.
