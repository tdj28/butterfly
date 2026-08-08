# Chaotic-saddle qualification checkpoint

Date: 2026-08-07
Status: CPU and GPU control reproduction passed

## What changed

The return-map program can now recover the nonattracting chaotic set inside
the two published period-4 windows, rather than interpolating attractor labels
across them. EXP-110 exposed a shallow third branch and failed its original
global-prominence and pointwise long-horizon-label gates. EXP-111 replaced
that brittle decision with a frozen local-uncertainty oracle and passed all 300
topology cells, but retained honest failures in lattice survivor density and
linear event timing.

EXP-112 then changed sampling and event localization, not the scientific
thresholds. Across 14 scrambled/nested Sobol ensembles, both coordinates, 15
oracle variants, step halving, later conditioning, and 21,000 bootstrap
refits, all 420 topology cells recover two branches at `a=0.118` and three at
`a=0.149`. Survivor fractions, critical locations, support, numerical failure,
and DOP853 short-horizon gates all pass.

EXP-113 transfers the frozen 8192-point controls to a Float64 Triton/RK4
kernel. The GPU returns the same two/three classification in all 30 topology
cells. One final survivor differs at the unimodal control (`1/8192`), while
the entire bimodal survivor curve is exact. The largest combined CPU/GPU
critical span is `0.01463`, and the largest DOP853 state/time discrepancies are
`2.46e-6` and `3.16e-6`.

## What this means for Jones

This is good news for a necessary part of Jones's explanation. It supports the
existence and numerical recoverability of the two/three-branch nonattracting
structure through regular windows, so the branch mechanism is not merely an
artifact of chaotic attractors or one CPU implementation. It does not yet show
that third-branch reinjection predicts `p -> p+1` spiral connections, nor does
it explain the full `(a,c)` plane.

## Numerical and compute record

RK4 advances the GPU state. Bounded Newton refinement is used only to locate a
Poincare crossing inside an RK4 step on a cubic-Hermite interpolant; adaptive
DOP853 is the independent short-horizon reference.

The source archive bound commit `03a77bf`; the retrieved receipt's remote and
local SHA-256 values match. An over-cap A40 price adjustment was rejected
automatically. The accepted secure A5000 ran at `$0.27/hour`, the conservative
total cost bound is below `$0.06`, and the account was verified to contain no
active pods after teardown.

## Next binding gate

Implement and preregister a structurally independent PIM-triple or
stagger-and-step saddle trajectory at the two controls. Only after that
corroboration should the saddle-defined branch boundary be continued across
the period-4 gap and then expanded adaptively in `(a,c,b)`.

## Independent-method checkpoint: EXP-114

EXP-114 implements strict Nusse-Yorke PIM straddles with adaptive DOP853 and
fails its complete prospectively frozen zero-censor gate. All five unimodal
lines and two bimodal lines contain a candidate that survives the full 256-
return lifetime horizon; no integration fails.

Three bimodal lines complete 1200-return straddles and retain 2997 pairs per
coordinate. Both coordinates recover three branches in every one of 15 oracle
variants. Within-PIM and combined CPU/PIM critical spans are below `0.01263`.
This is retained as independent bimodal-saddle corroboration, but it does not
close the two-control gate. The successor will treat censoring as a lifetime
lower bound and require a censored interior block to be strictly bracketed by
captured lower-lifetime endpoints, plus nested-horizon stability.

## Censor-aware successor frozen: EXP-115

DEC-009 and EXP-115 now turn that diagnosis into an executable, prospectively
frozen rule. A censored interior block is eligible only when captured points
on both sides have exact, strictly shorter lifetimes. The code never imputes an
escape time beyond the observed lower bound, and boundary-touching plateaus
remain unresolved. Unit tests cover both certified refinement and boundary
rejection.

The target repeats three fixed section lines at 64- and 128-return censor
horizons. Each horizon must independently recover the expected two/three
topology at both controls; critical locations must also agree across horizons.
The preregistration checkpoint is the next source commit. No target value has
been inspected while choosing these gates.

## Censor-aware result: fixed-horizon success, nested-horizon failure

EXP-115 completes from clean preregistration commit `f354fc0` in `5574.91 s`
and fails its full gate. The 64-return unimodal profile produces three complete
straddles but insufficient invariant-domain coverage; the 64-return bimodal
profile produces only one of the required two straddles. Both profiles remain
unresolved, so the nested comparison is unresolved. No integration fails.

