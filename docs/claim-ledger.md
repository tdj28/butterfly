# Scientific claim ledger

Last updated: 2026-08-13

This ledger separates the paper's claims from current conclusions. Literature
assessments in the dated review are research leads until their primary sources
are independently verified.

| ID | Claim | Current state | Recovered-code coverage | Required acceptance test |
|---|---|---|---|---|
| CLM-001 | A primary periodicity hub and nested spirals exist for the Rössler system at fixed `b = 0.2` in the `(a,c)` plane. | Original claim; reported as externally supported, source verification pending | Partial: an MPI period-map kernel exists | Reproduce the hub with two independent integrators; publish convergence, horizon, and basin tests |
| CLM-002 | The proposed hub center near `(a,c) = (0.1798,10.3084)` has a saddle-focus equilibrium. | Verified locally at the reported coordinate: EXP-001's analytic equilibria and Jacobian give the small equilibrium `(0.003489598512,-0.019408223091,0.019408223091)` with eigenvalues `0.0889667722 +/- 0.9959555077 i` and `-10.3030439458`. This is a two-dimensional unstable spiral plus one strongly stable direction. | Implemented analytic equilibria/Jacobian, finite-difference Jacobian check, vector-field residual test, equilibrium invariance under DOP853, and a hash-bound receipt. | Continue the equilibrium/eigenstructure over a declared neighborhood and locate the Hopf curve; keep homoclinic existence and uniqueness in CLM-003 separate. |
| CLM-003 | That parameter pair is a homoclinic point, and is the unique such point on the stated transition segment. | Original claim; unestablished. EXP-155 shows that the Hopf-born period-1 family is not itself the proposed homoclinic orbit: at the hub it retains period `5.9935437090` and stays at least `10.0310033361` from the small equilibrium. This does not test or reject a distinct equilibrium-manifold homoclinic connection. | No stable/unstable equilibrium-manifold intersection yet; only a negative identification result for the continued period-1 orbit. | Continue stable and unstable equilibrium manifolds as a boundary-value problem; validate an intersection and define the domain in which uniqueness is asserted. |
| CLM-004 | A codimension-one curve separates two-branch/unimodal and three-branch/bimodal return-map regimes and is explicitly connected to periodicity-hub/shrimp organization. | Shared 2012 advance: independent, near-simultaneous Jones and Barrio-Blesa-Serrano co-discovery, building on an earlier reported TTL/TBA foundation that the original referee explicitly required Jones to attribute and complete; the primary source remains to be checked | Strong local invariant-set evidence, not yet a TBA curve: EXP-108 passes attracting controls; EXP-112/113 qualify CPU/GPU saddle controls; EXP-116 passes independent PIM stability; EXP-117 qualifies a blind two-branch saddle at `a=0.140`; EXP-119 qualifies `a=0.150` chaotic/three-branch with a resolution model. EXP-121 prospectively reproduces both saddle controls and qualifies `a=0.145` as two-branch. EXP-122 blindly qualifies `a=0.147` as two-branch. EXP-123/124 expose survivor-conditioning sensitivity at `a=0.148`; blind PIM EXP-125 qualifies its saddle as two-branch, while identical-method EXP-126 and EXP-128 qualify `a=0.1485` and `a=0.14825` as three at both censor ceilings. EXP-127 rejects faster mean capture for the transient extra branch and instead qualifies delayed but bounded capture. EXP-129 prospectively matches a negative signed edge slope to a blind two-branch midpoint at `a=0.148125`. Blind EXP-148 then qualifies `a=0.1481875` as two at both horizons, narrowing the finite bracket to `[0.1481875,0.14825]`. EXP-130 rejects brute finite-sprinkler continuation near that boundary. EXP-131 then prospectively falsifies the finite-sprinkler three/positive prediction at `c=19.8,a=0.148`, while fully qualifying `c=19.9,a=0.150` as three/positive. EXP-132's 256-return successor qualifies the finite `c=19.9` bracket `[0.145,0.150]` and a new `c=19.8,a=0.150` three/positive endpoint; its full gate remains failed because `c=19.8,a=0.148` is bootstrap-unstable. The evidence implies a bent or displaced boundary, but still no curve. EXP-133 through EXP-141 recover, primitive-identity audit, and continue eleven distinct UPO families from the two local endpoint saddles; all persist across the finite bracket with fundamental section identity intact. EXP-142 validates their endpoint manifold seeds; EXP-143's atlas selects four capture-sensitive branches, but prospective EXP-144 rejects every finite-horizon capture contrast under phase, density, and horizon controls. Retrospective EXP-145 finds that a pre-existing unstable lobe is excluded from all two-side PIM saddle profiles and included in all three-side profiles with nested two-dimensional atlas convergence. Prospectively frozen EXP-149 then passes at an untouched midpoint: the blind two-branch saddle excludes the frozen lobe on all six PIM clouds. This rejects simple birth/death, crossing-loss, and the tested capture-timing proxy while supporting lobe inclusion/pruning or reinjection. EXP-107 separately qualifies the Jones historical section locally. | Continue a direct intersection or symbolic-pruning residual, compare sections, and verify earlier TTL attribution |
| CLM-005 | The left side of the hub follows the Andronov-Hopf curve and admits specially oriented Hopf-to-homoclinic slices. | Partially qualified distinctive Jones claim: EXP-153 analytically reconstructs the regular small-equilibrium Hopf locus at `b=0.2` and independently root-checks all 192 points. At `a=0.1798`, the Hopf endpoint is `c=0.5192306256940273`. After EXP-154's preserved administrative failure, unchanged-gate EXP-155 passes 118 one-winding period-1 points from `c_H+0.001` to the reported hub coordinate with six Radau checks. The source audit establishes that Figure 2 draws horizontal `L1` and vertical `L2` examples but prints no exact historical path equations. It also shows that the exact small-equilibrium Hopf point at `c=10.3084` lies at `a=0.0018649211`, outside the displayed `a>=0.1` range, so the visible `L1` is a clipped post-Hopf segment or schematic. The homoclinic endpoint and hub-envelope relationship remain open. | Reusable exact Hopf locus plus phase-conditioned DOP853/Radau period-1 continuation, whole-orbit winding identity, square-root amplitude scaling, Floquet tracking, a machine-readable source transcription, hash-bound receipts, and two-scale figures. | Publish the fixed-`a` path as an operational `L2`-like reconstruction; preregister and compare visible-segment and full endpoint-matched `L1` controls; independently validate or reject the equilibrium homoclinic endpoint; quantify the hub-envelope relationship. |
| CLM-006 | Stable windows along the selected slices follow logistic-map ordering through period seven. | Distinctive Jones finite-range claim; heuristic rather than a proved conjugacy. EXP-155 through EXP-173 now qualify the Hopf-born family and four complete supercritical doublings: exact events at `c=3.1807265333384103`, `4.3100451384813105`, `4.636447200967924`, and `4.7090113823613065`, followed by stable primitive period-2, period-4, period-8, and period-16 children. At `c=4.716`, Radau gives unstable period-8 parent multiplier `-1.2072089`, stable period-16 child multiplier `0.1483902`, period ratio `1.9999996`, winding sixteen, and perturbed-attractor recovery. Finite event-spacing ratios `3.45990` and `4.49812` support accumulation but not universality. This exceeds the finite period range but does not establish its symbolic permutation or kneading ordering. The original referee notes that generic unimodal-flow ordering was already known and requires the scope to respect Holmes-type high-period reversals. | One-winding parent continuation, four exact flips, doubled-cover nullspace switching, phase-invariant child identity, primitivity tests, balanced block-Floquet clustering, DOP853/Radau parity, stability exchange, and attraction recovery through period sixteen. Figure 2/6 source targets are now machine-readable. | Reconstruct the return-map partition; algorithmically compare the 23 transcribed words, orbit permutations, kneading data, and Floquet multipliers through period seven on the operational paths; then search prospectively for the first disagreement. Optimize segmented switching and checkpointed recovery before extending higher children. |
| CLM-007 | The finite ordering probably persists to substantially higher periods. | Speculation | Absent | Enumerate and validate increasing periods; report the first disagreement or a justified bound |
| CLM-008 | Shrimp centers on the transition curve are doubly superstable because both critical points belong to the orbit. | Overlapping Jones and Barrio-Blesa-Serrano result; the PRL supplies a sharper TBA/superstability geometry. EXP-186 shows that one exact printed gray-box coordinate is a qualified period-6 orbit but not a reproducible word center. EXP-187/188 then test and reject a Floquet-only proxy: the finer branch continuation resolves 289 cells and 65 signed zero edges, while its sole coarse stationary-saddle candidate disappears on refinement. EXP-189 qualifies corrected stable period-6 orbits on all 65 zero edges. Direct GPU EXP-190 then finds all 130 candidate/profile maps robustly two-branch, so this complete local Floquet-zero neighborhood cannot supply two distinct critical memberships on the recovered historical x representation. This does not reject double superstability; it rules out the first landmark and Floquet-zero shortcuts. Prospectively executed EXP-191 places the other exact period-6 landmark in a coherent component. EXP-192 independently reproduces both landmarks as period 6 but separates their stable raster components. EXP-194 corrects 58 stable flow orbits across the second component and exposes a representation issue: each historical period-6 orbit has eight phases on Barrio's positive-x section. EXP-195 prospectively requalifies all 58 without changing orbit data. EXP-196 exactly matches CPU/GPU survivor and return-pair counts at two steps and qualifies the three-branch Barrio z-map kernel. Target-word-blind EXP-197 resolves 31 cross-step-consistent three-branch candidates but finds that none of the 58 sampled corrected orbits passes both critical-interval and zero-slope membership gates; its nearest point is `(a,c)=(0.21555,7.372)`. EXP-198 reproduces that center and qualifies 685 dense corrected orbits, but fails its 1,000-point coverage gate; the center's 152-point passing component touches the lower-a boundary. EXP-199 then resolves 126 two-step three-branch candidates on that incomplete field. None passes any direct gate and no same-phase cell brackets both residuals: the first crosses zero, but the second is positive throughout. EXP-200 quadruples support and localizes the disagreement to high smoothing. Prospectively frozen EXP-201 then passes 94/104 candidates under a seven-level smoothing ladder, two RK4 steps, and nested 2,048/8,192 support. Eighty-six have identical transition indices and eight differ by one; every qualified second-critical span is below `0.01680` versus the `0.03` gate. EXP-202 then retains all 94 and one `[7,5]` phase assignment across 12 low-smoothing/support/step views, but no direct point or strict cell passes; the second residual is positive in all 1,128 evaluations (`min=0.019945`). The shallow critical is a qualified finite-data scale object, but the sampled stable field still contains no double-critical center. EXP-203 finds only a bounded stable strip in the lower-c extension. EXP-205 then prospectively refines seven real `-1` Floquet brackets on that strip to `7.63e-11` in `a`, establishing a genuine period-6 flip edge. EXP-206 exact-Jacobian continuation passes all 41 points across `c in [7.16,7.32]`, promoting that edge to a dense sampled orbit-defined curve. EXP-207 fails its eight-point branch-arm gate, but three isolated candidates survive a prospectively frozen independent follow-up: EXP-208 gives three primitive stable period-12 children paired with unstable period-6 parents, with exact 6/8 versus 12/16 section identity and all proper subperiods rejected. EXP-209 then passes seven-point fixed-`c` continuation at all three slices. After EXP-210 documents 16 doubled-parent root collapses, prospectively frozen EXP-211 independently seeds and qualifies all 124/124 cells on a 31-by-4 child-sheet patch with zero fallbacks, 31 square-root exponents in `0.50264--0.50309`, exact section identity, adjacency coherence, and six Radau controls. This establishes a dense regular sampled period-12 sheet, not double-critical membership, a TBA identification, formal continuity, or global endpoints. | Direct critical membership remains absent; the scale-aware audit rejects the sampled stable field while the flip boundary and a dense sampled supercritical child sheet are orbit-qualified | Run the frozen EXP-204 residual replay; continue the period-12 sheet to its endpoints; continue the unstable period-6 family; compare both orbit-defined sets with a future TBA curve |
| CLM-009 | “Mutant shrimp” connect lower- and higher-period regions across the transition. | Distinctive Jones descriptive claim | Period labels only; no connectivity analysis | Continue the relevant periodic-orbit families and bifurcations instead of inferring connectivity from pixels |
| CLM-010 | Rotation of third-branch reinjection organizes the nested spiral and the `p -> p+1` transitions. | Distinctive Jones, potentially novel hypothesis; no counterpart identified in the PRL. The original referee accepted the phenomenon as potentially key but rejected its branched-manifold/phase-space explanation as unclear. | Qualified local prerequisite evidence: after EXP-106's unexpected three-branch result, EXP-107 passes all 105 negative-orientation `x` sensitivity cells across nearby parameters, section offsets, and oracle choices; all 105 independent `z` cells also return three with bootstrap consensus `1.0`. The positive half-plane is not a stable scalar graph, so the evidence is explicitly representation-bounded. EXP-127 freezes a scalar extra-branch observable and rejects faster mean capture at `a=0.148`; that domain has delayed but bounded capture and is not part of the PIM-resolved saddle. The recovered UPO census persists across the local bracket and its phase-resolved seeds validate, but EXP-144 rejects the four atlas-selected finite-horizon capture contrasts as phase/density robust. Retrospective EXP-145 finds a pre-existing UPO escape lobe excluded from every two-side PIM saddle profile but included in every three-side profile under nested full-section distance controls. Prospectively frozen EXP-149 then passes at an untouched midpoint: the blind two-branch saddle excludes the frozen lobe on all six access-line/horizon clouds. This supports lobe inclusion/pruning or reinjection but establishes neither reinjection rotation nor an exact connection. | Define and prospectively test an exact manifold-intersection or symbolic-pruning residual; compare against template/TBA/homoclinic alternatives; generate a replacement unfolded-spiral figure |
| CLM-011 | The inter-period symbolic transitions shown through period seven are correct. | Distinctive Jones claim; different in scope from the PRL's fixed-period local symbolic partition. Source extraction records 23 words, ten state-space/symbol-matched arrows, one visual-only arrow, three explicit lower-period relationships, and ten parameter landmarks. Every printed `p -> p+1` arrow follows the same zero-insertion grammar. Blind EXP-174 then evaluates the exact printed coordinates with no expected labels: all 20 qualified-profile cases agree between DOP853 and Radau, eight landmarks resolve at periods `5,6,8,14,6,5,14,14`, and two remain unresolved. The strict experiment fails because one initial condition changes from unresolved at the early horizon to period 14 later. EXP-176/177 qualify neutral three- and two-branch partitions on the same historical representation. EXP-178/179 identify the higher-coordinate trimodal critical as the likely descendant but fail strict bracket gates. Fresh-trajectory EXP-180 tracks the same feature at 20/21 DOP853 points and 4/5 Radau controls, leaving one support hole. EXP-181 hits both frozen gap predictions but fails a long-time pointwise parity gate. Scientifically unchanged EXP-183 then passes two-step survivor/critical parity, complete attractor capture, and five-return DOP853 audits, qualifying the local operational identity through the gap. After EXP-184's preserved pre-integration receipt-field failure, scientifically unchanged EXP-185 qualifies the source-derived mapping `K1/C`, `K0/D`, `B0/2`, `B1/1`, `B2/0` across two solvers, disjoint segments, both coordinates, and physical deposition geometry without reading a target word. EXP-186 then qualifies the exact second landmark as period 6 with sub-`2.14e-13` closure and step-stable x topology, but z is monotone and the x words `010011`/`C10011` match no frozen target. The exact printed coordinate is therefore rejected as a reproducible word center. | Machine-readable source target and asset audit, solver-qualified recurrence labels at eight approximate landmarks, a non-circular encoder, qualified neutral controls, parity-qualified local identity, an independently qualified alphabet, and one honest exact-coordinate word failure; dynamic arrow validation remains absent | Preserve all failed gates and raster-only box-association limit; locate a superstable center by a target-word-blind dynamical objective, encode it under the immutable partition/mapping, then verify all 11 arrows through orbit continuation |
| CLM-012 | The hub drifts robustly as `b` varies from `0.2` to `2.0`. | Partial new support over a narrower range: EXP-021 shows coherent raster motion for `b in [0.1,0.3]`; EXP-022 corrects stable period-3 and period-5 cycles along moving representative paths in all eleven frames. EXP-023/024 refine three period-doubling seeds. EXP-025 through EXP-040 trace, switch, and locally qualify a folded event surface. EXP-041 decisively reclassifies its apparent doubled-period `+1` event as a fundamental `-1` period-doubling surface at three points. This still does not establish a hub center, transition surface, or behavior through `b=2`. | GPU atlas, shooting/Floquet diagnostics, natural and pseudo-arclength continuation, a coupled multiplier solve, branch switching, invariant-cycle identity, prospective local scaling, a bounded fixed-`c` curve, a 45-point surface patch, and a fundamental-period audit now cover two cross-`b` family candidates and four local stability events. | Continue the flip surface globally and overlay it on atlas-window geometry; continue equilibrium/Hopf and TBA surfaces; define and track a hub center; extend prospectively toward `b=2`; validate selected events independently. |
| CLM-013 | A `5000 x 5000` finite-time period scan reliably classifies periods through 11. | Original computational claim; reliability not established. EXP-213/214 now supply a concrete local failure mode: a standard sign-change counter loses coalescing roots near a grazing and reports six rather than seven phases while the invariant orbit persists. | Partial: checked-in code hard-codes `500 x 500` and classifies through 11; extremum-partitioned event counting repairs one qualified local boundary | Rebuild the classifier, establish false-classification rates, use extremum-aware counts near tangencies, separate unresolved/chaotic/escaping/quasiperiodic states, then perform resolution studies |
| CLM-014 | The relevant Rössler dynamics are fully topologically conjugate to the logistic map along qualifying slices. | Revised and presumptively rejected as a global claim: the original referee identified the two-dimensional return-map obstruction and the absence of correspondence between all periodic orbits. Only a precisely bounded finite correspondence, quotient, or semiconjugacy may survive. | Absent | Define the two-dimensional Poincaré map and invariant set; test finite orbit correspondence and a normally attracting one-dimensional graph/quotient; report the first failure; use conjugacy only if bijection and all stated hypotheses are actually established |
| CLM-015 | The topology-change/TBA curve remains well defined inside regular shrimp windows through nonattracting chaotic saddles. | Barrio-Blesa-Serrano result, verified as a claim of the local PRL; not a Jones result | Published controls and independent PIM pass; EXP-117 qualifies `a=0.140` as a two-branch saddle; EXP-119 qualifies `a=0.150` chaotic/three-branch. EXP-121 qualifies `a=0.145` as two-branch, and blind EXP-122 qualifies `a=0.147` as two-branch. EXP-123/124 expose survivor-conditioning and rare-survivor power limits at `a=0.148`; blind PIM EXP-125 qualifies it as two-branch, while identical-method EXP-126/128 qualify `a=0.1485/0.14825` as three at two censor ceilings. EXP-127 explains the transient conditioning split through delayed but bounded extra-branch capture. EXP-129's held-out signed prediction passes at `a=0.148125`; blind EXP-148 qualifies `a=0.1481875` as two at both horizons, yielding `[0.1481875,0.14825]`. EXP-130 supplies a qualified negative method result: finite sprinklers do not resolve the narrow local controls. EXP-131's adaptive PIM run fully passes `c=19.9,a=0.150` as three/positive but falsifies the proposed three/positive class at `c=19.8,a=0.148`; the boundary therefore cannot be continued as a simple nearly vertical line from `c=20`. EXP-132 qualifies the complete finite bracket `[0.145,0.150]` at `c=19.9` and the `c=19.8,a=0.150` three/positive endpoint at 256 returns, but retains `c=19.8,a=0.148` as bootstrap-unresolved and fails overall. | Continue only validated endpoints through additional regular gaps, prospectively qualify the lobe/pruning association, and identify the underlying global bifurcation |
| CLM-016 | The TBA curve passes through each principal doubly-superstable point and is tangent there to the `s+` superstability curve. | Barrio-Blesa-Serrano result, verified as a numerical/theory-backed claim of the local PRL | Absent | Continue TBA, `s+`, and `s-`; solve the double-critical condition and measure tangency with uncertainty |
| CLM-017 | Chaotic attractors and chaotic saddles on the same side of the TBA have the same return-map/template topology. | Barrio-Blesa-Serrano result, verified as a claim of the local PRL | The near-neighbor stress test passes locally: EXP-119 qualifies `a=0.150` chaotic/three-branch in all 120 adequate-resolution cells, consistent with the `a=0.149` saddle; coarse cells reproduce the old detector miss. EXP-120's coordinate-specific coverage gap at `a=0.145` shows why scalar equivalence remains insufficient for template claims. | Compare full two-dimensional maps and unstable periodic-orbit knot/link invariants across representative same-side saddle/attractor pairs |
| CLM-018 | The spiral/unimodal and screw/bimodal transition appears in an experimental Rössler-type circuit. | Barrio-Blesa-Serrano empirical result, verified as a claim and figure in the local PRL | Not applicable to recovered numerical code | Obtain underlying data if possible or treat the published circuit return maps as external corroboration; do not claim independent experimental reproduction |
| CLM-019 | Stable period-12 and period-3 attractors coexist at `(a,b,c)=(0.245,0.2,5.75)` in the expanded high-`a` atlas, separated by a fractal basin boundary in the declared `z=0`, `[-10,10]^2` initial-condition plane. | Newly reproduced numerical finding: both cycles pass closure/Floquet stability gates. EXP-019 resolved all 57,344 uncertainty pairs; prospectively preregistered EXP-020 resolved 57,342/57,344 and found `alpha=0.4264`, pair-bootstrap interval `[0.4094,0.4442]`, `R^2=0.9976` across a 64-fold scale range. The positive sub-unity exponent supports fractal and rejects riddled at measured scales; the numerical dimension remains provisional. | EXP-015 through EXP-020 | Test CPU parity, longer transients, spatial conditioning and smaller scales; recover both cycles by shooting/collocation; continue both families and independently interval-validate selected orbit data. |
| CLM-020 | A period-3-to-period-6 fundamental flip belongs to a folded parameter-space surface; separated surface points, including a projection fold, have a supercritical period-doubling branch opening. | Newly reproduced local finding. EXP-028 through EXP-047 independently qualify the event, cycles, scaling, surface, fold line, and period-3/6 identity. EXP-048/049 expose the failed EXP-023 provenance. EXP-050 then independently rebuilds the true period-5 branch with identity enforced. The period-3/6 surface and the true period-5 branch are distinct objects. | Local coupled solves, branch switching, scaling, fold-safe continuation, double-cover identities, atlas falsification, direct recurrence counts, and identity-constrained natural continuation. | Repeat the 3/6 atlas overlay; continue the surface globally; validate selected flips; compare with TBA geometry. |
| CLM-021 | At fixed `(a,c)=(0.245,5.1)`, the true period-5 family undergoes a supercritical flip, and its stable period-10 child later changes the historical return-section branch count through a boundary grazing rather than another flow-orbit bifurcation. | Newly reproduced local finding. EXP-051 through EXP-105 establish eight supercritical rungs from 5→10 through 640→1280 using identity-safe continuation, multiple shooting, block-Floquet stability, whole-orbit sign identity, and an exact second-variational event solve. Three prospective predictions pass: EXP-066 misses the 80→160 event by `1.398e-7`; EXP-086 misses the 320→640 event by `3.00e-10`; and EXP-103 corrects the predicted 640→1280 event at `b=0.17971219643223899`, only `1.476e-11` from its frozen prediction. EXP-104 produces four bilateral amplitude-consistent child candidates; EXP-105 identifies both signs as one stable period-1280 child with whole-orbit RMS `3.94e-8` and dominant moduli near `0.426174`. The six finite spacing ratios progress `4.5363, 4.5944, 4.6476, 4.6646, 4.6682, 4.6690`. EXP-055 separately locates the section grazing at `b=0.181750232321`. This is deep finite cascade evidence and a clean separation of flow bifurcation from section topology, not a global TBA, logistic conjugacy, or universality proof. | Identity-safe continuation, signed block-Floquet refinement, 32/64/128-segment multiple shooting, multiresolution phase-invariant orbit comparison, perturbed-attractor recovery, continuous section-tangency refinement, three successful frozen out-of-sample scaling predictions, a two-solver/two-representation precision audit, a known-event-validated exact augmented flip solve, and independent period-1280 child qualification. | Continue orbit-defined flip and grazing sets in parameter space; satisfy RVR-003 through RVR-006 for the reviewers' branch-count, finite-ordering, reinjection, and unfolded-spiral gaps; test alternate sections/coordinates; compare with TBA and atlas geometry. |

