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
