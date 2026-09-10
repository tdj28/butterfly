# Paper workspace

This directory contains a readable main article followed by a detailed technical
supplement in the same PDF. The main article tests the symbolic reinjection
explanation for Rössler periodicity hubs: whether an extra inner return
predicts the connections between neighboring windows. It presents the chain
before methods and numerical results, separating supported local ingredients
from the mechanism still open. The supplement preserves the numerical
record, including failed experiments and corrected interpretations.

## Start here

- Build the current PDF using the commands below. Public PDF publication is
  pending approval. The earlier `manuscript-symbolic-v1` draft contains the
  previous layout, not this mechanism-first revision; published research
  checkpoint PDFs remain unchanged as historical artifacts.
- [`manuscript.tex`](manuscript.tex) builds the combined article and supplement.
- [`sections/01-introduction.tex`](sections/01-introduction.tex) introduces the
  question and historical context.
- [`sections/02-mathematical-objects.tex`](sections/02-mathematical-objects.tex)
  defines the measurements and includes a short vocabulary table.
- [`sections/05-topology-tests.tex`](sections/05-topology-tests.tex) introduces
  the symbolic alphabet, reinjection/zero-insertion explanation, and full
  source-derived chain diagram through period seven, before the methods and results.
- [`sections/04-results.tex`](sections/04-results.tex) starts with the local
  alphabet and unresolved critical-word tests, then assesses the geometric
  and orbit ingredients. Evidence from separate slices is not a joined chain.
- [`sections/06-discussion.tex`](sections/06-discussion.tex) summarizes what the
  evidence changes for the original claims and what would close each open claim.
- [`sections/08-data-availability.tex`](sections/08-data-availability.tex)
  links the public source, versioned data subsets, replay guide, and movie,
  and states what is not yet publicly reproducible.
- [Review 001 response](../docs/reviews/2026-09-04-review-001-response.md)
  explains which external criticisms were accepted, qualified, or require new
  research; it does not reproduce the private review.

The main article now includes thirteen central figures. It uses
rounded coordinates where extra digits do not help interpretation; the technical
record retains the full numerical values and acceptance criteria.
The current draft's title-page author and PDF author metadata are deliberately
blank. Historical citations still credit Jones and the other original authors.
The main article is followed by the technical supplement and references.
The chain is Figure 2; its explanation starts in Section 3, before methods
and results. Page numbers depend on the current build.
The title, abstract, opening results, claims table, and conclusion all frame
the symbolic reinjection prediction as the central test. Numeric section
filenames retain their historical names; `manuscript.tex` sets reading order.

## Technical supplement

The reader guide at [`sections/s00-reading-guide.tex`](sections/s00-reading-guide.tex)
links to the following appendices and their PDF page numbers:

- [`sections/s01-numerical-methods.tex`](sections/s01-numerical-methods.tex):
  shooting, continuation, orbit identity, Floquet calculations, and saddle methods.
- [`sections/s02-experiment-record.tex`](sections/s02-experiment-record.tex):
  the full experimental sequence and its historical figures; the symbolic
  supplement adds the EXP-483 support diagnosis.
- [`sections/s03-symbolic-tests.tex`](sections/s03-symbolic-tests.tex): source
  transcription, operational symbols, failed center searches, and remaining tests.
- [`sections/s04-interpretation-record.tex`](sections/s04-interpretation-record.tex):
  how interpretations changed as evidence accumulated.
- [`sections/a-reviewer-closure.tex`](sections/a-reviewer-closure.tex): a readable,
  multipage table mapping referee concerns to current evidence and open tests.
- [`sections/s05-prior-work.tex`](sections/s05-prior-work.tex): a source-level
  comparison with earlier and later work, defining the present contribution's limits.
- [`sections/s06-equilibrium-checks.tex`](sections/s06-equilibrium-checks.tex):
  both equilibrium spectra at four declared points, with an explicit
  time-direction convention and a source-replayable algebraic check.

[`tables/README.md`](tables/README.md) documents the new algebraic report and
selected PIM classifier endpoint table. These additions do not close the
remaining campaign-wide raw-data or invariant-mechanism requirements.

The long experimental sections retain chronological statements such as “next”
or “at this stage.” Their meaning is historical. The main article and its
claim summary state the current conclusions. This preserves the audit trail
without requiring a reader to reconstruct the whole chronology first.

