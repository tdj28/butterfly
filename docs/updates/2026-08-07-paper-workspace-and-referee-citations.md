# Paper workspace and referee citations

Date: 2026-08-07
Status: manuscript scaffold and citation gate verified

## What changed

The project now has a `paper/` workspace that grows in parallel with the
research. The first manuscript draft already contains the model equations,
precise object/terminology boundaries, computational methods, established
results through the period-640 child, open topology tests, limitations, a
plain-language conclusion, and a claim/evidence/limitation appendix.

The bibliography resolves all sources explicitly named by Referee B. Jones's
incomplete Ref. 6 is Barrio, Blesa, Serrano, and Shilnikov, *Physical Review E*
**84**, 035201 (2011), DOI `10.1103/PhysRevE.84.035201`. The Holmes (1984) and
Lefranc et al. (1994) references are also present with publisher-verified
metadata. Jones (2012), Barrio, Blesa, and Serrano (2012), and Rössler (1976)
complete the initial required set.

The manuscript credits the 2011 foundation explicitly and describes the two
2012 papers as independent, near-simultaneous co-discoveries of the connection
between return-map topology change and periodicity-hub/shrimp organization.
It does not claim that generic finite logistic ordering was new, and it does
not use global logistic conjugacy.

## Verification

- `python3 scripts/check_paper_references.py` passes with six BibTeX entries,
  six cited keys, and six required citations.
- `latexmk -pdf -cd paper/manuscript.tex` produces a six-page draft with all
  citations resolved.
- All six rendered pages were visually inspected. No text is clipped or
  overlapped; the appendix table was changed to ragged-right flexible columns
  after the first render exposed poor word spacing.

## What this does not close

Bibliographic presence does not close RVR-002. Holmes (1984), Lefranc et al.
(1994), and Barrio et al. (2011) still require claim-level close reading, and
the full primary-source novelty matrix still has to cover the homoclinic
foundation, template literature, and post-2012 hub research.

Likewise, manuscript prose does not close RVR-003 through RVR-007. The global
two/three-branch oracle, finite `L1`/`L2` ordering test, reinjection observable,
replacement unfolded-spiral figure, and cross-flow generalization remain
experimental gates.

## Next execution items

1. Complete claim-level reading of the three referee-mandated sources and
   publish the primary-source novelty matrix.
2. Freeze the return section, invariant domain, coordinate, and uncertainty
   rules for RVR-003 before scanning the branch-transition curve.
3. Add each verified post-2012 source to `paper/reference-ledger.md` as it
   becomes relevant; raw bibliography imports are not accepted.
