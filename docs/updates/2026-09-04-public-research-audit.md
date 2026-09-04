# Public research audit and corrected priorities

The review found and fixed four numerical acceptance bugs, strengthened public
reproducibility and credential handling, and corrected scientific claims that
exceeded the evidence. The complete [audit](../reviews/2026-09-04-public-research-audit.md)
and [next-step queue](../next-steps.md) now lead the documentation.

## Changes and verification

- `bbef38a`: failed partial basin integrations cannot be labeled periodic;
  escaping trajectories are not counted as bounded attractors; shooting
  acceptance includes phase and arclength constraints. New regressions pass.
- `f3cf626`: finite RunPod cost limits, cleanup for malformed provider prices,
  credential redaction, broader ignore patterns, and a public-file scanner.
  Provider verification is mocked only; no live calls were made.
- `de3bc0b`: source-archive test portability, explicit Pillow dependency,
  included-source citation/figure checks, and Linux Python 3.12/3.13 CI.

The combined local suite passes **461 tests**. CPU reference verification
passes. The manuscript checker finds 11 BibTeX entries, 11 cited keys, all ten
required citations, ten included TeX source files, and 31 manuscript figures.
An independently prepared source archive with a fresh locked environment
passed the reproducibility subset's 411 tests before integration with the
other fixes. The starting archive had three Git-dependent test failures.

The historical credential scan found no matches across 726 commits and 5,309
file blobs for the five local credential values and the declared token/key
patterns. The staged files are separately checked before each commit.

## Scientific corrections

The full-flow Floquet-zero center interpretation is retracted: smooth-flow
monodromy is invertible, and projected scalar-map criticality is a distinct
object. Corrected orbit samples remain intact. The nearby homoclinic candidate
has useful independent solver/radius checks, but its fine sampled turn has no
parameter-error bound. The eighth-birth criticality interpretation needs a
shrinking-amplitude local test. Neither issue establishes a refutation of the
original Jones mechanism.

The abstract and conclusion now explain the results instead of recounting
the execution log. Integer period labels are distinguished from flow return
time and section counts. The README states the bounded, single-initial-condition
atlas scope and the missing public raw-data archive.

## Manuscript and figure QA

The final draft compiles to 51 pages with no undefined references/citations,
warnings, overfull boxes, or underfull boxes in the final log. Rendered pages
1, 3, 11, 39, 48, 49, and 51 were inspected for the abstract, mathematical
definitions, homoclinic figure, criticality caveat, discussion, conclusion,
and references.

The newly named audited birth-criticality image corrects the embedded title
while preserving every numerical metric and all four source-receipt hashes.
The original image and its receipt remain available. Its generation command
is in the [figure index](../../paper/figures/README.md).

```text
manuscript.pdf bytes: 10162881
manuscript.pdf SHA-256:
3308c4e5e162e9755dc430d1e64317cae4e90f8506e89277aa5f4893c3df8aab

audited birth-criticality image SHA-256:
1873c28b26031f33dc21bda9c7901ecf8c669d791743324a3ef6ca2a7630179c
```

## Next

Publish reproducible core evidence and audit the remaining callers of the
fixed numerical gates. Then prioritize an independent homoclinic formulation
with parameter uncertainty, the finite period-seven symbolic comparison, and
a direct manifold-contact/reinjection test. EXP-474 remains frozen and
unexecuted. No paid compute was used for this review.
