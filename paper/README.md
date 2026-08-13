# Paper workspace

This directory is the continuously updated manuscript for the modern
reassessment and extension of Jones (2012). It is intentionally developed in
parallel with the computation, but a result enters the prose as established
only after it has a repository experiment receipt and a matching state in
[`../docs/claim-ledger.md`](../docs/claim-ledger.md).

## Files

- [figures/](figures/) contains the visual argument and generation receipts.
- [supplement/](supplement/) contains Supplemental Movie S1, the animated
  multi-\(b\) parameter-plane atlas.

- [`manuscript.tex`](manuscript.tex) is the compile entry point.
- [`sections/`](sections/) holds the paper prose in reviewable units.
- [`references.bib`](references.bib) is the authoritative project bibliography.
- [`reference-ledger.md`](reference-ledger.md) records why each source matters,
  where its metadata was verified, and where it should be cited.
- [`reviewer-traceability.md`](reviewer-traceability.md) maps the original
  referee objections to manuscript text and scientific closure gates.
- [`required-citations.txt`](required-citations.txt) lists citations that may
  not disappear from the manuscript during editing.
- [`../scripts/check_paper_references.py`](../scripts/check_paper_references.py)
  checks the BibTeX/citation/required-source contract.

## Build and check

From the repository root:

```sh
python3 scripts/check_paper_references.py
latexmk -pdf -cd paper/manuscript.tex
```

The current target is a portable `article` draft. Journal formatting comes
only after the scientific closure gates are satisfied.

## Visual build

The figure-generation commands and source hashes are recorded in
[figures/README.md](figures/README.md). The manuscript currently contains 17
figures: the multi-\(b\) superstructure, a global-to-shrimp zoom, the Hopf
locus and connected family, cascade and return-map controls, the dense
period-6 corrected-orbit fields, scale-aware two-critical audits, the lower-c
stable strip, its refined real-minus-one Floquet edge, and the dense coupled
continuation of that edge, followed by independent qualification of three
primitive stable period-12 children.

## Writing rules

1. Define the flow, section, return map, invariant set, and symbolic quotient
   separately.
2. Do not use *conjugate*, *topological*, *branched manifold*, or
   *universality* without a precise mathematical object and a passed test.
3. Cite prior work at the first statement of prior knowledge. The two 2012
   papers are described as independent, near-simultaneous co-discoveries of
   the return-map topology transition's role in periodicity-hub organization.
4. Label open mechanisms as hypotheses. A deep cascade is not evidence that
   the two/three-branch, reinjection, or unfolded-spiral mechanisms are closed.
5. Every quantitative result names its experiment IDs in the source comments
   or the accompanying project record.
6. Negative results, failed gates, and section/coordinate dependence remain in
   scope; they are not edited away to improve the narrative.