## Current scientific positioning

CLM-008 addendum (EXP-212--214): 123 additional exact parent events extend the
upper period-6 flip arm through `c=8.40309`. The lower stop is not a physical
endpoint: continuous and extremum-aware refinement qualifies a
historical-section grazing at `c=6.93831802121`, where phases change
seven-to-six while Barrio remains eight and the real-`-1` event persists.
This strengthens the parent skeleton but establishes neither critical-point
membership nor a TBA identification.

CLM-008 addendum (EXP-215--216): invariant continuation crosses the qualified
grazing and reaches a sampled minimum `c=6.83093274`, then reverses its
`c`-projection and returns through 21 exact events to `c=6.99993288`. All
returning points retain seven extremum-historical and eight Barrio phases, and
the terminal event independently recorrects under Radau. This rejects the
assumed monotone lower extension and reveals a candidate broad second arm; it
does not yet prove global closure, a shrimp-boundary assignment, TBA
membership, or double-criticality.

CLM-008 addendum (EXP-217): 135/135 accepted exact events extend the returning
arm to `(a,c)=(0.27126703,8.25273305)`, retain extremum-historical/Barrio counts
`7/8`, and pass terminal Radau recorrection. Across the common `c` range its
separation from the original arm grows from `0.00891` in `a` at `c=7.16` to
`0.05778` at `c=8.25`. This qualifies a broad folded orbit-defined skeleton,
not yet paired shrimp boundaries, child stability on the returning arm, TBA
membership, or double-criticality.

