# Referee-to-paper traceability

Last updated: 2026-08-07

This file complements the scientific closure gates in
[`../docs/reviews/2026-08-07-jones-peer-review-gap-audit.md`](../docs/reviews/2026-08-07-jones-peer-review-gap-audit.md).
It prevents a manuscript edit from appearing to answer a referee when the
underlying experiment is still open.

| Referee concern | Required citations | Current manuscript location | Scientific gate | State |
|---|---|---|---|---|
| Equations and fixed/scanned parameters were introduced in the wrong order | `rossler1976equation` | “Mathematical objects and claim scope” | RVR-001 | Drafted; exact section/domain still open |
| “Conjugate” was used without a one-to-one correspondence between all relevant trajectories/orbits | `holmes1984bifurcation` | Introduction; “Mathematical objects”; limitations | RVR-001, RVR-004 | Terminology corrected; test open |
| Jones failed to credit Ref. 6 for identifying TTL | `barrio2011global` | Introduction; “Prior work and novelty boundary” | RVR-002 | Citation present; close-reading novelty matrix open |
| Logistic/kneading ordering in a flow was already known through finite period | `lefranc1994combining`, `holmes1984bifurcation` | Introduction; “Prior work and novelty boundary” | RVR-002, RVR-004 | Citation present; finite Jones test open |
| Novelty was unclear amid recent periodicity-hub work | `barrio2011global`, `jones2012topological`, `barrio2012topological` | Introduction; “Prior work and novelty boundary”; discussion | RVR-002 | Co-discovery wording fixed; complete primary-source matrix open |
| Two/three extrema oscillation was promising but insufficiently demonstrated | `jones2012topological`, `barrio2012topological` | Results; “Topology and symbolic tests still required” | RVR-003 | Local attracting and saddle controls pass, including independent 128/256 PIM stability; continued curve open |
| Reinjection was described using an unclear phase-space branched-manifold picture | `jones2012topological` | “Topology and symbolic tests still required” | RVR-005 | Reframed as a return-map hypothesis; experiment open |
| The spiral-unfolding argument and Fig. 6 were too hard to follow | `jones2012topological` | “Topology and symbolic tests still required”; future figure slot | RVR-006 | Explicitly open |
| The tool was not exploited or generalized | all core sources as context | Results; discussion | RVR-007 | Rössler computation advanced; cross-flow test open |
| No accessible conclusion for nonspecialists | none mandatory | Conclusion | RVR-008 | First plain-language draft present; independent readability review open |

## Rule for marking a row closed

A citation or paragraph can close an exposition or attribution issue. It cannot
close a scientific issue. Rows tied to RVR-003 through RVR-007 require the
acceptance evidence specified in the peer-review gap audit and the claim
ledger, not merely revised prose.
