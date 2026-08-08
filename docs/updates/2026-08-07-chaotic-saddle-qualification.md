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
