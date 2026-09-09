# EXP-492: locate the sixteen event-boundary candidates

Prospective exploratory successor, 2026-09-08 local date. EXP-491 is complete
and unchanged. Its pointwise accuracy checks passed, while sixteen intervals
failed time coherence. A post-run inspection of its retained extrema found
one sign-changing extremum in the flagged half of each interval, with the
same ordinal and accepted-prefix count in both solvers. These are
outcome-informed nominations, not independent confirmations.

## Question and scope

Do those sixteen nominated extrema actually reach the section tangentially,
with a nondegenerate, two-sided birth/death of a crossing pair? A positive
result localizes a boundary in the initial-curve coordinate u at fixed
parameters. It does not establish a parameter bifurcation, a periodic window,
an invariant quotient, a projected output fold, C/D, a symbolic word/arrow,
the physical inner-return interpretation, or a homoclinic connection.

Keep all 26 EXP-491 intervals in the input ledger. The ten screened-regular
intervals are explicitly not selected for this boundary test; that does not
certify them free of hidden boundaries. The sixteen selected intervals cover
ten families: all eight left-region families and the second case's two
right-region depth-eight families. Preserve every nomination and failure.

## Deterministic input construction

Bind the full EXP-491 completed summary, audited public result and original
EXP-490 input table. For each failed interval, independently require both
solvers to identify the same unique half with an adjacent prefix-time change
exceeding one. Open the four retained endpoint reports, verify their hashes,
and retain all 64 complete endpoint JSON reports as public input evidence.
Require equal extremum counts, the same unique sign-changing extremum ordinal
in both solvers, and identical counts of accepted crossings earlier than
each nominated extremum minus 0.5 model-time units. No new integration is
used for this construction; all source report hashes are retained.

The u search box is exactly that original half-interval. Its arithmetic
midpoint is the sole u seed. The time seed is the mean of the four nominated
extremum times. Freeze a time box of seed time plus/minus 0.25. A failed box,
alignment or uniqueness check fails construction, not selection of a more
convenient extremum. The independent validator reconstructs identities and
seed arithmetic from the public evidence, not just table self-hashes.

## Direct test and complete matrix

Use the original affine curve q0+u*v0 and its tangent, with the exact
historical reconstructed negative section. At each candidate solve

    h(u,t)=0, h_t(u,t)=0

using fixed-time six-dimensional state/first-variation IVPs and bounded
two-variable Newton: DOP853 and Radau, rtol=1e-13, atol=1e-15, max_step=.001,
eight iterations, one seed, no damping alternatives, retries or box expansion.
Retain every returned Newton IVP before interpretation, including a solver
failure. An exception inside the existing census helper can prevent its
partial mesh from being returned; in that case preserve the profile-start
record, earlier files and whole-run failure, and report the incomplete matrix.
Require plane residual<=1e-10, velocity residual<=1e-9, |h_u|>=1 and
|h_tt|>=1. Require both roots inside the frozen boxes and paired u/time/scaled
state agreement<=1e-9/1e-8/1e-7, with scales(15,15,.01).

If both roots qualify, use their arithmetic mean u as a **common side-input
center**, so both side solvers start from exactly identical initial states.
This alignment does not average away a failed root. With w the frozen half-
interval width, use the four doses (-w/1000,-w/10000,w/10000,w/1000), in that
order. All four shifted inputs must remain inside the search box; otherwise
retain the roots and mark all side arms skipped, with no smaller substitute.

Each dose gets a complete extremum-partitioned census through the original
candidate horizon: guard1e-8, uncertain-extremum margin1e-10, same solver
settings. In the fixed root-time window plus/minus0.05, require two roots on
the side predicted by h_u*dose*h_tt<0, zero on the other side, exactly one
accepted negative crossing when the pair exists, no uncertain extrema,
plane residual<=1e-8 and crossing angle>=1e-7. The preceding accepted count
must match the frozen endpoint-derived count. The separation at the two
pair-producing doses must have ratio sqrt(10), within 5% relative error.
Reject uncertain extrema anywhere before the local window's end or adjacent
to a local root bracket, not only those strictly inside the window. Evaluate
the predicted birth/death side using each solver's actual distance from its
own fitted root; report that effective dose alongside the common nominal dose.

