# EXP-500: complete section-root census of the retained decimal polynomials

Status: prospective, outcome-informed saved-data diagnostic. EXP-499 and all
earlier results are known. No trajectory will be integrated or replaced.

## Question and scope

Do the complete plane-root censuses of both retained decimal configurations
agree at all 32 EXP-499 inputs, and do their accepted downward half-plane
crossings exactly reproduce the previously nominated sequence?

The strongest possible result is a complete, numerically consistent event
sequence for these **piecewise numerical polynomials**. It is not an all-root
proof for the exact flow, a repaired EXP-498 verdict, a winding measurement,
a smooth second critical point, C/D, an invariant quotient, or a Jones arrow.
Missing crossings, ambiguous classifications, disagreeing configurations and
unresolved root regions remain visible. There is no preferred solver or subset.

## Fixed input and representation

Use all 64 full coefficient archives from EXP-499, anchored by its summary
SHA-256 `340617c9dfde4240a468b04574f87dc01c2cc3f13a6e488d933050adef1deab3`
and audited compact SHA-256
`d8e01f7cf572f5a77a0319fc59aa465f6e5f2ce9c590d613c7ebbd7cfd29c8d5`.
Retain all 26 original ledger entries and all 32 realized inputs, including
both original failed pairs and EXP-499's additional method discrepancy.

Read each stored decimal coefficient as an exact rational. On segment i, use
its Taylor polynomial over `[t_i,t_(i+1)]`, with the last endpoint the exact
stored horizon. This gives a complete partition without decimal-subtraction
gaps. Check that each domain width matches its stored step to the existing
10^(-digits+8) replay tolerance. Polynomial values at a join can differ because
step advancement was rounded: record the largest scaled jump and require
at most 1e-20, plus equal plane signs on the two sides (or two exact zeros).
A sign mismatch or one-sided exact zero makes the complete profile unresolved;
do not silently insert a bridge crossing. These are finite-precision numerical
curves, not an exactly continuous flow solution.

## Root-count method

Transform each plane polynomial to u in [0,1]. Clear rational denominators
using a positive multiplier. A strict constant-dominance bound can exclude
roots on the whole closed interval cheaply. Otherwise convert the full
polynomial, without degree truncation, to its Bernstein basis. For power
coefficients a_i and degree n, b_k = sum(i<=k) a_i C(k,i)/C(n,i).
The transformation u=v/(1+v) gives coefficients C(n,k)b_k for positive v.
Descartes' rule therefore gives no interior root for zero sign variations,
and exactly one simple interior root for one variation. Ignore zero
coefficients when counting variations. Subdivide with integer de Casteljau
arithmetic when more than one variation remains. Explicitly retain endpoint
and exact subdivision-point roots; never rely on endpoint sign changes alone.

This is established root-isolation methodology, not a proposed new algorithm;
see the [SageMath real-root isolation documentation](https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/real_roots.html)
(version 10.8, inspected 2026-09-09). Our small implementation uses exact
integers/rationals, no degree/precision reduction, and is not a Sage execution.

Isolate each simple root to absolute time width <=1e-25. Maximum subdivision
depth 160, maximum 2,048 search nodes per segment and 256 refinements per
single-root interval. An identically zero polynomial, repeated nondyadic root,
or exhausted bound produces explicit unresolved intervals, not an empty census.
Each segment retains a covering leaf certificate; root-free leaves and
one-root leaves together cover the complete segment, with exact endpoint roots
separately retained. A separately coded verifier reconstructs each leaf's
Bernstein coefficients by direct affine power expansion, not by replaying
the producer's subdivision recursion. Exact polynomial fixtures compare
against the existing separate Sturm implementation and known roots.

## Event classification and comparisons

Compute rational interval bounds on all three coordinates, polynomial y
derivative and the actual vector field over each isolated root interval.
Require matching definite polynomial/field direction and crossing angle >=1e-7
using the squared lower-bound velocity/upper-bound norm inequality. Classify
half-plane membership only if the complete x interval is strictly below or
strictly above the original bound; ties remain unresolved. Retain every root,
including positive direction, wrong half-plane and the initial-time exclusion.
Accepted means downward, inside the half-plane, and time strictly after 1e-8.
An interval straddling that time cutoff is unresolved. Exact same-time roots at
a mesh join are grouped only if both classified records agree; retain their
segment witnesses rather than silently dropping a duplicate.

Require equal ordered root counts and classifications across both configurations
and every paired time/state discrepancy <=1e-12/1e-9, scaled by (15,15,.01).
Compare the entire accepted sequence in order with each configuration's old
EXP-499 nominations, using those same thresholds. Counts must match before
pointwise comparison; no nearest-event selection. Report all root records,
counts, classifications, join diagnostics, unresolved regions and comparisons.
Zero accepted events cannot qualify this particular nonempty parent sequence.
Tiny paired differences remain discrepancies, not absolute error estimates.

## Controls, failure and release

The same census/verification/classification functions must pass synthetic
polynomials with zero/one/two closely spaced roots, exact endpoint and midpoint
roots, a repeated root, an identically zero polynomial, and a forced depth
limit. Test sign/direction/half-plane/cutoff ambiguity, inconsistent joins,
omitted certificate leaves, missing profiles and altered parent identities.
Replay both configurations of EXP-499's saved analytic controls without any
new integration; expected plane roots come from their analytic identities.
The exact isolated source checkout must load and run the real control CLI
without ambient repository imports or bytecode writes.

Local CPU only. No paid review, rental, credential loading, raw upload or new
IVP. Bound each execution/audit phase by 7,200 seconds; execution output <=512
MiB, initial free space >=9 GiB and runtime floor >=8 GiB; <=1,000,000 segments.
Freeze and push source, protocol, plan, tests and analyzer before the new census.
Rehash raw inputs and check the authentic startup path before consuming the
new exclusive `artifacts/EXP-500/analysis-once.json` marker. Never alter an old
marker or source. A structural/runtime failure stops and preserves partial
evidence; mathematical unresolved cells do not stop other planned profiles.
Keep full certificates local and publish an audited compact all-event table
with the raw dependency limitation explicit. No formal manuscript release or
new theoretical novelty is claimed. New cost, upload or scientific-scope
authority must be obtained if needed; no such expansion is part of this plan.