Both independently executed 128-return profiles pass. Three unimodal
straddles recover two branches and three bimodal straddles recover three in
both section coordinates; all 15 oracle variants agree. The largest within-PIM
critical span is `0.01501` and the largest combined CPU/PIM span is `0.01511`.
This is qualified fixed-horizon two-control corroboration by a structurally
independent PIM/DOP853 construction, but not censor-horizon invariance.

The result is positive for the local Jones/Barrio branch substrate and negative
for treating a short lifetime ceiling as harmless. The next frozen comparison
must test 128 versus 256 returns before PIM is used to continue the saddle-
defined boundary.

## Longer-horizon successor frozen: EXP-116

EXP-116 freezes the accepted EXP-115 128-return critical intervals and hashes
as immutable references, then computes only a new 256-return profile. All
geometry, solver, line, oracle, CPU-comparison, and support gates remain
unchanged. Both controls must pass and the combined 128/256 critical span must
be at most `0.04` in both coordinates. This avoids paying to recompute the
already hashed reference while preserving a prospective comparison.

## Longer-horizon result: EXP-116 passes

EXP-116 completes from clean commit `a90b330` in `5136.14 s` and passes every
gate. All six 256-return PIM lines resolve, both controls retain 2097 pairs per
coordinate, and all 60 case/coordinate/oracle cells return the expected
two/three distinction. There are no adaptive integration failures.

The maximum within-256, CPU/256, and frozen-128/new-256 normalized critical
spans are `0.01601`, `0.01595`, and `0.01601`. Reliance on censored bounds
drops from 1108/385 evaluations at 128 returns to 34/1 at 256 returns. The
finite-horizon independent-method control gate is therefore closed at the two
published points. The next binding action is prospective saddle-defined
continuation through the intervening regular gap.

## First held-out saddle path frozen

EXP-117 is preregistered as the first prospective use of the qualified sampler
away from the two published controls. It evaluates all five period-4 cells
identified by EXP-109 on the `c=20,b=0.2` path. Only `a=0.118` and `a=0.149`
retain expected endpoint labels; the labels at `0.120,0.140,0.145` are blind.
Every cell repeats the complete seven-ensemble EXP-112 gate, and the resulting
five labels must form one nondecreasing two-to-three transition. This can
produce a held-out saddle-defined bracket, not yet a continuous TBA curve.

## Held-out path result: partial progress, complete gate fails

EXP-117 completes from clean commit `8cb8bfa` in `759.27 s` and fails the full
path gate. The robust counts are `2,2,2,unresolved,3`. The blind `a=0.140`
case passes every frozen numerical gate and all 210 oracle variants in both
coordinates, narrowing the resolved saddle bracket to `[0.140,0.149]`.

At `a=0.145`, rapid survivor decay leaves 33--231 final survivors and
284--1872 pairs. Seventy-two of 90 attempted oracle variants return two
branches, none return three, and 18 remain coverage/bootstrap unresolved. At
`a=0.120`, 210/210 variants return two, but the 2000-unit cycle reference is
too short for the repeated-block classifier; a post-result 3000-unit audit
recovers period 4 and the same capture cycle to scaled distance `1.06e-9`.
Neither diagnosis changes the failed receipt.

The combined record also exposes a new continuity question. The qualified
three-branch saddle at `a=0.149` lies immediately beside EXP-109's two-branch
aperiodic candidate at `a=0.150`. A recurrence-only post-result audit remains
nonperiodic after burn-ins through 10000 time units, so simple rapid periodic
capture does not explain the difference. Freeze a multi-burn-in topology and
Lyapunov audit at `a=0.150` before assuming one monotone TBA crossing.

## Adjacent invariant-set audit frozen

EXP-118 preregisters the `a=0.150` audit without an expected branch label. It
collects eight 1200-return datasets: the original initial state after four
burn-ins through 10000 time units and four scrambled-Sobol section states at
the longest burn-in. Both coordinates must agree under all 15 oracle variants,
with frozen within/across-dataset critical-drift gates. Two initial states must
also classify chaotic under eight-block variational spectra and agree with an
independent two-trajectory largest exponent. This test decides persistence and
local topology; it does not yet choose among a second crossing, crisis/set
selection, or scalar-projection failure.

