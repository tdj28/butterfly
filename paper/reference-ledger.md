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

### Targeted post-2012 update (2026-09-04)

This is a first source-checked expansion, not a complete review through 2026.
See the [claim comparison](../docs/reviews/2026-09-04-post-2012-literature.md)
for implications and the essential equation-convention conversion.

| BibTeX key | Role and verification | Reading status / boundary |
|---|---|---|
| `barrio2013spirals` | Homoclinic hub organization and cross-system symbolic scans; author-hosted published chapter, pp. 53–64 and DOI checked | Rössler section and Lorenz/Shimizu–Morioka examples examined; not new mechanisms introduced here |
| `malykh2020homoclinic` | Direct later hub/homoclinic study; published DOI and author-list cross-checked with arXiv and publisher PDF | Equations (1)–(2) and hub/continuation sections read in author preprint; translated parameterization must be converted before comparing numbers |
| `gierzkiewicz2021periodic` | Rigorous period-forcing benchmark; publisher metadata and arXiv author record checked | Abstract and model/parameter statements read; full proof/code audit pending |
| `capinski2017homoclinics` | Interval-validation standard beyond floating-point agreement; SIAM metadata and author preprint abstract checked | Method summary read; proof implementation not yet reproduced |
| `nitta2022verification` | Alternative validated homoclinic method; open Springer article metadata checked | Abstract, assumptions and method outline read; its parameter-independent-equilibrium restriction needs explicit treatment |

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

### Targeted manuscript-assessment corrections (2026-09-04)

The following additions repair specific omissions in the historical and modern
comparison. They are not a completed systematic review through 2026. The source
assessment was treated as recommendations to check, not as evidence in place of
the papers. Only the independently checked claims below enter the manuscript.

