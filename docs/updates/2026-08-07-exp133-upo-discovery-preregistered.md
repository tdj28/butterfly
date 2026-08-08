# Update — EXP-133 PIM-seeded UPO discovery preregistered

DEC-011 converts the next mechanism question into executable gates. Stored PIM
close returns are only shooting proposals: exact DOP853 returns must first
close, and any corrected orbit must retain its proposed section-crossing count
and be transversely unstable by Floquet analysis.

EXP-133 freezes that exploratory search on the independently qualified `c=20`
two- and three-branch saddles. Recovery on both sides would supply finite orbit
objects for manifold seeding; it would not identify the branch-opening event.

A capped secure Runpod was briefly provisioned for parallel execution, but the
derived PIM state archives were outside the existing source-only upload
authorization. No artifact transferred and no workload ran; the pod was
terminated and the account verified empty. The frozen experiment remains
queued for local execution after EXP-132.

The clean local run subsequently passes in `23.47 s`, with accepted unstable
recoveries on both sides. It also reveals that reported lag/crossing identity
does not by itself exclude a repeated traversal: the three-side lag-8 result
is a double cover of lag 4. EXP-134 is therefore frozen before manifold work to
audit every proper divisor and deduplicate phase-invariant primitive families.

EXP-134 passes the divisor audit: all nine two-side recoveries are primitive,
while the two three-side lag-8 recoveries close at half-period near `1.1e-11`
and reduce to lag 4. Its 512-point phase grid is too coarse to consolidate
three equal-period lag-4 phases at the `1e-6` RMS gate, so EXP-135 freezes a
continuous phase-shift optimization before the unique-family count is used.

EXP-135 passes that correction. It leaves nine distinct primitive families on
the two-branch saddle and exactly two among the sampled three-branch
recoveries: lag 4 and lag 12. The shared lag-12 class is the first
identity-continuation candidate; the upper lag-4 class is the test for whether
that orbit persists or terminates across the branch-opening interval.

EXP-136 now freezes both lag-12 continuation directions with an independent
midpoint whole-orbit match, plus lag 4 from the upper to lower endpoint. Every
point retains proper-divisor, crossing, closure, neutral, and instability gates.

EXP-136 fails the strict fixed-lag gate but rules out a simple orbit-birth
mechanism. The upper lag-4 UPO passes all 21 points to `a=0.148`. Both lag-12
flow orbits remain closed, primitive, and strongly unstable when the frozen
counter reports 11 rather than 12 crossings. A post-hoc boundary audit shows
that report is a phase-window artifact, not a section tangency: shifting the
one-period window restores all 12 crossings, and the nearest x-extremum is
more than 8 units from the section. Their family equality remains unresolved
because the fixed-lag paths stopped before overlap. The next test will continue
flow identity without using section count as a stopping gate.

EXP-137 now freezes that repair. Both lag-12 seeds must traverse the full
21-point bracket under flow/Floquet/primitivity gates. The Barrio count is
measured separately on `(0.1 T, 1.1 T]`, and continuous whole-orbit matching at
the midpoint must decisively classify the paths as the same or distinct.

EXP-137 completes all 42 flow points and shifted crossing counts successfully.
The two paths are decisively distinct at the midpoint by period and whole-orbit
RMS. Its receipt remains strictly failed only because bitwise equality rejects
the lower grid representation `0.14812499999999998`. EXP-138 changes that one
gate to a frozen `1e-14` tolerance and reruns the complete calculation.

EXP-138 passes. Both primitive lag-12 UPO families continue across all 21
points, all 42 shifted windows contain 12 crossings, and the midpoint identity
audit classifies the families as distinct. With the lag-4 continuation from
EXP-136, the local branch opening is no longer plausibly explained by birth,
death, or section-crossing loss of these tested UPOs. The mechanism search now
moves to their invariant manifolds and symbolic pruning/reinjection geometry.

Before manifold seeding, EXP-139 freezes the remaining UPO census gap. It
continues all eight untested primitive lower-side families to the three-branch
endpoint, retaining flow/Floquet/primitivity gates and each family's own
phase-robust section lag. Any stopped path becomes the next event-refinement
target; a complete pass supplies an eleven-family cross-boundary orbit library.

EXP-139 qualifies seven of those eight paths across the complete interval.
Lag-13 family 01 alone stops at `a=0.1480375`, with `xtol` convergence and
closure only `6.6e-12` above the corrector's internal numerical floor. EXP-140
now freezes a higher-precision rerun of that single family; no bifurcation is
inferred from the EXP-139 stop.

EXP-140 passes the original stop, then the same hardcoded `1e-10` corrector
floor recurs at the midpoint with normal optimizer convergence. EXP-141
separates optimizer success from the unchanged declared `1e-8` orbit-closure
gate and reruns the family. This is a bookkeeping correction, not a relaxed
scientific threshold.

EXP-141 passes all 21 points. The complete recovered census now contains
eleven primitive UPO families that all persist across the finite local
two/three-branch interval with fundamental section identity intact. This
rejects simple birth/death or crossing-loss explanations for every recovered
family and moves the mechanism program decisively to invariant-manifold
connectivity, symbolic pruning, and reinjection.