## Adjacent invariant-set result: chaos passes, cross-resolution label fails

EXP-118 completes from clean commit `3f351d9` in `214.11 s` and fails its full
gate. All eight 1200-return datasets remain nonperiodic across burn-ins through
10000 and four independent section seeds. Both variational spectra classify
chaotic and their largest exponents agree with independent two-trajectory
estimates within `0.00865`. The Lyapunov rows miss only the frozen `1e-6`
trace-identity sub-gate, at `2.80e-6` and `2.74e-6`.

The scalar topology disagreement is structured, not random. Forty-six of 48
20-bin cells return two, while 189 of 192 30--80-bin cells return three; the
remaining five are unresolved and no cell votes in the opposite resolution
group. Thus EXP-109's nominal two at `a=0.150` is not robust to the qualified
local oracle. The apparent `0.149/0.150` reversal is unsupported, which is good
news for branch continuity, but EXP-118 cannot be relabeled three-branch.
Freeze an independent resolution-convergence successor with the coarse result
as a declared negative control and a tighter trace audit.

## Resolution-convergence successor frozen

EXP-119 doubles each return sequence to 2400, uses four new scrambled-Sobol
states from seed 119 plus the original state, and separates the oracle matrix
prospectively. The three 20-bin cells per coordinate are an under-resolution
control expected to return two; all twelve 30--80-bin cells must return three.
Critical locations must meet the frozen within-dataset gate and the combined
new/hashed-EXP-118 across-dataset gate. Both Lyapunov cases are repeated with
tenfold tighter relative/absolute tolerances and half the maximum step while
retaining the original `1e-6` trace threshold.

## Resolution-convergence result: EXP-119 passes

EXP-119 completes from clean commit `e01457b` in `310.80 s` and passes. All five
new datasets remain aperiodic and provide 2399 pairs per coordinate. All 30
20-bin control cells return two, while all 120 30--80-bin cells return three.
Maximum within-dataset and combined new/frozen critical spans are `0.01184`
and `0.01807`.

Both tighter variational spectra classify chaotic, independent largest-
exponent differences are at most `0.00519`, and the trace errors fall to
`1.25e-7`. The adjacent `0.149/0.150` contradiction is therefore closed as a
coarse-resolution artifact. The binding path action returns to the
support-poor `a=0.145` saddle cell using a prospectively enlarged ensemble and
the now-qualified resolution grouping.

## Large-support `a=0.145` successor frozen

EXP-120 addresses the last sampled path hole without changing the capture
physics or oracle thresholds. Every corresponding EXP-117 ensemble grows by a
factor of eight, with a `2^15,2^16,2^17` nested ladder and new scrambles
120--122. All seven ensembles and both coordinates must resolve two branches
in every oracle variant, with unchanged survival, critical-drift, minimum-
support, and DOP853/Hermite gates. A pass narrows the sampled saddle bracket to
`[0.145,0.149]`; it does not interpolate the boundary.

## Large-support result: sample scarcity closes, coordinate coverage remains

EXP-120 completes from clean commit `89caeb3` in `358.51 s` and fails its full
gate. The eightfold support increase works numerically: every run now exceeds
323 final survivors and 2726 pairs, survivor fractions agree within `0.001282`,
and no integration or DOP853 audit fails.

All 105 `y` cells resolve as two. In `z`, 84 cells resolve as two and the
remaining 21 are exactly the three 80-bin variants in every run. Each fails
only equal-width domain coverage at `0.675` or `0.6875`, has one nominal
critical point inside the resolved interval, and never returns three. More
sampling cannot fill bins outside the projected invariant support. Freeze a
prospective coverage-censor rule, reproduce both published controls with it,
then apply it on new `a=0.145` ensembles.

## Coverage-censor qualification frozen

EXP-121 preregisters a coverage-only censor rule before generating new data.
At least 12 of 15 variants per run and coordinate must resolve normally. Any
remainder must fail only the coverage gate, retain at least `0.65` coverage,
remain graph-like, contain exactly the expected nominal critical geometry, and
stay within the unchanged critical-span thresholds when included. An opposite
branch count or any other failure is fatal.