Cross-check each entire accepted side-event sequence between solvers: equal
counts, time difference<=1e-7 and scaled-state difference<=1e-6. Retain every
ordinary root, reconstructed root, extremum, later crossing and raw trajectory.
Root agreement without the complete side matrix is not a qualified boundary.
Report the two-root/one-negative-crossing distinction explicitly; a changed
section count is not by itself a changed physical period.

Maximum target workload: 16 candidates x 2 solvers x (8 Newton IVPs + 4 side
censuses) = 384 integrations. Failed roots retain both solver outcomes and
skip the joint side matrix; no experiment marker is reset. The EXP-491
three-point flag is the cheaper prior screen, not proof of this mechanism.
All sixteen outcomes are reported alongside that screen, without filtering.

## Controls, audit and resources

Analytic controls traverse the same Newton, census, ordinal and paired-side
path. Positive polynomial-clock fields have exactly 0, 1 and 8 preceding
negative crossings and a known simple tangency; a no-root-in-box field and
a transverse crossing must remain unqualified. Both solvers are required.
Control traces and full event reports are retained; their integration meshes
may be discarded. For prefix k, set T=2k+1 and
P(z)=product(z-j, j=1..2k)/(2k)!, with P=1 for k=0. The clock field is
x'=0, z'=1, y'=d/dz[P(z)*((z-T)^2+x)]. Its initial state is
(2e-5,T^2+2e-5,0), tangent(2,2,0), u box[-.001,.001], seed u=0,
seed t=T+.002, time box T+/-.1, horizon T+1.5, and doses
(-2e-6,-2e-7,2e-7,2e-6). The exact root is u=-1e-5,t=T; accepted regular
crossings are at odd integers1..2k-1. A negative x adds a negative crossing
at T-sqrt(-x). The independent control audit requires all those event times
within1e-7, in addition to the production checks.

The no-root control uses k=0, initial(.1,1.1,0), with the other k=0 settings;
Newton must leave the frozen u box. The transverse control uses field
(0,-1,1), initial(0,.5,0), tangent(1,0,0), seed t=.5 and time box[.4,.6];
its Newton matrix must be singular and no side arm may run. Both negatives
retain both solvers. Each of the five conditions has at most24 control
integrations, so the whole analytic matrix has at most120. The
coefficient/algebra tests include the other realized prefix counts and
independently computed event equations.

The read-only audit reconstructs the complete input and outcome matrices,
Newton sequence, raw initial/final states, independent Rössler grazing
equations, side geometry, paired comparisons, exact decisions and hashes.
Missing or failed rows are not removed. This is a same-agent local audit,
not independent peer review or rigorous integration validation.

Use the existing local CPU, serial target execution, 7,200-second whole-run
deadline, 384-target cap, 8 GiB output cap, 16 GiB initial free-space reserve
and 8 GiB free-space floor. Charge the observed EXP-491 1,160.794844 seconds
over 156 censuses, scale to the maximum 384 and double: about 5,714.68 seconds,
leaving the remainder for the analytic controls. Fixed-time Newton IVPs are
no longer than their original horizons; this remains a conservative heuristic,
not a guaranteed runtime. Complete actual controls and tests before freeze.

Freeze and push code, plan, input evidence, tests and audit before any new
target trajectory; verify the live remote SHA and then execute in the same
turn. Monitor completion/operational validity only until full audit. If an
integration, deadline or storage exception prevents completing the matrix,
preserve the incomplete run and failure, with no automatic restart.

No paid review, rented GPU, API generation, new upload or manuscript release.
The human-controlled Pro policy applies. Scientific thresholds and old
sources remain unchanged; additional mechanisms or symbolic conclusions need
their own designs, not post-run reinterpretation of this endpoint.