CLM-008 addendum (EXP-220): the frozen three-slice child claim fails, but the
untouched near returning-arm slice yields four primitive stable period-12
children toward lower `a`, opposite the original arm's higher-`a` children.
All four pair with unstable period-6 parents and pass exact section identity,
primitivity, period-ratio, Floquet, and DOP853/Radau whole-orbit gates. This
locally supports an opposing-boundary interpretation. The middle and far
returning-arm children remain unresolved and prevent a global shrimp-boundary
assignment.

CLM-008 addendum (EXP-223, EXP-226, and EXP-229): adaptive identity-safe continuation
qualifies one stable primitive period-12 child through 212 points and 45 exact
returning-arm events. The full middle-slice target fails where the nominal
child becomes the parent traversed twice. DOP853 and Radau then independently
localize the intervening period-6 real-`-1` crossing at
`c=7.62537829761/7.62537829365`. A primitive stable child passes before it;
after it, both solvers qualify the stable parent's double cover through
half-period closure, state identity, doubled `14/16` section counts, and
monodromy squaring. This establishes a bounded sampled child strip on one
frozen path. EXP-229 subsequently identifies this crossing with the known
EXP-217 returning arm at all 21 tested coordinates: maximum `a` difference is
`1.46e-14`, while the former `5.60e-7--5.85e-7` apparent separation is exactly
linear interpolation error. The second-boundary inference is retracted. The
result demonstrates stability exchange across the known flip locus, not
whole-shrimp connectivity, TBA membership, or double-criticality.

