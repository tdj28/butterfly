# EXP-496: a lower-a endpoint for the fold-contact search

Prospective exploratory successor, 2026-09-09. EXP-495 found that neither
original primitive cycle meets the measured right-fold proximity rule. This
test recomputes the fold at the already-qualified third negative-a step of
EXP-494, approximately a=.21545/.21547, b=.2, c=7.212. The original upper
endpoints are a=.21575/.21577. Prior results inform this selection; it is not
an independent sample or a retry of EXP-490/494/495.

## Question and complete design

Does the signed input-x contact residual at zero-based cycle event 3 change
sign between the old upper endpoint and the newly evaluated lower endpoint?
EXP-495 identified event 3 as nearest in both cases. That choice and the known
upper sign are outcome-informed and now fixed; no other event may rescue the
primary comparison. An opposite sign nominates a parameter bracket only.
Two endpoints do not prove continuity, an interior root, exact criticality,
an invariant quotient, C/D, a word/arrow, or a homoclinic connection.

Retain all 26 original fold candidate identities in the input ledger. In each
case select the first parent-qualified in-region candidate in each right-region
history/direction family, in the original table order: depths 4/8, directions
0/1. These eight representatives cover all four variants in both cases. Two
additional qualified upstream preimages in the second case are marked
not-selected-duplicate-representation, not failed or independently replicated.
All sixteen parent-ineligible candidates retain their status. This fixed
representative selection reduces duplicate work; it does not select on new
endpoint performance.

Use both DOP853 and Radau for each selected representation: **16 fold profiles**.
Keep the affine curve's original x/z initial state and tangent, but set its
initial y to the small-equilibrium section offset at the new parameter. This
defines a transported finite-image-curve family, not an assumed invariant
manifold. Count the same m+1 accepted returns as the original depth. Preserve
the original observed input-x region as the in-region gate.

Warm-start u and t at the arithmetic means of the two **qualified** old roots,
identically for both new solvers. Freeze new boxes u_seed +/- .02 and
t_seed +/- 1, horizon t_seed+3, finite-difference epsilon=1e-6. These are
explicitly new search domains at new parameters, not expansions of the old
consumed search. Eight Newton iterations, one seed, no alternate guess,
damping, box expansion, sample refill or automatic retry.

All integration and fold-qualification thresholds are copied unchanged from
EXP-490: rtol1e-13, atol1e-15, max_step .001; exact determinant equations,
separate center/side extremum-aware event censuses, ordinal/transversality,
input conditioning, opposite slopes, nonzero curvature, finite-difference
agreement and both-solver gates. Corrector convergence alone never qualifies.

## Periodic observations and primary comparison

Use the saved EXP-494 paired observations at each base and at negative-a step
3, not a new periodic integration. Require all stored correction, paired,
repeat, primitive-period and six/eight count gates to have passed. Bind their
complete public summary and audit receipt. Both windows (.25 and1.25 periods)
and both methods remain in the comparison, with their qualified common phase
convention. No nearest-state permutation or rephasing is fitted.

For every qualified new fold and each matching method/window, compute
`r=(cycle_state[3].x-fold_input.x)/15` at each endpoint. Require opposite
signs and |r|>=1e-6 at both ends to call that variant sign-resolved. Also
retain all six ordered pair distances, with fold input matched to cycle j
and fold output to cycle (j+1)%6, using EXP-495's full-state/x-only metrics,
scales(15,15,.01), radius1e-4 and complete sensitivity ladder. Those other
indices are diagnostics only, not alternative primary endpoints.

A representation is endpoint-proximate if event3's full-state pair distance
is <=1e-4 in all four new solver/window variants. Otherwise it nominates an
opposite-sign interval only when all four variants have resolved opposite
signs. An ineligible fold is unresolved, not a missing zero. A case-level
endpoint or bracket result requires the corresponding status in all four
representations; report mixed, failed and same-sign cases without selecting
the best history, direction, method or phase. Do not infer absence of a
contact from a failed bounded search.

## Validation, execution, audit and resources

Before targets, run the existing 12 actual transformed-rotation positive,
no-fold and degenerate-projection controls through the same fold-shooting and
census functions. Add successor input/selection, shifted-section, common-seed,
state/sign/ordinal, mixed-variant and tampering tests. The input builder must
be deterministic and copy all parent provenance without new target trajectories.
The full public machine input and source closure are pushed before execution.

The runtime verifies clean exact pushed Git, all input/source hashes, source
closure, controls and free space, then creates its exclusive attempt marker.
Retain every returned Newton mesh, three census meshes/reports per converged
profile, started records, failures and full terminal inventory. A field or
integrator exception can prevent return of its partial mesh; preserve the
started record, earlier evidence and explicit whole-run failure instead of
inventing partial data or resuming. Outcome interpretation waits for the audit.

The separate auditor checks initial/final meshes, Newton arithmetic and
independently coded fold algebra, every retained census, the complete paired
qualification and separate scalar contact/distance arithmetic. It replays
the entire eight-representation/sixteen-profile matrix and parent ledger.
This is same-agent numerical verification, not independent peer review.

Maximum 176 retained target trajectories (16 times eight Newton plus three
censuses), with at most 48 additional tiny census-guard IVPs; no new periodic
IVP. Serial local CPU, 3600-second operational limit, 2 GiB output ceiling,
16 GiB initial free-space reserve and 8 GiB execution floor. Scaling EXP-490's
1572.14 seconds/208 retained trajectories to 176 and doubling gives about
2660.55 seconds; this is a feasibility heuristic, not a runtime guarantee.
Controls run before the consumed target attempt and are separately recorded.

All source, raw results, failed profiles and derived figures must remain
reproducible. No paid review, GPU rental, restricted upload or manuscript
release is requested. The human-controlled Pro policy overrides old gates.
Escalate paid review, restricted disclosure or a materially different research
objective; a negative endpoint result is not itself a reason for permission
requests, extra seeds or another paid review.