## Figures and references

All **31 earlier scientific figures** remain. Independent-homoclinic,
accuracy-grid, symbolic-chain, support-diagnostic, direct-return-geometry
and recovered-fold/response figures bring the total to **39**: thirteen in the
main article and 26 in the supplement. Supplementary figures use S-prefixed
numbers, while asset filenames and generation receipts keep their stable
historical identifiers. No scientific image or figure receipt was changed by
the narrative reorganization; EXP-475 and EXP-476 add separate new figures.
The symbolic-chain redraw uses all 23 words and 14 attributed relationships
from the frozen Jones Figure 6 transcription. Its styles preserve the original
evidence categories; it is not a new numerical validation of those arrows.

The EXP-483/484 additions distinguish a sampling bottleneck from local
flow-geometry accuracy. All 80 declared points pass the direct-return checks;
no invariant curve, critical letter or chain arrow is thereby verified. The
direct-return comparison is Figure 3; the full support comparison is Figure S25.
These figures regenerate from their public compact receipts without raw
target integrations. The PDF author remains blank, and public PDF publication
still requires separate approval.

EXP-517 adds a local-fold recovery figure: all four history/direction
constructions and both solvers recover the same full-state reference under
unchanged numerical gates. This is a calibrated local ingredient, not a
verified C/D dictionary or Jones chain. The failed original eighth-return
representation remains explicitly failed.

EXP-518 then tracks those four constructions through both remaining parameter
steps. Its supplementary figure puts successful transport beside the failed full-state
cycle-contact test: all sixteen x projections pass, but all full-state
comparisons fail. Neither contact nor a symbolic chain is inferred. The
new figure is generated from the audited public receipt; it is not a fitted
or hand-drawn interpolation of the evidence.

EXP-519 then resolves that local mismatch using a fresh four-point response
and one prescribed correction. All 513 integrations audit, and all sixteen
full-state contact and prediction checks pass. The new Figure 5 shows every
stencil point, the explicitly reused failed anchor and the corrected endpoint.
The earlier transport figure is preserved in the supplement rather than
adding another chronological stop to the main narrative. No second critical
point or symbolic chain is inferred from this single local contact.

[figures/README.md](figures/README.md) lists regeneration commands and source
hashes. [supplement/](supplement/) contains the existing animation materials.
The homoclinic-continuation asset named `fig30` is the **EXP-472, 80-point
snapshot**; the subsequent EXP-473 point is described in the text. The apparent
local turn remains a sampled numerical feature requiring parameter-sensitive
error control and an independent formulation.

[`references.bib`](references.bib) holds the bibliography;
[`reference-ledger.md`](reference-ledger.md) records each source's role and
verification status. [`required-citations.txt`](required-citations.txt) protects
required sources from accidental removal. The citation checker follows all
included main and supplemental sources and verifies figure paths.

## Build and check

From the repository root:

```sh
.venv/bin/python scripts/check_paper_references.py
.venv/bin/python scripts/render_quadratic_control_table.py --verify
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/manuscript.tex
```

The target remains a portable `article` draft. Numerical evidence, rather than
journal formatting, determines when a claim can be promoted.

## Writing rules

1. Define the flow, section, return map, invariant set, and any scalar quotient
   separately. Explain a technical term before relying on it.
2. Put the scientific question, result, and implication in the main article.
   Put chronological solver development and detailed acceptance checks in the
   supplement, without removing negative evidence.
3. Do not use *conjugacy*, *topological invariant*, *branched manifold*, or
   *universality* without stating the mathematical object and its evidence.
4. Treat the two 2012 studies as independent, near-simultaneous co-discoveries
   while crediting earlier foundations and subsequent work explicitly.
5. Distinguish the three cascade paths; integer cycle labels are not flow times,
   scalar-map criticality is not a zero full-flow multiplier, and solver
   agreement is not a rigorous existence proof.
6. Every quantitative result must be traceable through experiment IDs, source
   comments, or the accompanying project record. A figure is not an independent
   validation of its source data.
7. Keep the claim ledger and manuscript consistent. A paragraph or citation may
   fix exposition but cannot close an unperformed scientific test.