CLM-008 addendum (EXP-230 and EXP-232): removing source-arm interpolation from
the child path carries the primitive period-12 branch past the false endpoint.
It then loses stability at a genuine real-`-1` event near
`(a,c)=(0.2407011815,7.6258156004)`. DOP853 and Radau roots agree to `3.38e-8`
in `c`, retain `7/8` parent versus `14/16` primitive-child identity, and show
stable-before/unstable-after period-12 multipliers bilaterally. This qualifies
a deeper local cascade rung, not yet its period-24 child, supercriticality, a
paired shrimp boundary, TBA membership, or double-criticality.

CLM-008 addendum (EXP-237--241): an exact 16-segment augmented representation
of the period-12 event passes all DOP853/Radau gates. Exact anti-periodic
switching then produces a primitive `28/32` period-24 branch, which continues
for 20 points. At a near-event offset of `-3.22e-10` in `a`, both solvers find
the period-12 parent unstable and period-24 child stable, qualifying the local
flip as supercritical. Farther along the same continued child, both solvers
agree on a strongly unstable multiplier near `-703.436`; this motivates a
frozen next-flip scan but does not yet establish the intervening event, a
period-48 child, a full child sheet, TBA membership, or double-criticality.

CLM-008 addendum (EXP-242--246): after preserving and correcting an
eigenvalue-identity failure, the exact period-24 branch reaches a second
real-`-1` event at `a=0.24070104611236293`. A 64-segment mode switch produces
primitive `56/64` period-48 candidates, and DOP853/Radau independently qualify
an unstable period-24 parent with a stable period-48 child immediately beside
the event. This extends the local returning-arm cascade through period 48 and
qualifies the second doubling as supercritical. It does not establish a
universality limit, global child sheet, paired shrimp boundaries, TBA
membership, or double-criticality.

