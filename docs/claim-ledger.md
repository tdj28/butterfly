# Scientific claim ledger

Last updated: 2026-08-06

This ledger separates the paper's claims from current conclusions. Literature
assessments in the dated review are research leads until their primary sources
are independently verified.

| ID | Claim | Current state | Recovered-code coverage | Required acceptance test |
|---|---|---|---|---|
| CLM-001 | A primary periodicity hub and nested spirals exist for the Rössler system at fixed `b = 0.2` in the `(a,c)` plane. | Original claim; reported as externally supported, source verification pending | Partial: an MPI period-map kernel exists | Reproduce the hub with two independent integrators; publish convergence, horizon, and basin tests |
| CLM-002 | The proposed hub center near `(a,c) = (0.1798,10.3084)` has a saddle-focus equilibrium. | Analytically checkable | Not implemented | Recompute equilibria and eigensystem at controlled precision and test a neighborhood |
| CLM-003 | That parameter pair is a homoclinic point, and is the unique such point on the stated transition segment. | Original claim; unestablished | Absent | Continue stable and unstable manifolds as a boundary-value problem; validate an intersection and define the domain in which uniqueness is asserted |
| CLM-004 | A codimension-one curve separates two-branch/unimodal and three-branch/bimodal return-map regimes and is explicitly connected to periodicity-hub/shrimp organization. | Shared 2012 advance: independent, near-simultaneous Jones and Barrio-Blesa-Serrano co-discovery, building on a reported common 2011 foundation that remains to be source-checked | Absent | Define the Poincaré map and branch criterion operationally; continue the transition curve and test section robustness |
| CLM-005 | The left side of the hub follows the Andronov-Hopf curve and admits specially oriented Hopf-to-homoclinic slices. | Distinctive Jones claim; not developed in the Barrio-Blesa-Serrano PRL | Absent | Continue the Hopf curve, publish exact path parameterizations, and quantify the geometric relationship |
| CLM-006 | Stable windows along the selected slices follow logistic-map ordering through period seven. | Distinctive Jones finite-range claim; heuristic rather than a proved conjugacy | Absent | Define the quotient/return map and symbolic partition; continue every orbit and compare permutations, kneading data, and Floquet multipliers |
| CLM-007 | The finite ordering probably persists to substantially higher periods. | Speculation | Absent | Enumerate and validate increasing periods; report the first disagreement or a justified bound |
| CLM-008 | Shrimp centers on the transition curve are doubly superstable because both critical points belong to the orbit. | Overlapping Jones and Barrio-Blesa-Serrano result; the PRL supplies a sharper TBA/superstability geometry | Absent | Solve both critical-orbit conditions simultaneously and continue their intersections |
| CLM-009 | “Mutant shrimp” connect lower- and higher-period regions across the transition. | Distinctive Jones descriptive claim | Period labels only; no connectivity analysis | Continue the relevant periodic-orbit families and bifurcations instead of inferring connectivity from pixels |
| CLM-010 | Rotation of third-branch reinjection organizes the nested spiral and the `p -> p+1` transitions. | Distinctive Jones, potentially novel hypothesis; no counterpart identified in the PRL | Absent | Define a reproducible reinjection observable, test coordinate/section dependence, and compare it against homoclinic-sheaf alternatives |
| CLM-011 | The inter-period symbolic transitions shown through period seven are correct. | Distinctive Jones claim; different in scope from the PRL's fixed-period local symbolic partition; one Jones transition was visual-only | Absent | Generate symbols algorithmically from a published partition and verify each transition through orbit continuation |
| CLM-012 | The hub drifts robustly as `b` varies from `0.2` to `2.0`. | Original under-documented claim | `b` is configurable, but no three-parameter study exists | Continue the transition surface and relevant bifurcation curves in `(a,b,c)`; detect folds and topology changes |
| CLM-013 | A `5000 x 5000` finite-time period scan reliably classifies periods through 11. | Original computational claim; reliability not established | Partial: checked-in code hard-codes `500 x 500` and classifies through 11 | Rebuild the classifier, establish false-classification rates, separate unresolved/chaotic/escaping/quasiperiodic states, then perform resolution studies |
| CLM-014 | The relevant Rössler dynamics are fully topologically conjugate to the logistic map along qualifying slices. | Revised: wording is too strong and the mathematical objects were not defined adequately | Absent | First test for a normally attracting one-dimensional invariant graph or quotient; pursue semiconjugacy/conjugacy only if its hypotheses are verified |
| CLM-015 | The topology-change/TBA curve remains well defined inside regular shrimp windows through nonattracting chaotic saddles. | Barrio-Blesa-Serrano result, verified as a claim of the local PRL; not a Jones result | Partial: EXP-012 resolves long chaotic-transient capture into period-6 and period-8 windows, but does not compute the invariant saddle | Reproduce chaotic saddles with the sprinkler method or a stronger saddle-computation method and compare their return-map topology with nearby attractors |
| CLM-016 | The TBA curve passes through each principal doubly-superstable point and is tangent there to the `s+` superstability curve. | Barrio-Blesa-Serrano result, verified as a numerical/theory-backed claim of the local PRL | Absent | Continue TBA, `s+`, and `s-`; solve the double-critical condition and measure tangency with uncertainty |
| CLM-017 | Chaotic attractors and chaotic saddles on the same side of the TBA have the same return-map/template topology. | Barrio-Blesa-Serrano result, verified as a claim of the local PRL | Absent | Define a topology classifier and compare attracting/nonattracting invariant sets over representative and boundary-near parameter samples |
| CLM-018 | The spiral/unimodal and screw/bimodal transition appears in an experimental Rössler-type circuit. | Barrio-Blesa-Serrano empirical result, verified as a claim and figure in the local PRL | Not applicable to recovered numerical code | Obtain underlying data if possible or treat the published circuit return maps as external corroboration; do not claim independent experimental reproduction |
| CLM-019 | Stable period-12 and period-3 attractors coexist at `(a,b,c)=(0.245,0.2,5.75)` in the expanded high-`a` atlas. | Newly reproduced numerical finding: distinct periods persist through transient 19,200, both cycles pass closure/Floquet stability gates, and all 57,344 EXP-019 uncertainty pairs resolve into one of the two cycles. The four smallest sampled scales form a disclosed post-result power law with `alpha=0.3733` and `R^2=0.9983`, making the boundary a fractal candidate rather than a proved dimension estimate. | EXP-015 through EXP-019 | Prospectively extend the small-scale fit; test added regions/seeds/horizons and a CPU subset; recover both cycles by shooting/collocation; continue both families and independently interval-validate selected orbit data. |

## Current scientific positioning

The safest working hypothesis is layered rather than exclusive:

1. Local saddle-focus structure supplies a plausible setting.
2. Shilnikov homoclinic organization may supply the global skeleton.
3. The return-map branch transition may organize shrimp centers.
4. Reinjection geometry may explain detailed symbolic connections within that
   skeleton.

The co-discovered 2012 advance is item 3's explicit connection to
periodicity-hub/shrimp organization. Items 1-2 have earlier foundations to be
source-checked; item 4 and the Hopf/logistic-slice construction are distinct
Jones extensions.

The project should test whether item 4 is measurable, robust, and explanatory;
it should not assume that item 4 replaces items 1-3.