New scrambled-Sobol seeds 123--125 repeat the complete seven-run construction
at the published `a=0.118` two-branch and `a=0.149` three-branch controls. The
same new ensembles are enlarged eightfold at `a=0.145`. All three cases, both
coordinates, numerical gates, and one ordered two-to-three transition must
pass before the sampled bracket can narrow to `[0.145,0.149]`.

## Coverage-censor result: EXP-121 passes

EXP-121 completes from clean commit `8d96f1c` in `686.79 s` and passes every
gate. The two published controls require no censoring: all 420 variants resolve
normally and reproduce two branches at `a=0.118` and three at `a=0.149`.

The new `a=0.145` data also pass. All 105 `y` variants resolve as two. In `z`,
84 variants resolve as two and the remaining 21 are the preregistered
coverage-only censors; none is rejected or contradictory. The weakest target
run retains 327 survivors and 2768 pairs, maximum target critical drift is
`0.01495`, and every numerical audit passes.

The prospective ordered path is exactly `2,2,3`, so the sampled saddle bracket
narrows to `[0.145,0.149]`. This closes the coordinate-coverage hole without
post-result relabeling. The next binding action is adaptive saddle-defined
continuation inside this interval and then through additional regular gaps;
the three samples alone do not establish a continuous global TBA curve.

## First blind midpoint frozen

EXP-122 preregisters `a=0.147`, the midpoint of the new sampled bracket, with
no expected branch count. For every run and coordinate, candidate counts two
and three are evaluated separately under the now-qualified coverage-censor
rule; exactly one must pass, and every one of 14 run--coordinate decisions must
agree. Seven new seed-126--128 ensembles span `2^14,2^15,2^16` section states
and retain all numerical and convergence gates. A two result narrows the
bracket to `[0.147,0.149]`; a three result narrows it to `[0.145,0.147]`.

## First blind midpoint result: EXP-122 passes

EXP-122 completes from clean commit `57e629b` in `272.07 s` and passes. Every
one of the 14 blind run--coordinate decisions uniquely selects two branches.
Of 210 variant cells, 207 resolve normally and three are admissible 80-bin `y`
coverage censors in the later-conditioned run. No cell is rejected or returns
three.

The weakest run retains 350 survivors and 3008 pairs. Maximum survivor drift is
`0.00568`, maximum across-run critical drift is `0.01499`, and all numerical
audits pass. The sampled saddle bracket therefore halves to `[0.147,0.149]`.
Freeze the next blind midpoint at `a=0.148`; retain the finite-bracket claim
until a separate continuation method establishes a continuous curve.

## Second blind midpoint frozen

EXP-123 preregisters `a=0.148` without an expected label. New Sobol seeds
129--131 use a `2^13,2^14,2^15` ladder, one power below EXP-122 because its
weakest run retained 350 survivors and 3008 pairs. The floors remain 100 and
1000, so inadequate support fails rather than triggering a post-result scale
increase. A two result yields `[0.148,0.149]`; a three result yields
`[0.147,0.148]`.

## Second blind midpoint result: conditioning consensus fails

EXP-123 completes from clean commit `a23770a` in `180.91 s` and fails. All six
300-unit runs select three branches in every `y` variant and every 30--80-bin
`z` variant. The 20-bin `z` cells under-resolve or fail bootstrap stability.
The 360-unit later-conditioned survivor subset instead selects two branches in
all 30 coordinate variants.

The split is not a numerical or support failure: the weakest run retains 200
survivors and 1737 pairs, survivor curves agree within `0.00403`, the period-4
cycle passes, and no integration or event audit fails. No blind label is
assigned and `[0.147,0.149]` is retained. Freeze a nested 360--480 conditioning-
horizon successor before any further spatial bisection.

## Nested conditioning-horizon successor frozen

EXP-124 uses new seeds 132--134 and conditions survivors through 360, 420, and
480 time units. Sixty-unit return windows remain centered at half each final
horizon. The 420-unit profile adds step halving, independent scrambles, and a
`2^15,2^16,2^17` ladder. All eight runs and both coordinates must blindly
select one common count while passing the original support, drift, survival,
cycle, and DOP853/Hermite gates. Passing establishes only 360--480 finite-
horizon stability; failure leaves `a=0.148` unlabeled.

