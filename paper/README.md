# Paper workspace

This directory contains a readable main article followed by a detailed technical
supplement in the same PDF. The main article asks what organizes the Rössler
periodicity windows, explains the measurements, and separates supported local
results from the mechanisms still open. The supplement preserves the numerical
record, including failed experiments and corrected interpretations.

## Start here

- [`manuscript.tex`](manuscript.tex) builds the combined article and supplement.
- [`sections/01-introduction.tex`](sections/01-introduction.tex) introduces the
  question and historical context.
- [`sections/02-mathematical-objects.tex`](sections/02-mathematical-objects.tex)
  defines the measurements and includes a short vocabulary table.
- [`sections/04-results.tex`](sections/04-results.tex) presents the main visual
  argument, with seven central figures and their limitations.
- [`sections/06-discussion.tex`](sections/06-discussion.tex) summarizes what the
  evidence changes for the original claims.

The main narrative is approximately 3,900 words, including captions. It uses
rounded coordinates where extra digits do not help interpretation; the technical
record retains the full numerical values and acceptance criteria.

## Technical supplement

The reader guide at [`sections/s00-reading-guide.tex`](sections/s00-reading-guide.tex)
links to the following appendices and their PDF page numbers:

- [`sections/s01-numerical-methods.tex`](sections/s01-numerical-methods.tex):
  shooting, continuation, orbit identity, Floquet calculations, and saddle methods.
- [`sections/s02-experiment-record.tex`](sections/s02-experiment-record.tex):
  the full experimental sequence and the remaining 24 figures.
- [`sections/s03-symbolic-tests.tex`](sections/s03-symbolic-tests.tex): source
  transcription, operational symbols, failed center searches, and remaining tests.
- [`sections/s04-interpretation-record.tex`](sections/s04-interpretation-record.tex):
  how interpretations changed as evidence accumulated.
- [`sections/a-reviewer-closure.tex`](sections/a-reviewer-closure.tex): a readable,
  multipage table mapping referee concerns to current evidence and open tests.

The long experimental sections retain chronological statements such as “next”
or “at this stage.” Their meaning is historical. The main article and its
claim summary state the current conclusions. This preserves the audit trail
without requiring a reader to reconstruct the whole chronology first.

## Figures and references

All **31 scientific figures** remain in the combined manuscript: seven in the
main article and 24 in the supplement. Supplementary figures use S-prefixed
numbers, while asset filenames and generation receipts keep their stable
historical identifiers. No scientific image or figure receipt was changed by
the narrative reorganization.

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