CLM-008 addendum (EXP-247--253): exact continuation of the period-48 branch
isolates its next real-`-1` event at `a=0.24070101640878155`. Although the
EXP-250 optimizer reaches its evaluation ceiling, all DOP853 event residuals
pass and the separately frozen EXP-251 segmented Radau audit independently
qualifies the orbit, anti-periodic tangent, multiplier, cyclic products,
proper-subperiod separation, and `56/64` identity. Hash-bound switching then
nominates primitive period-96 candidates on both signs. At a near-event point,
DOP853/Radau agree on an unstable period-48 parent and stable primitive
period-96 child with exact `112/128` identity, qualifying a third local
supercritical doubling. The two available event spacings have ratio `4.557`;
this is finite cascade evidence, not a universality, full child-sheet,
paired-boundary, TBA, double-criticality, or whole-plane result.

CLM-008 addendum (EXP-254--261): continuous phase minimization first proves
that both period-96 switch signs are one phase-shifted orbit. Exact
continuation then reaches a fourth real-`-1` event at
`a=0.2407010100842176`; DOP853 and segmented Radau independently agree on the
orbit, anti-periodic tangent, multiplier, cyclic products, proper-subperiod
separation, and `112/128` identity. Bilateral switching produces primitive
`224/256` period-192 candidates, and a frozen near-event test classifies the
period-96 parent as unstable and period-192 child as stable under both
solvers. A common-parameter whole-orbit audit then aligns both switch signs at
a half-period shift under both integrators, showing one stable primitive
period-192 orbit. This qualifies a fourth local supercritical doubling. The four event
coordinates give only two finite spacing ratios, `4.557` and `4.697`; they do
not establish a limiting constant, universality, a full child sheet, paired
boundaries, TBA membership, double-criticality, or a whole-plane result.

CLM-008 addendum (EXP-263--267): exact continuation of the unified period-192
branch reaches a strongly unstable endpoint, and a magnitude-separated scan
isolates one real-`-1` bracket. The first coupled solve and an unchanged-node
precision audit preserve near-threshold multiplier failures. A prospectively
frozen tighter coupled solve then passes symmetric DOP853/Radau `1e-7` flip
gates at `a=0.24070100861338276`, with orbit/tangent residuals below
`5.31e-11/1.39e-11`, proper-subperiod separation, and exact `224/256`
identity. This qualifies a fifth exact event, not its period-384 child. The
three finite spacing ratios are `4.557`, `4.697`, and `4.300`; their
non-monotonicity strengthens the prohibition on a limiting-universality claim.

CLM-008 addendum (EXP-268--269): bilateral 512-segment switching from the
fifth exact event produces six primitive period-384 candidates with exact
`448/512` identity. At a prospectively frozen near-event point, DOP853 and
Radau independently classify the period-192 parent as unstable and the
period-384 child as stable, with child moduli agreeing to relative
`1.83e-6`. A common-coordinate whole-orbit audit then aligns both switch signs
at a half-period shift under both solvers. This qualifies one stable primitive
period-384 orbit and a fifth local supercritical birth, but not a sixth event,
limiting universality, paired boundaries, TBA membership, double-criticality,
or a whole-plane result.

