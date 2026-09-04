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
[figures/README.md](figures/README.md). The 30-figure collection covers:

- Multi-\(b\) recurrence atlases, a global-to-shrimp zoom, and historical landmarks.
- The Hopf locus, corrected periodic families, and finite period-doubling chains.
- Attracting and chaotic-saddle return maps, critical-point tests, and failed center searches.
- Period-6 flip arms, section grazing, and a sampled period-12 child sheet.
- High-precision correction of the returning cascade, including retraction of a false daughter.
- The nearby homoclinic candidate and its numerical continuation.

Figure 30 is the frozen **EXP-472, 80-point snapshot**. EXP-473 subsequently
adds an eighty-first accepted continuation point, described in the text and
repository record. Its absence from that figure is a snapshot boundary.
The apparent local turn is a feature of the sampled numerical branch;
conditioning-aware parameter errors and an independent formulation remain
necessary to establish its physical location.

The abstract and conclusion summarize the current findings; the detailed
results preserve the experiment sequence and failed checks. A publication
edit should move most chronological solver development into a supplement
while retaining the source receipts and reproducible figure inventory.

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