## Nested conditioning-horizon result: topology resolves, power does not

EXP-124 completes from clean commit `1116860` in `505.33 s` and fails the
frozen all-run consensus requirement. Twelve of 16 blind run--coordinate
decisions select two; four are unassigned; none selects three. Of 240 oracle
variant cells, 228 resolve as two and 12 fail bootstrap stability. The failures
are exactly the three 80-bin variants in each unassigned decision.

The 360-unit baseline, three full-size independent 420-unit profiles, and the
doubled `2^17` 420-unit profile select two in both coordinates. At 480 units,
only 121 of 65,536 trajectories remain; both coordinates' 20--60-bin variants
still resolve as two, but the 80-bin bootstrap is underpowered. Step halving
and the `2^15` control likewise leave only the 80-bin `y` variants unassigned,
while the doubled sample restores a unanimous result.

Support floors technically pass with 121 survivors and 1061 pairs. Maximum
survival drift is `0.00223`, the period-4 reference passes, and DOP853/Hermite
errors remain far below threshold. The strict experiment therefore remains a
failure and `[0.147,0.149]` is unchanged, but the evidence rules out a resolved
return of the third branch through 480 time units. Freeze an independent
censor-aware PIM test at `a=0.148` before further spatial bisection; then measure
escape lifetime by branch to test the faster-escaping-third-branch mechanism.

## Independent blind PIM successor frozen

EXP-125 removes the sprinkler's final-survivor selection from the branch-count
decision. The already qualified censor-aware Nusse--Yorke construction refines
three fixed access lines and advances each successful PIM straddle for 800
returns at both 128- and 256-return lifetime ceilings. The target carries no
expected count and no sprinkler-derived critical-point reference. Both
coordinates and both horizons must unanimously select two or three across all
15 oracle variants, with at least two straddles, 1000 pairs, zero integration
failures, and the qualified critical-drift gates.

This adaptive DOP853 implementation is CPU-process parallel, not the qualified
fixed-step Triton sprinkler. It runs on the local reference host so a GPU
method change cannot contaminate the blind decision. A later GPU PIM port must
earn its own parity receipt.

## Independent blind PIM result: `a=0.148` passes as two-branch

EXP-125 passes from clean commit `982a729` after `4091.72 s`. All six fixed PIM
access lines complete: three at each of the 128- and 256-return censor ceilings.
Every profile contributes 2097 retained return pairs per coordinate. Both
coordinates at both horizons resolve as two across every oracle variant,
giving 60/60 two-branch cells, none three, and none unresolved.

The cross-horizon normalized critical spans are `0.008504` in `y` and
`0.004735` in `z`. The period-4 reference passes. Two 128-horizon lifetime
evaluations are right-censored and accepted only through the previously
qualified certified-block rule; the 256 profile has no censors. No adaptive
lifetime integration fails.

This independent stable-set-targeting result closes the rare-survivor power
failure in EXP-124 and qualifies `a=0.148` as a two-branch saddle at the frozen
finite censor pair. The sampled bracket narrows to `[0.148,0.149]`. It supports
the faster-escaping-third-branch explanation for EXP-123, but it does not prove
an infinite-lifetime saddle or a continuous TBA curve. Freeze the next blind
midpoint at `a=0.1485` and independently measure escape lifetime by branch.

## Next independent PIM midpoint frozen

EXP-126 applies the passing blind EXP-125 definition unchanged at
`a=0.1485`, the midpoint of `[0.148,0.149]`. The same three access lines, 128-
and 256-return censor ceilings, 800-return straddles, DOP853 tolerances, two
coordinates, and 15-variant oracle are retained. No expected count or previous
critical-point reference is encoded. A unanimous two result yields
`[0.1485,0.149]`; a unanimous three result yields `[0.148,0.1485]`; any gate
failure preserves the present bracket.

## Next independent PIM midpoint result: three-branch

EXP-126 passes from clean commit `e78ec6a` in `3840.50 s`. All six fixed access
lines complete and each horizon supplies 2097 retained pairs per coordinate.
Both coordinates at both the 128- and 256-return censor ceilings resolve as
three across all 15 oracle variants: 60/60 three-branch cells, no two-branch
cell, and no unresolved cell.