CLM-008 addendum (EXP-270--273): common-coordinate whole-orbit phase matching
first identifies both period-384 switch signs as one orbit. Eight exact
continuation steps then reach a strongly unstable endpoint, and a
magnitude-separated scan isolates one real-`-1` bracket. A prospectively
frozen 512-segment coupled solve terminates normally and passes symmetric
DOP853/Radau `1e-7` flip gates at `a=0.24070100830924687`, with all orbit and
tangent residuals below `2.53e-11`, proper-subperiod separation, and exact
`448/512` identity. This qualifies a sixth exact event, not its period-768
child. The four finite spacing ratios are `4.557`, `4.697`, `4.300`, and
`4.836`; their non-monotonicity still forbids a limiting-universality claim.

CLM-008 addendum (EXP-274--275): bilateral 1,024-segment switching from the
sixth exact event produces six primitive period-768 candidates with exact
`896/1024` identity. At a prospectively frozen near-event point, DOP853 and
Radau independently classify the period-384 parent as unstable and the
period-768 child as stable, with child moduli agreeing to relative `2.24e-5`.
This qualifies a stable primitive period-768 orbit and a sixth local
supercritical birth, but not tangent-sign equivalence, a seventh event,
limiting universality, paired boundaries, TBA membership, double-criticality,
or a whole-plane result.

CLM-008 addendum (EXP-276--278): two complete common-coordinate sign audits
align both period-768 switch signs at half phase under DOP853 and Radau, while
each preserves one isolated four-representation long-product spread failure.
A prospectively frozen canonical audit binds those passed whole-orbit
identities and the independently preselected EXP-275 negative sign, then
corrects one common-phase seed under both solvers. The stable moduli agree to
absolute `9.78e-8` under the unchanged `0.002` gate, and exact `896/1024`
identity passes. Thus the two signs qualify as one stable primitive orbit for
continuation, while both failed receipts remain part of the conditioning
record. This does not establish a seventh event or universality.

CLM-008 addendum (EXP-279--287): exact continuation and a separated spectral
scan isolate a period-768 real-`-1` event at `a=0.2407010081734325`. The
Float64 augmented solve and tighter immutable replay preserve an independent
multiplier failure because the local multiplier sensitivity exceeds Float64
parameter resolution. Two prospectively frozen 50-digit, three-level,
order-four integrations then pass independently: classical RK4 gives
`-0.9999999948282761`, RK4 3/8 gives `-0.9999999948805051`, and their
difference is `5.22e-11`. All Richardson, neutral, cyclic, characteristic,
orbit, tangent, primitive, and exact `896/1024` identity gates pass. This
qualifies a seventh exact numerical flip event and yields a fifth finite
spacing ratio `2.239`; it does not qualify a period-1536 child, seventh
supercritical birth, limiting universality, paired boundaries, TBA membership,
double-criticality, or a whole-plane result.

CLM-008 superseding addendum (EXP-288--292): the event promotion above is
retracted without deleting its numerical history. Sparse switching produces
six well-corrected period-1536 candidates, but the independent parent/child
criticality audit cannot resolve the parent side. Two 50-digit tableaux agree
on the stored parent multiplier near `-1.000000115`, yet a true 50-digit orbit
correction at three step counts leaves the prospective `1e-6` source
neighborhood by `7.32e-5`--`9.32e-5` and drives the tracked `-1` root toward
zero. This is consistent with unconstrained correction to the nearby
lower-period double cover. The qualified claim therefore returns to six exact
supercritical births through a stable primitive period-768 child. The
seventh-event coordinate and ratio `2.239` are candidates only; an augmented
orbit-plus-antiperiodic-tangent correction is required to resolve them
(FND-101).

CLM-008 addendum (EXP-293): the first 50-digit augmented orbit-plus-tangent
pilot converges the 1,024-step discrete equations to residuals below `1.24e-30`
and preserves `2.58e-5` half-orbit separation, thereby avoiding the
lower-period double-cover collapse seen in EXP-292. It still fails the frozen
physical bracket after a `-4.50e-9` coordinate shift and fails the pointwise
tangent-source gate. The seventh-event retraction remains in force pending
multi-resolution and independent-tableau reproduction.

CLM-008 addendum (EXP-294): the augmented classical-RK4 coordinate and period
converge across 1,024/2,048/4,096 steps with ratios `15.718/15.706`. The finest
and Richardson coordinates lie inside the original event bracket, residuals
are below `1.32e-26`, and primitive half-orbit separation persists. The frozen
receipt nevertheless fails only identity with the old Float64 tangent field,
whose maximum pointwise displacement remains `4.162` across resolution. No
event is restored until an independent tableau agrees with the new corrected
orbit and tangent line.

CLM-008 addendum (EXP-295 and FND-102): an independent three-resolution RK4
3/8 augmented sequence passes all ten gates. Its `a` and period ratios are
`15.721/15.707`; its Richardson coordinate differs from the classical value
by `2.05e-14`; finest nodes and base tangents agree within `1.24e-10` and
`1.61e-13`; and all tangent-line gates pass. This supersedes the old Float64
tangent field and qualifies a seventh primitive real-`-1` event near
`a=0.24070100823759`. The fifth finite spacing ratio is corrected from the
retracted `2.239` to `4.244`. The ledger now supports seven exact events, six
supercritical births, and a stable primitive period-768 child; the seventh
birth's criticality and period-1536 stability remain open.

CLM-008 addendum (EXP-296--299): the first fresh switch fails only because its
qualified 4,096-step event source misses the unchanged DOP853 matching gate by
`4.41e-9`. An 8,192-step augmented refinement then passes all ten gates and
reduces that residual to `9.64e-10`; both largest-predictor switch signs pass
from the refined source. A prospectively selected positive sign is corrected
independently under DOP853 and Radau. Both solvers classify the primitive
period-1536 child as strongly stable, with moduli `0.12419628/0.12419164`, and
pass every orbit, identity, and agreement gate. The parent remains inside the
frozen `1e-4` neutral margin at `0.99999149/1.00002167`, so EXP-299 correctly
fails as `other-or-unresolved`. This strengthens, but does not yet promote, a
supercritical seventh-birth interpretation; the ledger remains at seven exact
events, six qualified supercritical births, and a stable primitive period-768
child.

CLM-008 addendum (EXP-300): a 32-step continuation from the independently
stable EXP-299 child accepts only 23/33 required rows, so the receipt fails
without relaxation. Its exact accepted prefix crosses the frozen `1e-11`
event-separation threshold at step 16 and reaches `7.56e-11`; terminal closure,
neutral, half-period nonclosure, and exact two-section identity all pass. The
terminal preliminary multiplier is not evidence. A separately frozen audit may
select the first-threshold row and independently correct it, but EXP-300 does
not itself change the ledger's seven-event/six-supercritical-birth status.

