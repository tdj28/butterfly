# Referee-to-paper traceability

Last updated: 2026-08-12

This file complements the scientific closure gates in
[`../docs/reviews/2026-08-07-jones-peer-review-gap-audit.md`](../docs/reviews/2026-08-07-jones-peer-review-gap-audit.md).
It prevents a manuscript edit from appearing to answer a referee when the
underlying experiment is still open.

| Referee concern | Required citations | Current manuscript location | Scientific gate | State |
|---|---|---|---|---|
| Equations and fixed/scanned parameters were introduced in the wrong order | `rossler1976equation` | “Mathematical objects and claim scope” | RVR-001 | Drafted; exact section/domain still open |
| “Conjugate” was used without a one-to-one correspondence between all relevant trajectories/orbits | `holmes1984bifurcation` | Introduction; “Mathematical objects”; limitations | RVR-001, RVR-004 | Terminology corrected; test open |
| Jones failed to credit Ref. 6 for identifying TTL | `barrio2011global` | Introduction; “Prior work and novelty boundary” | RVR-002 | Citation present; close-reading novelty matrix open |
| Logistic/kneading ordering in a flow was already known through finite period | `lefranc1994combining`, `holmes1984bifurcation` | Introduction; “Prior work and novelty boundary” | RVR-002, RVR-004 | Citation present; four complete supercritical rungs through a stable period-16 child are qualified on an explicit `L2`-like path. The source-defined symbolic permutation/kneading comparison remains open |
| Novelty was unclear amid recent periodicity-hub work | `barrio2011global`, `jones2012topological`, `barrio2012topological` | Introduction; “Prior work and novelty boundary”; discussion | RVR-002 | Co-discovery wording fixed; complete primary-source matrix open |
| Two/three extrema oscillation was promising but insufficiently demonstrated | `jones2012topological`, `barrio2012topological` | Results; “Topology and symbolic tests still required” | RVR-003 | Controls, `a=0.140`, `a=0.145`, `a=0.147`, and `a=0.150` pass prospectively; EXP-123/124 expose finite-time conditioning sensitivity at `a=0.148`; blind PIM qualifies `a=0.148`, `a=0.148125`, and `a=0.1481875` as two and identical-method `a=0.1485` and `a=0.14825` as three, narrowing the sampled bracket to `[0.1481875,0.14825]`; EXP-129's held-out signed edge predicts its blind class; EXP-127 explains the conditioning split as delayed but bounded transient capture; EXP-130 rejects finite-sprinkler continuation near the boundary and EXP-131 prospectively falsifies a nearly vertical extension at `c=19.8`; eleven recovered primitive UPO families all persist across the local bracket, selecting a manifold/pruning mechanism; a transverse continued curve and manifold event remain open |
| Reinjection was described using an unclear phase-space branched-manifold picture | `jones2012topological` | “Topology and symbolic tests still required” | RVR-005 | Reframed as a return-map hypothesis; EXP-127 rejects faster capture for the `a=0.148` transient branch, the complete recovered UPO census persists across the bracket, and EXP-144 rejects capture timing for four phase-resolved candidates. Retrospective EXP-145 finds a pre-existing UPO escape lobe excluded from every two-side PIM saddle profile but included in every three-side profile under nested two-dimensional distance controls; prospectively frozen EXP-149 then passes the predicted two-branch/lobe-excluded association at an untouched midpoint. Exact manifold contact and reinjection rotation remain open |
| The spiral-unfolding argument and Fig. 6 were too hard to follow | `jones2012topological` | “Topology and symbolic tests still required”; future figure slot | RVR-006 | Source extraction complete: 23 words, ten matched arrows, one visual-only arrow, three lower-period relationships, and ten parameter landmarks are machine-readable. Blind exact-coordinate recurrence identifies eight solver-qualified periodic landmarks, two unresolved points, and one early/late capture mismatch. Word/arrow reproduction and replacement figure remain open |
| The tool was not exploited or generalized | all core sources as context | Results; discussion | RVR-007 | Rössler computation now includes a dense 41-point period-6 flip curve, an identity-safe 124-point period-12 child-sheet patch with 31 square-root fits, 123 additional pseudo-arclength parent events through `c=8.40309`, a cross-solver qualified section grazing, a lower-`c` projection turn, 135 exact returning-arm events through `c=8.25273`, and a 45-event returning child strip bounded by a second cross-solver flip on one frozen path; two-dimensional continuation of that boundary, global endpoints, TBA comparison, and a cross-flow test remain open |
| No accessible conclusion for nonspecialists | none mandatory | Conclusion | RVR-008 | First plain-language draft present; independent readability review open |

## Rule for marking a row closed

A citation or paragraph can close an exposition or attribution issue. It cannot
close a scientific issue. Rows tied to RVR-003 through RVR-007 require the
acceptance evidence specified in the peer-review gap audit and the claim
ledger, not merely revised prose.
