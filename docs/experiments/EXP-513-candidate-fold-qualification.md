# EXP-513: qualify all five recovered candidate intervals

Prospective, outcome-informed local experiment. EXP-512 supplied endpoint
sign changes, not roots or connected return branches. This test asks whether
a fixed bounded search in each interval finds a regular numerical fold and
whether it reproduces the four qualified depth-four full-state references.

## Complete selection and procedure

Use all five EXP-512 intervals, in reported order: direction 0 [1,2], [15,16],
[16,17]; direction 1 [17,18], [18,19]. Preserve each original initial state,
tangent, parameter, nine-return count and epsilon=1e-6. The u box is the
original endpoint interval. The observation horizon is the maximum endpoint
horizon (including the explicit EXP-512 extension), not the old warm-root time.

For each interval, first retain an extremum-aware dense census at its exact
arithmetic midpoint under DOP853 and Radau. Use the same EXP-512 numerical
settings and all event/input conditioning thresholds. If that midpoint pair
is not regular, report `midpoint-unqualified` and do not launch its Newton
search. This is a declared seed-admission rule, not evidence that the whole
interval contains no fold. Continue every other candidate regardless.

When admitted, seed u at the midpoint and seed time at the mean of the two
observed ninth-return times. Permit time only between the guard and the fixed
horizon, and u only in the original interval. Use the unchanged eight-iterate
two-equation projected-fold shooting method. Newton corrects u/time; DOP853 or
Radau still integrates the ODE and variational equations. No rejected collapsed
root is reused and no new parameter point is introduced.

Preserve every Newton mesh. A converged equation receives the unchanged
u-epsilon, u, u+epsilon event censuses only when all three lie inside its
original interval. Retain guard meshes too. Require the existing ordinal,
state/time, transversality, input gain/projection, opposite-side slope,
finite-difference curvature and nondegeneracy tests. Add paired-solver
agreement over the complete nine-event prefix at each of the three offsets;
last-two-event agreement alone does not pass this new check.

Compare every qualified root's input AND output state against ALL four
depth-four references using scales [15,15,.01]. `reference_restored` requires
every resulting distance <=1e-6, the existing cross-history threshold.
Report this separately from local fold qualification and the inherited
historical x-region test. Multiple preimages need not be distinct physical
folds. A restoration in both directions is only permission to design the next
joint-contact continuation, not an established joint point or chain.

## Claims and limitations

Positive: a locally qualified numerical fold under this finite representation,
possibly reproducing the depth-four references. Negative: this fixed search
did not qualify a fold or did not restore the reference. Failures remain
failures. No global root absence, exact-flow theorem, continuous-u domain
certificate, C/D assignment, generating partition or p-to-p+1 arrow follows.
Midpoint/endpoint event-time differences are diagnostic warnings, not proofs
of discontinuity. Grazing localization, when needed, is a later prospective
experiment; do not label an unconverged Newton search a grazing certificate.

## Controls, freeze and resources

Reuse and replay EXP-511's six analytic dense-census profiles and EXP-502's
retained analytic control bundle for the unchanged fold producer/auditor.
New target-free tests cover complete selection, midpoint seed admission,
earlier-event mismatches, all-reference/full-state distance decisions, missing
conditions, and the controller's all-five execution path. Exercise the actual
source/input consumer in a fresh isolated copy before the one-shot marker.
Run the full test suite, local design audit, explicit public secret scan, then
commit, push and live-verify the exact execution source before targets.

Maximum 160 target IVPs: ten midpoint profiles with guard/main (20), plus ten
fold profiles of at most eight shooting IVPs and three guard/main censuses
(140). No new control IVPs, cycles, limiting boundaries, GPU workers or paid
reviews. Limit 3,600 seconds and 2 GiB including final summary; initial free
space 11 GiB, continuing floor 8 GiB, failure reserve 1 MiB. Every JSON/NPZ
write is pre-admitted under the actual producer. Preserve one consumed attempt,
all failures and immutable historical evidence. Resource or unexpected errors
stop the attempt and retain its incomplete status; never reset it.

The raw audit replays every new midpoint dense polynomial, shooting mesh and
algebra, guard/census product, paired-prefix gate and scalar reference distance.
Old compact inputs and analytic controls are explicitly reused, not another
audit of all old targets. Raw files remain local under the existing publication
boundary; release compact results and source with honest replay scope.
