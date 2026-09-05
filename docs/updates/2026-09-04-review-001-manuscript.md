# Review 001: sharpen the claims without losing the symbolic question

Date: 2026-09-04. Branch: `codex/address-review-001`.
Starting source: `f9e6806426f247c1166c0a6bb2396b02883cb7f1`.

## Assessment

The external review concerned the draft before the symbolic explanation was
moved forward. Its main scientific criticism still applies: the existing
local results do not establish the invariant reinjection mechanism connecting
neighboring shrimp. The response keeps that mechanism as the paper's central
question while distinguishing observations, numerical candidates, and proofs.

The [point-by-point response](../reviews/2026-09-04-review-001-response.md)
records accepted criticisms, qualifications, and unperformed tests. It is a
paraphrase; neither the private review nor its embedded citation tokens are
published in the repository.

## What changed

- Defined a scalar return **relation** separately from a regular transverse
  Poincaré map and a genuine quotient. Added the necessary quotient identity
  and a table separating Hopf, flip, homoclinic, scalar-classifier, and
  double-critical objects.
- Described the branch bracket as a finite-horizon scalar classifier result,
  the eleven recovered UPOs as a nonexhaustive library, and the fixed-a
  L2-like path as a surrogate rather than a recovered historical path.
- Preserved the 23-word, 14-relationship source chain and the blank author.
  The symbolic explanation remains Section 3, before methods and results.
  Encoding, finite ordering, and invariant symbolic constructions are distinct.
- Added nine verified references and an eleven-row prior-work comparison.
  The two 2012 studies retain independent co-discovery wording; earlier
  foundations and later numerical, symbolic, and rigorous work receive credit.
- Replaced ambiguous numerical "exact" prose with corrected/analytic/
  discretized terminology. Frozen figure labels and historical identifiers
  remain unchanged and are explicitly qualified.
- Relabeled within-Sobol-net bootstrap ranges and log-rank outputs as
  descriptive sensitivity diagnostics. Independent scrambles, not individual
  dependent points or repeated classifier fits, are replication units.
- Added direct public source, data-release, replay-guide, and movie links to
  the PDF, together with what those archives cannot currently reproduce.
- Added a selected PIM endpoint/horizon table, source-linked CSV, and a
  four-point algebraic check of **both** equilibria. Main claims now state
  the evidence needed for closure, not merely a status label.

## New calculation and its limits

The new [algebraic reporter](../../scripts/report_review001_equilibria.py)
compares the existing NumPy eigensolver with an independent 80-digit Decimal
characteristic-polynomial calculation. It runs no trajectory integration,
continuation, or manifold search and introduces no dependency changes.

At all four declared points, the small equilibrium has one stable and two
unstable directions in forward time; the large equilibrium has two stable
and one unstable direction. The one-real-unstable Shilnikov convention uses
reversed time for the small equilibrium and forward time for the large one.
The positive spectral quantities establish neither a loop nor an equilibrium's
global organizing role. The report is numerical algebra, not interval proof.

The source-bound [JSON report](../../paper/tables/review001-equilibria.json)
has SHA-256
`db6242f620ce019cc6e83e33d7723a8aeafd8e93c55bcfd4231debf313b36fdc`.
The largest binary64 equilibrium residual is `7.42e-14`; the largest
same-Jacobian spectral discrepancy is `6.44e-15`. Regeneration instructions
and selected-table provenance are in [paper/tables](../../paper/tables/README.md).

## What remains unperformed

The [execution priorities](../next-steps.md) retain the symbolic pilot ahead
of further homoclinic point accumulation. It still needs a word-independent
center and a held-out prediction of one reinjection/extra-symbol transition.
Signed invariant-manifold or pruning measurements, archive-wide section
transversality, independent bifurcation formulations, calibrated
independent-scramble uncertainty, and complete public input dependencies
remain open. Both equilibria's global influence is untested.

The homoclinic candidate is not an error-bounded parameter or an existence
theorem. EXP-476 remains failed, with its failed and skipped cases preserved.
No historical acceptance status, receipt, manifest, figure asset, or source
transcription was changed. No paid compute or cloud upload was used.

## Verification and delivery

- Python 3.13.11: **805 tests pass**, including eleven new algebraic checks
  and three new presentation/provenance checks.
- Citation checker: **25 entries, 25 cited keys, 24 required citations,
  18 included sources, and 34 figures** pass.
- Independent reviews checked literature claims, mathematical framing,
  algebra, source provenance, and public replay scope. They caught a residual
  bound that applied only to one comparison, and a caption calling all
  parameter-space objects curves; both were corrected. The algebraic JSON
  regenerated byte-for-byte in the current environment.
- The LaTeX build has no warnings or overfull/underfull boxes. The PDF has
  69 pages: 19 main-article pages, then the supplement and references.
  All pages were rendered and visually checked; new tables and archive links
  received higher-resolution inspection. Figure 2 is on page 7, and its
  explanation starts on page 5. Ten figures remain in the main article and
  24 in the supplement.
- Local PDF SHA-256:
  `f0f42f2ba807bfbe323adce8315369cf8d6a938d97efe659b253509af12f1625`.

This checkpoint updates manuscript source and the local PDF. It does not
publish or replace any PDF release. The older `manuscript-symbolic-v1`
release remains a draft with the previous layout; public PDF publication
remains pending approval. Published research checkpoints are unchanged.
