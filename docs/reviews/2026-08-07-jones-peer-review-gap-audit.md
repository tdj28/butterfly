# Jones peer-review gap audit

Date received: 2026-08-07

Source: user-supplied referee reports for manuscript `LN13044/Jones`.

Status: binding research and manuscript checklist

## Bottom line

The present program addresses many weaknesses that the referees did not
explicitly name: solver provenance, orbit identity, branch switching, Floquet
stability, false-family rejection, high-period conditioning, and prospective
prediction. Those are important new strengths, but they do **not** by
themselves close the referees' central concerns.

The principal open referee gaps are:

1. operationally define and continue the two-branch/three-branch return-map
   transition;
2. replace global logistic-map conjugacy with an exact finite-period question
   and report the first disagreement;
3. formulate third-branch reinjection in the return map or with a robust
   invariant, not as a branched manifold deposited in phase space;
4. reconstruct the symbolic `p -> p+1` spiral-unfolding argument in a
   machine-generated, reader-followable figure; and
5. establish novelty by explicit comparison with prior primary literature,
   not by treating logistic-like ordering as new.

No project document or future paper may say that the peer-review gaps are
closed until the acceptance gates below are satisfied.

## Referee A

| Referee concern | Current response | State | Closure evidence required |
|---|---|---|---|
| Novelty was unclear relative to recent work | The project now separates the shared Jones/Barrio-Blesa-Serrano co-discovery from Jones's distinct finite symbolic, mutant-shrimp, and reinjection hypotheses. A systematic primary-source novelty audit is still absent. | Partial | Source-verified chronology and claim-by-claim comparison including the earlier TTL/TBA, homoclinic, logistic-ordering, and experimental literature. State precisely which result is reproduction, correction, or new. |
| Focus on one narrow aspect did not support broad interest | The multi-`b` atlas, basin work, bifurcation surfaces, and high-period cascade broaden the numerical program. Cross-system generality has not been demonstrated. | Partial | Qualify the complete topology pipeline on Rössler, then apply the frozen definitions prospectively to two structurally different flows, retaining negative results. |
| The technical/symbolic tool was promising but not exploited | The numerical engine is now heavily exploited. Figure 6 is transcribed into a versioned target containing 23 words, ten matched arrows, one visual-only arrow, three lower-period relationships, and ten parameter landmarks. Blind EXP-174 classifies the exact printed coordinates: eight are periodic with complete late DOP853/Radau agreement, two remain unresolved, and one initial condition exposes delayed period-14 capture. No computed orbit has yet been assigned a source word under an independently reconstructed partition. | Open | Produce a versioned orbit/branch/symbol database, verify all claimed transitions through period seven, and make at least one held-out symbolic prediction before computing the target orbit. |
| No conclusions accessible to nonspecialists | Current findings documents state claim boundaries, but there is no revised manuscript conclusion or accessible spiral explanation. | Open | A plain-language conclusion, a one-page mechanism diagram, and a claim/evidence/limit table reviewed independently for comprehensibility. |

## Referee B

