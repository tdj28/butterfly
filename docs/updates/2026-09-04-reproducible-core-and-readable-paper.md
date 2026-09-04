# Reproducible core, readable paper, and an independent homoclinic test

Date: 2026-09-04. Branch: `codex/reproducible-research-core`, based on the
merged public-audit PR #3. This checkpoint implements the first parts of the
[agreed research priorities](../next-steps.md); it does not claim that the
global research program is complete.

## What is already checked

- The main article is now approximately 4,100 words, with eight central
  figures, a vocabulary table, and a clear claim summary. The combined draft
  retains all 31 earlier figures and adds the independent homoclinic
  comparison, for **32 figures** and the complete technical record.
  The combined PDF is 60 pages; the main article occupies the first 13.
  The old compressed reviewer table is now readable.
  The LaTeX build has no warnings; all rendered pages were visually checked
  for layout, with close checks of the main narrative and reviewer table.
- Five later primary references have been added and cited. The
  [literature comparison](../reviews/2026-09-04-post-2012-literature.md) records
  their roles and remaining reading work. This is a targeted expansion,
  not a complete review through 2026.
- The canonical/origin-fixed Rössler parameter conversion is implemented and
  tested. It prevents directly comparing our `b=0.2` slice to differently
  parameterized later papers.
- A deterministic, explicitly allowlisted core-data archive and safe verifier
  now support a public replay command. The nine historical data/protocol
  files total 6,629,037 bytes before compression, including the new pilot's
  full record and protocol; source/environment metadata
  and checksums accompany them. Secrets, reference PDFs and machine logs are
  excluded. See the [replay guide](../reproducibility.md).
- The local replay redraws the archived 26,931-point atlas panel, recomputes
  the flip orbit and its six/eight section counts, and reintegrates all 32
  homoclinic arcs. Flip multiplier: `-0.999999888417178`; augmented-flow
  closure: `1.65834e-10`; largest homoclinic arc defect: `1.08861e-9`.
  Each passes its declared reproduction gate. The flip must also remain
  close to the released seed in phase-fixed state and period.

The atlas step redraws existing classifications; it does not integrate the
entire raster again. Candidate replay does not repeat discovery or provide
independent existence validation. Failed historical direct forward replay
remains included in the homoclinic input rather than being hidden.

## New independent method: EXP-475

The pilot changes the homoclinic boundary formulation and discretization:
whole-orbit collocation with eigenspace-projection endpoints, two shrinking
endpoint radii, and free `a` and flight time. The saved path supplies only
an initial guess. This is not AUTO/HomCont and not an independent discovery.

Before target execution, the same formulation recovers the analytic Duffing
connection with damping near zero; each endpoint-radius halving lowers the
measured state error by approximately a factor of eight. A positive-`mu`
negative control fails as required. Bounds, numerical gates, a local CPU
budget, and the stop-on-failure rule are recorded in the EXP-475 manifest.
The source and protocol must be committed before the target run.

**Result: passed**, in 3.04 seconds on local CPU with no retries or tuning,
after source and protocol were committed and pushed as `cf275082`.
All three endpoint-radius cases and the final tolerance-refinement case pass.
The finest estimate is `a=0.18264361203806015`, only `3.86e-9` from EXP-342,
but the refinement changes `a` by `4.06e-8`, versus `4.30e-9` for the last
radius change. The finer result has maximum short-segment replay defect
`1.06e-7`. The measured sensitivity is not a rigorous error bound.
See [EXP-475](../experiments/EXP-475-independent-projected-homoclinic.md)
and its [compact receipt](../experiments/receipts/EXP-475.json).

The remaining caller audit found a missing arclength acceptance condition
and nine unchecked correction sites across seven scripts. These are fixed
with regression tests; historical receipts remain unchanged. A read-only
scan found 360 reported-success matching/arclength records, all below the
`1e-8` gate (largest `2.81e-12`). This is scoped evidence, not a complete
revalidation of every historical result.
See the [caller audit](../reviews/2026-09-04-corrector-caller-audit.md).

The complete local suite passes **542 tests**. The manuscript checker finds
16 bibliography entries, all 16 cited, all 15 required citations, and all
32 included figures. The final LaTeX pass has no warnings.

The initial Python 3.13 CI failure was a malformed-archive test-fixture
incompatibility, not a numerical failure. A portable fixture exercises the
same rejection path; both Linux Python versions pass after the fix.

## Interpretation

This work strengthens reproducibility and makes the story accessible.
It does not yet resolve the fine homoclinic turn, establish the exact printed
Jones coordinate, complete the finite symbolic ordering, or explain every
shrimp. The next mechanism tests remain parameter-sensitive independent
homoclinic validation and the measured manifold/finite-word links.

No paid compute, RunPod host, or credential upload was needed for this phase.

## Source checkpoints

- `03e5b17`: later literature and equation-convention conversion.
- `08a4f1b`: allowlisted bundle, safe extraction and numerical replay.
- `ef7390f`: illustrated main article and technical supplement.
- `84f85b1`: same-seed replay identity safeguards, independently reviewed.
- `cf27508`: prospectively frozen EXP-475 method, controls, and target protocol.
- `e0e1528`: portable Python 3.13 archive-rejection fixture; both CI versions green.