CLM-008 addendum (EXP-301): independent DOP853/Radau correction at the
deterministic first `1e-11`-separated prefix row passes every orbit and
agreement gate, but parent and child are both unstable. Parent moduli are
`1.00132578/1.00130325`; child moduli are `284.80804/284.80915`. This fails the
required stability exchange and leaves the seventh birth direction open.
Combined with EXP-299's independently stable child at the source coordinate,
it brackets a child stability loss on the exact continuation prefix; it does
not yet qualify a real-`-1` eighth event or change the secure event/birth count.

CLM-008 addendum (EXP-302): the complete 18-row block-Floquet prefix passes and
isolates exactly one stability-loss bracket in its first interval. The real
period-1536 multiplier changes from `-0.12419628` to `-4.49514241` over
`a in [0.24070100823770973,0.24070100823781396]`; four-shift relative spread
is at most `2.35e-6`. This nominates an eighth real-`-1` cascade event for an
augmented exact solve. It does not yet change the secure count of seven exact
events and six independently supercritical births.

CLM-008 addendum (EXP-303--304): the dense 2,048-segment augmented solve is
terminated without a scientific verdict after stagnation and catastrophic
trial divergence. The replacement 50-digit cyclic formulation reduces the
system to 8-by-8 and converges in 145 seconds to residuals below `2.71e-31`
while preserving primitive period-1536 separation. Its coarse coordinate lies
`4.576e-9` outside the physical bracket and raw tangent coordinates leave the
source neighborhood, so no eighth event is promoted. Multi-resolution and an
independent RK tableau remain mandatory.

CLM-008 addendum (EXP-305): the 50-digit classical-RK4 augmented sequence
passes all correction, fourth-order convergence, primitive-separation,
node-identity, and tangent-line gates at 1,024/2,048/4,096 steps per segment.
Its parameter and period convergence ratios are `15.7178/15.7060`, but the
Richardson event coordinate `a=0.2407010082240912813` lies `1.362e-11` below
EXP-302's `1.04e-13` continuation-row bracket. The sole failed bracket gate is
preserved. This invalidates that interval as a physical event bound without
invalidating the converged cyclic formulation; independently corrected child
endpoints must rebuild the stability bracket. The secure count remains seven
exact events and six independently supercritical births.

CLM-008 addendum (EXP-306 and FND-103): an algebraically independent
three-resolution RK4 3/8 augmented sequence passes all ten gates. Parameter
and period ratios are `15.7210/15.7069`; its Richardson coordinate differs
from EXP-305 by `2.05e-14`; extrapolated periods differ by `7.21e-11`; finest
nodes agree within `1.24e-10`; and every tangent-line gate passes. This
qualifies the eighth primitive numerical real-`-1` event at consensus
`a=0.24070100822410155263` despite preserving the rejection of EXP-302's
micro-bracket. The sixth finite spacing ratio is `5.312`, extending the
non-monotone sequence without establishing a limit. The ledger now supports
eight exact events, six independently supercritical births, and a stable
primitive period-768 child; period-3072 existence and the seventh/eighth birth
directions remain open.

CLM-008 addendum (EXP-307): an 8,192-step RK4 3/8 extension of event eight
passes all ten representation gates. Parameter and period increments converge
at `15.8601/15.8529`; augmented residuals are below `1.37e-29`; and the
doubled DOP853 event-matching and secondary-null residuals are
`1.36e-9/3.60e-12`. This qualifies the representation as a source for a
period-3072 switch but does not change the eight-event/six-supercritical-birth
ledger or establish a period-3072 child.

CLM-008 addendum (EXP-308): both bilateral 4,096-segment period-3072 signs
correct in two evaluations and pass matching, phase, closure, neutral,
node-primitivity, displacement, period-ratio, and exact `3584/4096` identities.
The negative sign passes every gate; the positive sign fails only direct
half-period nonclosure at `4.41e-8 < 5e-8`. The bilateral candidate-count gate
therefore fails without relaxation. No period-3072 child or birth direction is
promoted.

CLM-008 addendum (EXP-309): deterministic factor-two predictor separation
produces two accepted primitive period-3072 candidates. Both correct in two
evaluations, with matching below `8.92e-11`, half-node RMS `9.02e-6`, direct
half-period nonclosure `2.25e-6/3.52e-7`, period ratio within `1.11e-12` of
two, and exact `3584/4096` identities. This nominates period-3072 children for
independent stability qualification; it does not yet establish attraction or
eighth-birth direction.

CLM-008 addendum (EXP-310): DOP853/Radau independently classify the primitive
period-3072 child as strongly unstable with moduli
`18.98176427/18.98180420`; every orbit, identity, nonclosure, and agreement
gate passes. Parent moduli `1.00003875/0.99995754` remain inside the frozen
`1e-4` neutral margin, so the combined result correctly fails as
`other-or-unresolved`. This is strong evidence consistent with a subcritical
eighth birth, but the secure ledger remains eight exact events and six
independently qualified supercritical births until a farther same-side audit
resolves the parent.

CLM-008 addendum (EXP-311): four full-step sparse corrections extend the
primitive period-3072 child while matching stays below `3.22e-9` and half-node
RMS grows from `9.02e-6` to `5.41e-5`. Terminal closure, neutral mode,
half-period nonclosure, period ratio, and exact `3584/4096` identity pass. The
branch crosses the finite event coordinate but ends only `7.77e-13` away, so
the frozen `1e-11` separation gate fails. This preserves an exact resumable
prefix but neither resolves parent stability nor changes the secure event and
birth ledger.

CLM-008 addendum (EXP-312): receipt-bound resumption accepts six more exact
period-3072 rows before a minimum-step trial reaches matching
`1.00429e-8 > 1e-8`. The seven-row receipt fails its nine-row and `1e-11`
separation gates, ending `4.744e-12` from the finite event, while terminal
closure, neutral mode, nonclosure, period ratio, and exact `3584/4096`
identity pass. The first row beyond `4e-12` was selected without stability and
is reserved for independent audit; no birth direction is promoted here.

CLM-008 addendum (EXP-313): at the stability-blind first prefix row beyond
`4e-12`, DOP853/Radau independently find the period-1536 parent unstable
(`1.00230292/1.00236720`) and the primitive period-3072 child extremely
unstable (`22667.8829/22667.8902`). Every residual, node-identity, nonclosure,
exact section-identity, and cross-solver agreement gate passes. The result
fails only because both families are unstable. Thus the daughter continuation
has crossed to the parent-unstable side; eighth-birth direction remains open
and requires solver-specific parent-event localization rather than a farther
parameter-distance proxy.