| Referee concern or request | Current response | State | Closure evidence required |
|---|---|---|---|
| Put the Rössler equation before scan/fixed-parameter choices | This is a manuscript-ordering correction, not a computational problem. | Open until rewrite | Publication checklist verifies equation, variables, parameters, fixed values, scan paths, and section definition before results. |
| Stop using `conjugate` loosely and define the mathematical objects | Project rules reserve conjugacy for precisely defined maps and invariant sets. The AI program uses quotient/semiconjugacy language and allows the one-dimensional hypothesis to fail. | Conceptually revised; empirically open | Define the two-dimensional Poincaré map and invariant domain. Test finite orbit correspondence first. Claim semiconjugacy or conjugacy only after its hypotheses and injectivity/surjectivity scope are established. |
| A two-dimensional return map can reverse infinitely many high-period orderings relative to the logistic map; cite Holmes | The claim ledger has already rejected blanket conjugacy, but the Holmes boundary has not yet been made a computational test. | Open | Add and verify the Holmes source; enumerate Rössler and logistic orbit permutations by period; report the first reversal/disagreement or a verified finite bound. |
| The likely result is one-to-one periodic-orbit correspondence only up to some period | The research plan already targets finite agreement rather than full conjugacy. No complete finite enumeration exists yet. | Open | Machine-generate periodic orbits, canonical symbolic words, permutations, and stability through at least the paper's period seven, then extend until the first mismatch or declared resource bound. |
| Logistic-like ordering of unimodal flows was already known; cite Lefranc and prior work | The project does not treat generic logistic similarity as the distinctive Jones result, but the primary-source bibliography is incomplete. | Open | Verify Lefranc et al. and related primary sources; rewrite novelty around the oscillating branch count, cross-period connections, and reinjection mechanism only where evidence supports them. |
| Clearly attribute the previously identified TTL and complete Ref. 6 | The project uses cautious co-discovery wording for the 2012 hub/transition connection, but the earlier TTL source and Jones Ref. 6 remain to be source-checked. | Open | Recover the exact cited work, define what it established, and distinguish prior TTL identification from the later connection to hubs, shrimp centers, and symbolic transitions. |
| Hopf-to-homoclinic slices looking logistic-like is not surprising | The project treats slice ordering as a finite test, not the main novelty. EXP-153/155 qualify the Hopf-born one-winding family on an explicit fixed-`a=0.1798` `L2`-like reconstruction to the reported hub coordinate. EXP-156 through EXP-173 solve four exact flips and independently qualify stable primitive children through period 16. The source audit finds that Figure 2 draws horizontal `L1` and vertical `L2` examples but prints no exact historical parameterizations. The equilibrium homoclinic connection and symbolic ordering remain unrecovered. | Partial | Publish operational paths with the historical qualifier, compare the two preregistered `L1` interpretations, validate the homoclinic endpoint independently, reconstruct the partition, and show what the selected paths reveal beyond generic unimodal ordering. |
| The branched-manifold language was misleading because the branched manifold is an abstract quotient, not an object deposited in phase space | Current plans explicitly avoid treating a projected deposit angle as a topological invariant. The proposed replacement has not been computed. | Conceptually revised; empirically open | Express the phenomenon first in the return map: invariant domain, critical points, third branch, reinjection coordinate, critical values, and itinerary change. Then test section/coordinate robustness or relate it to a template invariant. |
| Add a return-map figure | EXP-055 supplies one local section-grazing event but not the requested global explanation. | Open | Generate return maps on both sides of the transition and along at least one full spiral rotation with invariant domain, branches, critical points, reinjection, and symbolic partition labeled from data. |
| The spiral-unfolding argument and Fig. 6 were too difficult to follow | No replacement figure yet exists. | Open | Produce a machine-generated unfolded spiral showing parameter arclength/angle, branch count, critical values, orbit points, symbolic words, and `p -> p+1` connections; every panel must bind to experiment receipts. |

## Binding closure gates

### RVR-001 — Terminology and mathematical objects

Define separately the flow, Poincaré section, two-dimensional first-return map,
relevant invariant set, any quotient map, and the finite symbolic comparison.
Ban unqualified `conjugate`, `topological`, `branched manifold`, and
`universality` from the revised manuscript.

### RVR-002 — Attribution and novelty

Verify the earlier TTL/TBA source, Jones Ref. 6, Holmes (1984), Lefranc et al.
(1994), the homoclinic foundation, and the 2012 papers. Produce a primary-
source novelty matrix distinguishing prior knowledge, co-discovery, Jones-only
hypotheses, reproduction, correction, and genuinely new results.

Checkpoint (2026-08-07): Jones Ref. 6 is resolved as Barrio et al., *Physical
Review E* **84**, 035201 (2011). Publisher-verified BibTeX for that paper,
Holmes (1984), and Lefranc et al. (1994) is now required and cited by the draft
under `paper/`. Claim-level close reading, the homoclinic-source expansion, and
the complete novelty matrix remain open, so RVR-002 is not closed.

### RVR-003 — Two-to-three branch return-map oracle

Freeze a Poincaré section and relevant invariant domain. Detect critical points
with uncertainty; distinguish dynamically relevant extrema from projection
artifacts; classify two versus three branches; continue the transition; and
repeat under declared section perturbations. This closes the referee's praised
but insufficiently demonstrated central mechanism.

