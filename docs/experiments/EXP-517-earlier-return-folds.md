# EXP-517: directly test the two earlier-return fold candidates

## Outcome-informed calibration, not verification of a symbolic chain

EXP-516 reports eleven endpoint sign-change cells across all saved ordinals.
Nine reuse intervals containing a previously qualified EXP-514 grazing in
their accepted prefix or before the output. The other two are direction-0
returns 4-to-5 at nodes 17–18 and 7-to-8 at nodes 18–19. Both bracket the
known depth-four reference x with regular endpoints and small endpoint time
jumps. Their interiors have not been tested. All these prior results were
known before this design; proximity to a calibration reference is not a
held-out prediction of Jones's alphabet.

Retain the complete eleven-cell ledger and its grazing classifications. Test
both unclassified cells, without rerunning the nine as if their known cuts
were smooth brackets. This does not exclude additional roots in those nine
intervals. A later interval-wide proof remains separate.

## Four representations, specified before new integrations

At a=.21559488260076548, b=.2, c=7.162000000000001, preserve both original
upstream anchors/directions and the exact legacy binary64 section. For each
of the two direction-0 intervals, keep its original u endpoints. Define the
direction-1 interval by matching the **initial physical x** at those two
endpoints with the original affine direction-1 curve. Its z changes according
to that curve's original direction; it is not fitted to the reference state.
These extended direction-1 intervals were not in the old twenty-node grid.
Record the realized x agreement to 1e-12. This supplies four candidates:
history 4 and 7, each with directions 0 and 1.

These are explicitly histories **4 and 7**, not a relabeling of history 8.
All EXP-510/515 eighth-return failures remain unchanged. Neither choosing
another ordinal nor obtaining a fold here would restore that old test.

Use the unchanged EXP-513 midpoint-seeding, two-equation bounded Newton
shooting and fold qualification implementations. At each midpoint, collect
the complete retained extremum-aware dense census with DOP853 and Radau.
Require the complete accepted prefix and input regularity to agree before
using the mean observed output time as the shooting seed. The u search box
is the prescribed interval; the time box is [1e-8, 55.670662229876534]. Stop
that candidate on a proposal outside its box; do not integrate it, enlarge
the box or substitute an unrecorded seed. Continue every other candidate.
There are at most eight Newton iterations per solver.

Keep the existing rtol=1e-13, atol=1e-15 and max_step=.001. Retain the full
9D state/first-/second-variation shooting meshes, plus every guard and census
mesh. Failed meshes are saved too. At a converged root use all three fixed
u offsets (-1e-6,0,+1e-6), only if they fit its original box. Require original
gain >=1e-4, normalized x component >=.001, angle >=1e-7, full-state <=1e-6,
time <=1e-7, normalized root derivative <=1e-7, opposite side slopes,
curvature finite-difference relative discrepancy <=.001 and nonzero scaled
curvature >=1e-6. Check the full accepted prefix at all three offsets; these
sampled checks are not a continuous-domain enclosure or an exact-flow proof.

Compare both input and output full states against every one of the four
existing depth-four references. A representation restores the calibration
reference only if every scaled-max distance is <=1e-6 and all fold checks
pass. Also report the maximum full-state spread across all eight solver
representations; the combined four-representation verdict requires <=1e-6
spread and every individual reference test to pass. Do not average away a
failed direction, history or solver. No C/D label, primitive-period claim,
periodic-family connection or symbolic arrow is assigned.

## Integrity, controls and resources

Reuse and raw-audit the existing analytic dense-census and fold control
bundles through the unchanged implementations; this adds zero control IVPs.
New analytic tests cover the deterministic mapped input matrix, retention of
all eleven nominations, failed midpoint/search paths, and the all-four
reference/spread decision. Pass isolated startup, source closure and tests;
freeze/push and live-verify the exact source before a one-shot marker.

The target cap is 128 IVPs: four candidates times two solvers times at most
two midpoint IVPs, eight shooting IVPs and six offset-census/guard IVPs.
Bound elapsed time at 3600 seconds and total target output at 2 GiB, including
the final summary; initial free space >=11 GiB, continuing floor 8 GiB,
failure reserve 1 MiB. Use canonical bounded JSON admission and the existing
compressed-product quota adapter. Preserve partial products and a consumed
attempt on failure; no retry of a consumed target or numerical fallback.

Raw products stay local. No paid review, GPU worker, upload, external
coordination or new spending is required. Release the complete same-agent
raw audit, compact public replay, all four geometric results and a figure
with failures retained. Further reconstruction and held-out symbolic tests
remain necessary even if all four folds qualify.
