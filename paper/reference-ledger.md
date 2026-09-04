# Reference ledger

Last updated: 2026-09-04

This is the human-readable companion to `references.bib`. “Verified” means
that title, author list, venue, year, pages/article number, and DOI or arXiv ID
were checked against a primary publisher or repository record. It does not mean
that every scientific claim in the work has already been independently read
and assessed.

| BibTeX key | Why it matters | Requested by | Metadata verification | Planned manuscript use | Full-text status |
|---|---|---|---|---|---|
| `rossler1976equation` | Defines the Rössler flow | Baseline | Elsevier/ScienceDirect record and DOI | Introduction; mathematical objects | Bibliographic record verified |
| `teschl2012ordinary` | Liouville's determinant formula and Floquet theory show why full-flow multipliers cannot vanish on a regular finite-period orbit | 2026-09-04 mathematical audit | Author-hosted AMS book PDF; title, author, series, volume, publisher, and year verified | Mathematical objects; distinction between scalar-model criticality and full-flow stability | Relevant Floquet discussion and equation (3.122) checked |
| `holmes1984bifurcation` | Establishes the high-period obstruction to treating a two-dimensional horseshoe return map as globally logistic | Referee B | Elsevier/ScienceDirect record and DOI | Introduction; prior work; limitations | Bibliographic record verified; close reading pending |
| `lefranc1994combining` | Prior experimental use of kneading/logistic ordering through finite period; blocks a novelty claim for generic finite unimodal ordering | Referee B | APS issue record, PubMed record, and DOI | Introduction; prior work; limitations | Bibliographic record verified; close reading pending |
| `gilmore1998topological` | Defines the template/branched-manifold role and the boundary between a topological invariant and a coordinate-dependent return-map projection | Jones Ref. 12; active partition reconstruction | APS *Reviews of Modern Physics* record and DOI | Mathematical objects; symbolic-test design; limitations | Abstract and bibliographic record verified; full partition convention close reading pending access |
| `metropolis1973finite` | Primary finite-pattern/unimodal-ordering source behind the Figure 6 ordering and zero-insertion target | Jones Ref. 13; active finite-ordering test | Elsevier/ScienceDirect open-archive record and DOI | Symbolic-test design; finite-ordering comparison | Abstract and bibliographic metadata verified; algorithm close reading pending |
| `barrio2011global` | Resolves Jones's incomplete Ref. 6; the source Referee B says must receive credit for identifying the topology-transition line (TTL/TBA) | Referee B | APS *Physical Review E* record and DOI | Introduction; prior work; topology hypothesis | Bibliographic record verified; close reading required for exact attribution wording |
| `jones2012topological` | Original Jones manuscript being reassessed and extended | Project source | arXiv record and local PDF | Introduction; results comparison; discussion | Local PDF in `references/1201.4343v1.pdf` |
| `barrio2012topological` | Independent, near-simultaneous co-discovery of the topology transition's role in periodicity-hub organization; sharper TBA/superstability analysis | Project source | APS/PubMed record, DOI, and local PDF | Introduction; prior work; discussion | Local PDF in `references/BarrioBlesaSerrano-2012-TopologicalChangesinPeriodicityHubsofDissipativeSystems.pdf` |
| `kantz1985repellers` | Primary transient-chaos/repeller and lifetime foundation cited by the Barrio PRL for its saddle computation | Barrio Ref. 13; active method | ScienceDirect journal record and DOI | Methods; saddle qualification | Bibliographic metadata verified; method-specific close reading pending |
| `nusse1989procedure` | Independent PIM-triple route to restrained chaotic-saddle trajectories | Modern validation method | ScienceDirect journal record and DOI | Methods; saddle qualification | Abstract and bibliographic metadata verified; full close reading pending |

## Citation decisions already fixed

- We do not call logistic-like finite ordering new. Holmes (1984) and Lefranc
  et al. (1994) delimit the claim.
- We credit Barrio et al. (2011) before describing the TTL/TBA as a Jones
  result. Exact novelty language remains provisional until a full primary-
  source comparison is complete.
- Jones (2012) and Barrio, Blesa, and Serrano (2012) are described as
  independent, near-simultaneous co-discoveries of the 2012 connection between
  return-map topology change and periodicity-hub/shrimp organization. This does
  not transfer Barrio et al.'s earlier 2011 results to Jones.
- The modern manuscript claims neither global conjugacy to the logistic map nor
  universal high-period ordering. At most it will claim a tested finite
  correspondence on explicitly defined objects.

## Next bibliography expansion

Before the related-work section is considered complete, verify and add the
remaining primary sources behind (i) the homoclinic organization of the hub,
(ii) two-branch/three-branch terminology and its TBA history, (iii) the exact
Rössler partition convention beyond Gilmore's general template framework,
(iv) finite-ordering results beyond the current primary sources, and (v)
post-2012 work that directly tests periodicity hubs. Each entry must be added
here with its role and claim boundary; a raw BibTeX import is insufficient.