CLM-008 addendum (EXP-314): parent-only DOP853 and Radau evaluations pass
oppositely placed signed real-`-1` brackets of width
`5.9544e-13/5.9827e-13`. Their new endpoint residuals are
`+3.27617e-4/-2.16818e-4`, safely beyond the fixed `1e-4` floor, with all
correction, direct-orbit, neutral, and block-Floquet gates passing. The shared
EXP-310 coordinate is barely unstable for DOP853 and barely stable for Radau
because it lies between the solver-specific numerical events. This explains
the neutral split without changing physical criticality or the secure birth
ledger.

CLM-008 addendum (EXP-315): two prospective bisections per solver pass every
fresh correction, direct-orbit, neutral, and block-Floquet gate. DOP853
retains event eight in
`[0.24070100822429846,0.24070100822444732]`; Radau independently retains it in
`[0.24070100822399930,0.24070100822414890]`. The widths are
`1.48853e-13/1.49575e-13`, and the brackets are disjoint by `1.49575e-13`.
This bounds the solver-representation uncertainty and explains why a shared
absolute coordinate cannot securely determine the parent side at the frozen
margin. It establishes neither two physical events nor the eighth-birth
direction; the next child switch must be event-relative under each solver.

CLM-008 addendum (EXP-316): equal-offset event-relative DOP853/Radau samples
independently classify the period-1536 parent as stable
(`0.99968068/0.99965539`) and the period-3072 candidate as strongly unstable
(`18.98363/18.98308`). Cross-solver node RMS values are
`4.51e-9/3.34e-10`, multiplier spreads are below `2.90e-5`, and every
correction, direct-orbit, neutral-mode, and exact section-identity gate passes.
The experiment still fails because child half-period nonclosure is only
`9.43e-7/1.61e-6`, below the frozen `2e-6` primitive-child floor. This is
strong solver-consistent subcritical evidence, but the secure birth ledger is
unchanged. Post-run diagnosis finds unchanged `9.01896e-6` half-node RMS and
only `3.34e-10` cross-solver child RMS, so geometric collapse is rejected; the
long single-shot diagnostic is below its own closure-error scale. Promotion
requires a prospectively frozen segmented and tolerance-converged identity
audit, not retrospective relaxation of EXP-316.

CLM-008 addendum (EXP-317): tighter DOP853/Radau corrections independently
retain phase-invariant primitive period-3072 half-orbit separation
`8.66424730e-6/8.66424725e-6`. Cross-solver child RMS is only
`3.34029e-10`, giving a `25,938.6` separation/error ratio; matching remains
below `2.13e-10`, period difference is `1.22e-7`, and the bound exact section
identities hold. Combined with EXP-316's stable-parent/unstable-child
classification, this qualifies the eighth local birth as subcritical. The
secure ledger is now eight exact events, six independently supercritical
births, and one independently qualified subcritical eighth birth; the seventh
birth remains unresolved. EXP-316's failed single-shot gate remains preserved.

CLM-008 addendum (EXP-318): independent 50-digit classical-RK4 and RK4 3/8
profiles resolve the period-768 parent at EXP-299's stable primitive
period-1536 coordinate. The signed real-`-1` residuals are
`+6.4226805e-6/+6.4226424e-6`, while empirical Richardson/cross-tableau
uncertainty is at most `7.7932e-9`, a signal/error ratio of `824.1`. All
arithmetic, orbit, neutral, cyclic, and characteristic gates pass, but the
frozen experiment fails because parent and candidate child are both stable.
This rules out promoting EXP-299's sampled pair as a supercritical stability
exchange. It does not retract the seventh exact event or decide its local
criticality: the stable period-1536 candidate may lie beyond an ultranarrow
fold/restabilization or on a distinct nearby sheet. The secure ledger remains
eight exact events, six independently supercritical births, and one
independently qualified subcritical eighth birth; the seventh birth remains
unresolved.

CLM-008 addendum (EXP-319): a same-map 50-digit RK4 3/8 branch switch removes
the discrete-event/continuous-child coordinate mismatch. Both tangent signs
and two predictor amplitudes pass, producing primitive stable period-1536
daughters on the lower-`a` side with moduli `0.92877`--`0.98228`. Mean
parameter displacement grows from `1.29205e-13` to `5.17089e-13` as half-node
RMS doubles from `7.88364e-7` to `1.57674e-6`, giving exponent `2.000728`.
This nominates a local supercritical seventh birth and shows that EXP-299's
higher-`a` stable candidate is not the immediate daughter in this discrete
representation. The secure ledger does not change until EXP-320 independently
replicates the result at 8,192 steps per segment.

CLM-008 addendum (EXP-320 and FND-105): the unchanged 8,192-step replication
passes every bilateral, correction, primitivity, direction, quadratic-opening,
period, cyclic, neutral, and child-stability gate. Its event-relative
displacements, amplitudes, and stable child moduli reproduce EXP-319 within
`9.08e-10`, `9.27e-13`, and `1.41e-10` relative, respectively; the independent
opening exponents are `2.000728180629/2.000728180631`. The immediate stable
daughter opens toward lower `a`, opposite EXP-318's higher-`a` stable-parent
side. This qualifies the seventh local birth as supercritical while preserving
EXP-318's stable/stable failure: the higher-`a` EXP-299 candidate is not the
immediate daughter. The secure ledger is now eight exact events, seven
independently qualified supercritical births, and one independently qualified
subcritical eighth birth.

Latest CLM-008 checkpoint (EXP-214): the lower-`c` DOP853/Floquet extension
qualifies 551 stable period-6 orbits but fails its 1,000-point coverage gate.
Seven prospectively selected edge brackets then all refine to real `-1`
Floquet events with `7.63e-11` maximum `a` width and exact two-section
identity. Exact-Jacobian coupled continuation then passes all 41 points over
`c in [7.16,7.32]`. The bounded stable strip therefore has a dense sampled
period-doubling curve. EXP-207 cannot follow the requested eight-point child
arms, but EXP-208 independently qualifies primitive stable period-12 children
at three separated post-flip samples. EXP-209 then passes square-root opening,
multiplier-ratio, independent-solver, and two-sided attraction gates at all
three slices. EXP-210 then preserves a 16-cell doubled-parent root-selection
failure. Without relaxing a gate, EXP-211 independently seeds and qualifies
all 124 cells of the 31-by-4 period-12 sheet, with zero fallbacks and 31
square-root fits. EXP-212 then adds 123 exact parent events and reaches
`c=8.40309`; EXP-213/214 qualify the lower historical-section grazing while
preserving the invariant event. This preserves the EXP-202 scale-aware
residual question while replacing unconstrained extrapolation with frozen
EXP-204 replay, remote child tests, invariant continuation through the
grazing, and future TBA comparison.

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
