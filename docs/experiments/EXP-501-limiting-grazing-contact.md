# EXP-501: limiting grazing-boundary contact

Status: prospective, outcome-informed numerical pilot; not preregistered.
Prior EXP-498/499/500 results informed this design. No EXP-501 target has run
when this protocol is authored. Paid review: not requested under AGENTS.md.

## Decisive question

At the fixed EXP-497 primitive-cycle/right-fold proximity anchor, does the
**regular return immediately preceding the accurately localized grazing** lie
on any of the six historical-section cycle events? EXP-498 compared finite
perturbations, not this limiting boundary point; EXP-499/500 qualified those
perturbed trajectories, not the boundary location itself. This pilot removes
that distinction before attempting a joint two-parameter contact solve.

Run all eight EXP-498 first-case boundary representations, including the old
failure; retain the complete 26-candidate inherited ledger. No selection among
depths, directions, roots, configurations, cycle phases or cycle indices.
Parameters remain the exact binary64 values a=0.21558015990653545, b=0.2,
c=7.212. Initial bases, directions, section, cycle events and root seeds come
only from the hash-bound public EXP-497/498 records. Seeds are the means of
the **fitted EXP-498** roots, not their older EXP-492 seeds. Original search
boxes and expected accepted-prefix counts remain unchanged.

The new initial curve is q(u)=q0+u*v evaluated in decimal arithmetic after
exact promotion of the binary64 q0 and v. Record requested u and every realized
initial component. This is explicitly a new curve evaluation: rounding of the
old binary64 side states, especially multi-coordinate directions, need not
place them exactly on it. Do not reuse old side geometry as if it measured the
new inputs. No new side-trajectory or winding claim is made here.

## Numerical contract

Two fixed profiles: 40 decimal digits/order 24/step 0.02 and 50 digits/order
32/step 0.01. Integrate the state and its initial-u variation together with a
sparse-quadratic Taylor recurrence, retaining every coefficient of all six
components at every step and every Newton iteration. Newton solves h=0 and
h_t=0 simultaneously; its Jacobian is [[w_y,f_y],[(Jw)_y,(Jf)_y]]. It does not
divide by the vanishing section velocity. At most eight integrations per
profile; no damping, hidden restarts, fallback or box expansion. Residual
bounds are 1e-24 for each equation. Require absolute unfolding and curvature
at least 1 for target qualification; paired u/time/state differences at most
1e-12/1e-12/1e-9 (state scaled by [15,15,0.01]). These are numerical agreement
criteria, not rigorous ODE error bounds.

State magnitude bound 1e4; tangent magnitude bound 1e12. Last-three-term
diagnostics, divided by [15,15,0.01], must not exceed 1e-20 for state and
1e-16 for tangent. They are not bounds on omitted terms. A mathematical
nonconvergence/box exit retains its trace and proceeds to the next profile;
storage, archive, input or source-integrity failure stops the run and preserves
partial evidence. No consumed attempt may be reset.

On each converged trajectory, audit the complete stored-polynomial section
census on [0,t_g-0.05]. The deliberate final tangency is outside this census;
this is not a claim of all roots through or beyond grazing. Use the frozen
EXP-500 exact-rational polynomial isolation/classifier and its separately coded
certificate verifier, without editing those sources. Require the prescribed
nonempty accepted-prefix count and complete ordered paired event agreement
(1e-12 time, 1e-9 scaled state). Its final accepted event is the limiting
predecessor. It must be transverse under the inherited angle threshold 1e-7.

Compare every qualified predecessor against all six events, both original
DOP853/Radau cycle profiles and both repeat windows: 16x24=384 possible
full-state comparison cells. The cycle inputs remain the audited EXP-497
binary64 reference, not a newly high-precision corrected cycle. Report x-only
residuals separately; they never substitute for full-state membership.
Primary proximity radius 1e-4, sensitivities 1e-6/1e-5/1e-3. For each cycle
index report the worst distance over **all** representations, configurations,
methods and windows. Do not minimize over those variants. Report boundary
state spread and predecessor spread as representation diagnostics, not
sampling uncertainty. Comparison with old finite-dose predecessors is
descriptive only, with their failures retained.

## Controls and audit

The same augmented integrator/Newton/archive path must recover analytic
rotation grazing (u=0,t=pi/2) and parabolic grazing (u=0,t=1), with root and
state errors <=1e-22. A nonzero quadratic exponential component checks
state/tangent evolution against an analytic expression. Both configurations
run every control. Synthetic tests additionally reject singular Newton
systems, box exits, malformed/partial archives, coefficient corruption,
missing profiles/ledger entries, changed tolerances and source/input drift.
The complete prefix census uses analytic crossing controls through its actual
producer and certificate-replay path. Exact isolated copied-source startup
must pass under python -I -B before first target integration.

The separate auditor checks every retained coefficient recurrence using
scalar sums at higher precision, reconstructs the Newton trace and initial
states, verifies the exact polynomial certificates, and rebuilds all distance
and completeness decisions. Shared classification/formula replay is disclosed;
this is local audit, not independent-team replication or peer review.

## Outcomes and claim limits

Positive: all sixteen root/prefix profiles qualify and at least one *fixed
cycle index* is within the primary radius in all 64 applicable cells. This
supports limiting-boundary/cycle proximity at this anchor, not exact contact.
Negative: complete qualified matrix, but no index meets that all-variant rule.
Mixed: any root or prefix fails; publish all available comparisons without
promoting a subset to the complete verdict. No tested outcome by itself
verifies/debunks Jones's flow-level chains, identifies C/D, proves a second
smooth scalar-map critical point, establishes homoclinicity, or verifies a
p-to-p+1 connection. This reconstruction is not recovered Jones source code.

Execution cap: 128 target IVPs, 7200 seconds, 4 GiB new output, 9 GiB initial
free space and 8 GiB reserve; local CPU only. Preserve every attempted raw
trajectory, failures and hashes. Public Git freeze before targets, one
exclusive EXP-501 attempt marker. Publish compact results and code after raw
audit; full coefficient archives remain local unless separately authorized
for upload. No paid API calls, cloud rentals or credential loading.

After the result, use the limiting residual (if qualified) with the distinct
right-fold residual in a prospectively bounded joint a,c contact experiment;
do not keep refining this fixed anchor indefinitely. An observed inability
to define two independent residuals requires revisiting the branch model,
not relabeling a grazing as the missing smooth critical point.
