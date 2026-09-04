# Reproducible core, readable paper, and an independent homoclinic test

Date: 2026-09-04. Branch: `codex/reproducible-research-core`, based on the
merged public-audit PR #3. This checkpoint implements the first parts of the
[agreed research priorities](../next-steps.md); it does not claim that the
global research program is complete.

## What is already checked

- The main article is now approximately 3,850 words and **12 pages**, with
  seven central figures, a vocabulary table, and a clear claim summary.
  The combined **59-page** draft retains all **31 figures** and the complete
  technical record. The old compressed reviewer table is now readable.
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
  now support a public replay command. The seven historical data/protocol
  files total 4,991,221 bytes before compression; source/environment metadata
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
measured state error by approximately a factor of eight. A positive-damping
negative control fails as required. Bounds, numerical gates, a local CPU
budget, and the stop-on-failure rule are recorded in the EXP-475 manifest.
The source and protocol must be committed before the target run.

Target execution and the clean-release publication receipt will be recorded
below when completed; no unperformed target result is claimed here.

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
