# EXP-494 — Move the inner-turn measurement onto periodic families

Status: prospective exploratory study; no target result inspected at design.
The EXP-480 six/eight counts and EXP-492/493 local initial-condition results
are already known. This does not retest them as fresh predictions.

## Question and complete matrix

Can corrected periodic cycles carry the projected-winding diagnostic, are
their candidate periods numerically minimal, and does a bounded nearby
parameter continuation encounter a change of winding? This is an exploratory
family survey, not a preselected symbolic word match or a chain verification.

First analyze all eight preserved EXP-480 profiles, without integration.
Bind its complete terminal receipt and every declared raw file. Use its
retained ordinary events only for this historical saved-data analysis; do not
describe them as a new extremum-aware census.

Then re-correct both nominated seeds using DOP853 and Radau and survey four
arms from each: increasing/decreasing a at fixed b,c; increasing/decreasing c
at fixed a,b. Each arm has eight equally spaced targets: |delta a|=0.0001 per
step, |delta c|=0.002 per step. There are 64 planned parameter points, two
solvers each, plus four base profiles. All arms start independently from the
qualified base; no cross-arm restart or outcome-dependent parameter choice.
This covers neither the entire plane nor a certified interval between nodes.

Both methods use the same preceding DOP853 state/period as phase reference.
A pair must qualify before advancing that arm. A failed pair and every later
unrun target remain in the complete ledger. Other independent arms continue.
No adaptive step, alternate seed, failed-method replacement or hidden retry.

## Numerical and geometric rules

Float64 CPU, DOP853/Radau, rtol=1e-12, atol=1e-14, max_step=0.01.
Existing variational phase-conditioned shooting: tolerance=1e-11, at most
30 evaluations. Require optimizer and corrector success, closure <=1e-9,
phase residual <=1e-10, scaled state step <=0.25 using (15,15,0.01), and
relative period change <=0.05. These step bounds are exploratory identity
screens, not a proof of unique branch continuation. Preserve all shooting
trial meshes, including unsuccessful trials; retain final observation meshes
and ordinary plane/extremum lists before interpreting them.
Retain final-observation dense polynomial coefficients (DOP853 F or Radau Q
and each step's old state) in numeric NPZ arrays, not pickle. This permits
replaying bracketed events without new integration; the coefficient evaluator
is checked against exact circular solutions and solver-reported event states.

Observe each corrected cycle for 2.5 candidate periods. Bracket roots between
normal-velocity extrema for both historical-negative and Barrio-positive
sections, preserving ordinary lists separately. Extrema are numerically
detected, so this is not a rigorous all-root certificate. Require no extrema
within 1e-8 of either plane in the two analyzed windows and root residual
<=1e-8. Analyze phase windows [0.25,1.25) and [1.25,2.25).

For each window: raw mesh, mesh augmented by all section extrema, and cubic
Hermite midpoint enrichment. Interpolate endpoints from retained states and
the vector field. Require scaled endpoint closure <=1e-6. Close each polygon
with an explicit short endpoint segment, measure its winding about the small
equilibrium's x-y projection independently of event counts, and require all
three polygon measurements to qualify under EXP-493's radius >=1e-10,
angle-step <=2.9 rad, integer residual <=1e-10 guards and agree in integer
winding. Compare that integer to historical accepted count afterwards.
Closure is numerical and polygon sampling is not a validated ODE enclosure.

A repeated traversal multiplicity m must divide the counts on BOTH sections,
conditional on complete transverse counts. Test every m>=2 dividing their gcd:
the state at T/m from each window start must differ by scaled norm >=1e-5.
Also require all distinct accepted states within each section separated by
>=1e-5, normalized crossing angles >=1e-6, and accepted-event distances from
window boundaries >=1e-7 periods. For known 6/8 cycles the only
possible multiplicity is 2; this is a conditional numerical minimal-period
check, never a rigorous proof. Zero-event cases remain unresolved.

Repeated windows and paired solvers must have equal ordered counts, scaled
event-state norm differences <=1e-6 and phase differences <=1e-7. Paired
corrected states must differ by <=1e-6 scaled norm and relative periods by
<=1e-7. All profile geometry and shorter-period checks must pass. Period
counts and winding are allowed to change between parameter nodes: enforcing
constancy would preclude observing the proposed mechanism by construction.

## Controls, execution, and release

Analytic circular orbits exercise the actual observer and geometry consumer
with both solvers, including a twice-traversed circle that must FAIL minimal
period, and zero-event/undersampled/contact negatives. Unit tests cover
complete grid, blocked arms, missing profiles, and paired mismatch. Local
reasoning/test audit only; paid review not requested under AGENTS.md.

Commit/push source, tests, protocol and plan before first new metric/target.
Execution records exact source/input hashes and an exclusive attempt marker.
At most 7200 seconds, 6000 IVPs, 8 GiB output; start with >=16 GiB free and
preserve an 8 GiB floor. Runtime limit is operational, not outcome-dependent.
Keep every attempted/blocked row and any failure. No paid GPU/API calls.
Release compact full-grid data, correction outputs and an allowlisted replay
bundle; raw meshes remain separately hashed when too large for the compact
release. Publication must state that availability distinction.

Interpretation: a qualified change nominates a periodic-family geometric
transition for a separately frozen localization. No observed change means
only no change on this bounded qualified sample. Failed continuation is not
absence of a branch. Neither result assigns C/D, recovers Jones words, proves
homoclinicity, nor verifies a p-to-p+1 symbolic arrow. A critical/branch
dictionary and held-out orbit coding remain indispensable.