The combined critical spans are `0.014702` in `y` and `0.008531` in `z`; the
period-4 reference and every lifetime integration pass. Horizon 128 uses the
already qualified certified-censor rule for 119 censored evaluations and 104
certified selections; horizon 256 has no censor.

Because EXP-125 qualifies `a=0.148` as two under the identical PIM definition,
the finite sampled classifier transition is now bracketed in
`[0.148,0.1485]`. This is strong local invariant-set evidence for the topology
change inside the regular window, but it is still not an independently
continued TBA curve. Freeze the next midpoint at `a=0.14825` only after adding
a branch-conditioned escape diagnostic so localization and mechanism advance
together.

## Branch-conditioned escape diagnostic frozen

EXP-127 turns the proposed faster-escape explanation into a prospective test.
The six adequate 300-unit EXP-123 runs define two empirical `y` critical-point
uncertainty envelopes; no new lifetime data can move them. A trajectory is
assigned only once from its last oriented-section crossing before a time-150
landmark, and crossings inside either envelope are excluded. The leftmost
domain is the added branch; the other two certain domains are the pooled core.

Untouched Sobol seeds 135--137 each start with `2^16` conditions and are
followed to time 420. The primary statistic is extra-minus-core restricted
mean survival time after the landmark, with a 99% trajectory bootstrap interval
and a two-sided log-rank test. All three seeds must independently support
faster extra-branch capture. A same-ensemble half-step run must also preserve
the effect within the frozen aggregate tolerances. This is a mechanism test,
not a continuation of the TBA curve.

## Branch-conditioned escape result: faster capture rejected

EXP-127 completes from clean commit `f9a15b9` in `259.18 s`. Its support and
numerical-quality gates pass, but the preregistered scientific hypothesis fails
in the opposite direction. Extra-minus-core restricted mean survival time is
`+30.50`, `+30.86`, and `+29.98` on the three untouched seeds. Their 99%
bootstrap intervals are `[27.39,33.55]`, `[27.89,34.01]`, and
`[27.25,32.66]`. The half-step repeat gives `+30.90`, only `0.40` from the
baseline, and changes the extra-branch fraction by `0.00042`.

The distributions cross rather than exhibit uniform faster escape. Every
extra-branch trajectory survives 60 residual time units, but none survives
180. The core captures much earlier on average while retaining a 1--2% tail at
270. This delayed-but-bounded capture directly explains why the extra branch
can occur in the 300-unit survivor map and disappear under 360-unit
conditioning. It is a finite transient domain, not part of the PIM-resolved
two-branch saddle at `a=0.148`.

The failed mechanism does not alter the `[0.148,0.1485]` PIM bracket. It removes
the `a=0.148` transient branch as a valid substrate for the Jones reinjection
claim. Freeze the next midpoint under the identical blind PIM definition, then
define reinjection on the genuinely three-branch saddle continued from
`a=0.1485`.

## Next blind PIM midpoint frozen

EXP-128 applies the passing EXP-125/126 invariant-set definition unchanged at
`a=0.14825`, the midpoint of `[0.148,0.1485]`. The same six PIM access-line and
censor-profile combinations, adaptive DOP853 tolerances, 800-return
straddles, two coordinates, and 15-variant oracle remain binding. No expected
count or previous critical location is encoded. A unanimous two result yields
`[0.14825,0.1485]`; a unanimous three result yields `[0.148,0.14825]`; any
failure preserves the current bracket.

## Next blind PIM midpoint result: three-branch

EXP-128 passes from clean commit `61d9044` in `3492.09 s`. All six access lines
complete and both censor profiles supply 2097 pairs per coordinate. Both `y`
and `z` select three across all 15 oracle variants at both 128 and 256 returns:
60/60 three-branch cells, no two-branch cell, and no unresolved cell.

Cross-horizon critical spans are `0.009043` in `y` and `0.009093` in `z`. The
period-4 reference and all lifetime integrations pass. Horizon 128 records 31
censored evaluations and 29 certified selections under the previously
qualified rule; horizon 256 has none. The finite invariant-set classifier
bracket narrows to `[0.148,0.14825]`.

This second blind bisection strengthens local ordering but is still not a
continued TBA curve. The next step freezes a signed critical-point--to--support
boundary margin across the bracket and asks whether its zero predicts the
blind labels; further bisection alone has diminishing theoretical value.