Checkpoint (2026-08-07): the local control problem is now strong. EXP-108
qualifies both published attracting endpoints; EXP-112/113 qualify the two
regular-window saddles on CPU/GPU; and EXP-115 independently recovers both
saddle topologies with adaptive DOP853/PIM at a fixed 128-return censor
horizon. EXP-116 then preserves both topologies and critical locations at 256
returns with all six access lines resolved and zero integration failures.
EXP-115's 64-return profiles remain a negative support control. EXP-129 then
prospectively matches the frozen signed lower-support prediction to a blind PIM
midpoint and narrows the finite `c=20` bracket to `[0.148125,0.14825]`.
Blind EXP-148 subsequently qualifies `a=0.1481875` as two-branch at both
censor horizons, narrowing the finite bracket to `[0.1481875,0.14825]` and
unlocking the separately frozen prospective lobe-association test.
EXP-130's unresolved-aware transverse discovery then rejects brute finite-
sprinkler continuation at the narrow local controls and selects four explicit
adaptive-PIM endpoint tests at `c=19.8` and `c=19.9` without claiming a curve.
EXP-131 executes those tests and prospectively falsifies the proposed
three/positive endpoint at `c=19.8,a=0.148`, while fully passing the
`c=19.9,a=0.150` three/positive endpoint. This is evidence that the boundary
bends or shifts, not a transverse continuation. EXP-132 then executes the
implied finite brackets at a 256-return horizon under EXP-121's independently
qualified coverage-only censor. It qualifies the complete `c=19.9` bracket
`[0.145,0.150]` and the untouched `c=19.8,a=0.150` three/positive endpoint.
The `c=19.8,a=0.148` endpoint remains failed because three high-bin variants
per coordinate are bootstrap-unstable, despite 12/15 two-branch decisions and
uniformly negative slopes. The full experiment therefore remains failed and
no curve is claimed.
EXP-133 through EXP-135 recover and primitive-identity-audit finite UPO
families on both sides of the `c=20` bracket, supplying the first qualified
orbit seeds for manifold continuation. They do not yet identify the event.
Transition continuation, the underlying manifold event, and reinjection
prediction remain open, so RVR-003 is materially advanced but not closed.

### RVR-004 — Finite logistic-ordering test

Source-audit `L1` and `L2`, publish operational reconstructions, define the
partition independently, and enumerate
orbit permutations, kneading data, critical itineraries, and stability. Verify
every claim through period seven and search prospectively for the first
high-period disagreement predicted by the two-dimensional-map limitation.

Checkpoint (2026-08-07): Figure 2 has now been inspected at figure resolution.
It draws a horizontal `L1` and vertical `L2` but gives no exact equations or
endpoint table. The fixed-`a=0.1798` path is therefore correctly scoped as an
explicit `L2`-like reconstruction, not recovered historical code. Figure 6 is
now a hash-bound machine target with 23 words through period seven, ten matched
`p -> p+1` arrows, one visual-only arrow, three explicit lower-period
relationships, and ten parameter landmarks. The paper does not print a
complete reproducible return-map partition; dynamic symbol assignment,
permutations, kneading data, and comparison remain open.

Checkpoint (2026-08-07, EXP-174): the ten printed parameter landmarks are now
tested blindly at their exact displayed coordinates. All 60 integrations pass
their numerical/crossing gates and every qualified DOP853 label agrees with
Radau for both initial conditions. Eight points resolve periodically at
periods `5,6,8,14,6,5,14,14`; two remain unresolved. The full experiment is
retained as failed because one initial condition at `(0.19368,0.2,8.456)` is
unresolved after an 800-unit transient and period 14 after 1600 units. This
supplies orbit seeds and a transient warning, not a partition or word match.

### RVR-005 — Reinjection without category error

Define the third branch and reinjection in the return map. Compare section
coordinates, branch ordering, winding/linking, and template candidates. A
coordinate-dependent projected angle may be reported only as such. Test whether
the observable predicts `p -> p+1` transitions beyond TBA and homoclinic-sheaf
geometry.

### RVR-006 — Unfolded-spiral evidence product

Replace the original hard-to-follow Fig. 6 with a receipt-bound figure and
caption that lets a reader reconstruct every transition. Include negative or
ambiguous turns rather than selecting only a clean sequence.

### RVR-007 — Exploit and generalize the method

The Rössler exploitation component is materially advanced: EXP-206 qualifies
a 41-point period-6 flip curve, and EXP-211 qualifies an identity-safe
124-point period-12 child-sheet patch with 31 square-root opening fits and
independent solver controls. EXP-212 adds 123 exact pseudo-arclength parent
events and reaches `c=8.40309`; EXP-214 then qualifies a historical-section
grazing without loss of the invariant flip event. Global endpoints and
comparison with the TBA are still open.

After RVR-003 through RVR-006 pass on Rössler, make held-out symbolic and curve
predictions. Then freeze the same definitions on two unlike flows before any
claim about broad dynamical-systems generality.

### RVR-008 — Manuscript exposition

The revised paper must lead with equations and definitions, separate prior art
from new results, explain the mechanism in plain language, and end with a
claim/evidence/limitation table. An independent reader should be able to follow
the unfolded spiral without consulting code.

## Relationship to work already completed

The high-period cascade through a stable period-640 child is valuable reviewer-
responsive evidence: it demonstrates that the modern code exploits exact
periodic-orbit continuation deeply, identifies numerical failure modes, and
makes successful prospective predictions. It strengthens the paper's finite
period-doubling story.

It does **not** close RVR-003 through RVR-006. A deep period-doubling cascade is
not the same object as the oscillating two/three-branch return-map topology,
finite logistic orbit ordering, third-branch reinjection, or the unfolded
spiral mechanism. The execution backlog keeps these workstreams distinct.