| BibTeX key | Verified primary record and reading level | Narrow manuscript use and boundary |
|---|---|---|
| `bonatto2008periodicity` | [Published DOI](https://doi.org/10.1103/PhysRevLett.101.054101), [author abstract and metadata in PubMed](https://pubmed.ncbi.nlm.nih.gov/18764395/); historical method attribution cross-checked in Vitolo et al. (2011), p. 2 | Early periodicity-hub and nested-spiral organization in a nonlinear circuit model. Do not describe this 2008 paper as the experimental observation: Vitolo et al. explicitly distinguish the numerical anticipation from a later experiment. Full 2008 paper close reading remains pending. |
| `barrio2009qualitative` | [Elsevier article record and abstract](https://www.sciencedirect.com/science/article/abs/pii/S0167278909000864), DOI `10.1016/j.physd.2009.03.010`; author list, volume 238, issue 13, pp. 1087-1100 checked | Local/global codimension-one and codimension-two limit-cycle bifurcation analysis predates this audit. The abstract does not establish identity with our particular period-6 branch; full continuation and parameter-convention comparison remains pending. |
| `vitolo2011global` | [Author-hosted published paper](https://empslocal.ex.ac.uk/people/staff/rv211/mypapers/vgg_global_structure_PRE2011.pdf), DOI `10.1103/PhysRevE.84.016216`; equations (1)-(3) and hub/manifold discussion on pp. 1-4 read | Direct predecessor for global Rössler hub organization: folded homoclinic sheaves are tied to saddle-focus manifold geometry. Their folded homoclinic locus is not the folded period-6 flip locus computed here. Uses `dz/dt=(b+z)x-cz` with `b=0.3`, not our constant-forcing convention; parameter numbers cannot be copied directly. |
| `letellier1995unstable` | [Author abstract and metadata in PubMed](https://pubmed.ncbi.nlm.nih.gov/12780181/), DOI `10.1063/1.166076`; title, authors' published initials, Chaos 5(1), pp. 271-282 checked | Systematic low-order UPO extraction, symbolic encoding, growth/pruning rules, and templates are established Rössler-specific prior work. The abstract states `a in [0.33,0.557], b=2, c=4`; it does not reproduce the Jones hub. Full text, exact partition, and encoding conventions remain to be compared before importing words. |
| `galias2025symbolic` | [Elsevier article record and abstract](https://www.sciencedirect.com/science/article/abs/pii/S1007570424005884), [author publication record](https://www.zet.agh.edu.pl/~galias/publ.html), DOI `10.1016/j.cnsns.2024.108403`; journal year 2025, volume 140, article 108403 checked | Combines symbolic UPO search, continuation, and interval arithmetic to prove several thousand periodic windows near the classical case. This is a rigorous window-existence benchmark, not a validation of our hub-specific chain. Author-accepted manuscript introduction was accessible through indexed primary text, but direct PDF access failed certificate validation; full equations and proof implementation have not been audited. Its parameter labels must be converted before any numerical comparison. |
| `igra2025knots` | [Elsevier record](https://www.sciencedirect.com/science/article/abs/pii/S0022039625003171), [author preprint v5](https://arxiv.org/html/2306.04772v5), DOI `10.1016/j.jde.2025.113290`; introduction, theorem statements, equations (1.1)/(1.5), and parameter assumptions read | Analytical chaoticity and symbolic periodic-orbit correspondence are obtained for an idealized trefoil/heteroclinic configuration. The required configuration is not established at our hub or scalar-classifier bracket. The paper switches from the standard constant-forcing equation to an equilibrium-translated convention, so assumptions and parameters require conversion. Full proof audit remains pending. |
| `owen2025error` | [Author preprint v3 and version record](https://arxiv.org/abs/2501.00150v3), [Section 5](https://arxiv.org/html/2501.00150v3); title, author, version and revision date checked | RQMC uncertainty must distinguish dependent points within each randomized net from independent net-level replicates. Existing trajectory bootstrap ranges are descriptive sensitivities, not automatically calibrated population confidence intervals. This citation does not validate our current RMST intervals, require a universal minimum of 20 scrambles, or supply rigorous deterministic error bounds. |
| `xing2023period1` | [ASME article record and abstract](https://doi.org/10.1115/1.4062201), [author bibliography](https://siyuan-xing.github.io/publications/); authors, volume 18, issue 8, article 081008 checked | Semi-analytical implicit-map treatment connects period-1 branches to approximate twin spiral homoclinic orbits. A relevant alternative approach, not a validated existence result or identification of our numerical candidate. Full equations, implementation and parameter correspondence have not been checked. |
| `docarmo2025measure` | [AIP article record and abstract](https://doi.org/10.1063/5.0239023), [author metadata and abstract in PubMed](https://pubmed.ncbi.nlm.nih.gov/39899585/); Chaos 35(2), article 023116 checked | Studies local-maximum return-map densities near hubs in five three-dimensional systems, including Rössler. The density fits assume full ergodicity after rescaling; they do not establish a flow-topological invariant or our symbolic reinjection mechanism. Full cross-system parameter and numerical-method comparison remains pending. |

The strongest novelty boundary is mechanism-specific auditing of the Jones
finite symbolic chain at declared parameters and sections, not the invention
of symbolic Rössler analysis, homoclinic hub organization, numerical
continuation, or large periodic-window libraries. Likewise, high-precision
floating-point agreement is not equivalent to the interval-validated
existence statements in the rigorous-numerics literature.

Two checked follow-up sources are not yet used as manuscript citations:

- Art B. Owen, *Monte Carlo Variance of Scrambled Net Quadrature*, SIAM Journal
  on Numerical Analysis 34(5), 1884-1910 (1997),
  [DOI `10.1137/S0036142994277468`](https://epubs.siam.org/doi/abs/10.1137/S0036142994277468).
  Publisher metadata and abstract checked. It supplies foundational variance
  theory; the added 2025 source more directly addresses the present error-bar
  interpretation.
- Zbigniew Galias, *Is the Classical Rössler Attractor Periodic? A Validated
  Numerical Study*, Chaos 36(5), 053121 (2026),
  [DOI `10.1063/5.0301581`](https://doi.org/10.1063/5.0301581),
  [author abstract and metadata](https://pubmed.ncbi.nlm.nih.gov/42089786/).
  The abstract describes symbol-order-guided window searches extremely close
  to classical parameters while leaving the classical attractor's nature
  open. Full reading is needed before comparing its precise ordering,
  parameter distance, or validation construction with this work.

### Remaining scope

Before the related-work section is considered complete, verify and add the
remaining primary sources behind (i) the homoclinic organization of the hub,
(ii) two-branch/three-branch terminology and its TBA history, (iii) the exact
Rössler partition convention beyond Gilmore's general template framework,
(iv) finite-ordering results beyond the current primary sources, and (v)
post-2012 work that directly tests periodicity hubs. Each entry must be added
here with its role and claim boundary; a raw BibTeX import is insufficient.
The additions above address concrete omissions; they do not close the full review.
