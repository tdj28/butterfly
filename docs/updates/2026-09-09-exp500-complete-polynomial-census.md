# EXP-500: checking for crossings outside the old nomination boxes

EXP-499 is merged through [PR69](https://github.com/tdj28/butterfly/pull/69),
main `d2e8be5164c6abc54281bd089371d3acd7065ad1`. Its higher-precision reference
qualifies all old nominated crossings, but did not search the rest of each
trajectory. EXP-500 addresses that specific gap using the same saved data.

## What is being tested

All 64 coefficient archives, all 32 realized inputs and all 26 parent ledger
entries are retained. Exact rational polynomial arithmetic supplies a complete
segment-by-segment root census, including positive crossings, wrong-half-plane
crossings and the initial root. Accepted events must reproduce the old ordered
sequence without nearest-event selection, and both decimal configurations must
agree on the complete classified census. Original failed results stay failed.

The [protocol](../experiments/EXP-500-complete-polynomial-census.md) distinguishes
the stored piecewise polynomials from the exact flow. Root-count completeness
for those numerical polynomials would not establish a flow-level all-root
theorem, a second critical point, C/D, local winding or a Jones chain arrow.
Rounded mesh joins are checked explicitly, not silently bridged.

The count method uses established Bernstein/Descartes root isolation. A
separate verifier reconstructs coefficients by direct affine expansion rather
than rerunning the producer's de Casteljau search. Event classification is
replayed through the same rational interval implementation, not described as
an independently implemented geometry check. The shared implementation and
finite-precision trajectory limitations remain explicit.

## Pre-outcome findings and controls

Two first-pass test fixtures were wrong: the proposed simple-root cubic had a
repeated root, and a supposed one-level search failure actually separated in
one subdivision. They were corrected before freeze; repeated-root and actual
budget-exhaustion controls remain present. No target census was generated.

The first saved-analytic rehearsal was interrupted after 3:09 observed process
elapsed time. It had completed the three 40-digit controls but spent excessive
time parsing zero coefficients with very large negative decimal exponents.
`Fraction("0E-...")` constructs a huge power of ten unnecessarily. Conversion
through `Decimal.as_integer_ratio` preserves the exact rational value and
avoids that expansion; nonzero decimals and rational certificate strings have
regressions. The partial `artifacts/EXP-500/preflight-controls-01` directory and
the interrupted process's traceback remain; no analysis marker was consumed.
The first rehearsal is not claimed as a final-source qualification.

All six saved analytic controls pass in the fresh
`artifacts/EXP-500/preflight-controls-02` directory. Rotation, near-tangent
rotation and the polynomial/exponential control pass in both precisions,
including their complete root counts and old analytic root identities.
The focused suite passes **37 tests**, including a close root pair invisible
to endpoint signs, comparison with a separate Sturm implementation, exact
endpoint ties, unresolved repeated roots, certificate tampering, rational
classification, source/input closure and the actual isolated CLI startup.
Receipt: `artifacts/EXP-500/preflight-focused-03.xml`.

Paid review: not run under the human-approval policy. This uses local CPU,
retained coefficients and no new IVPs; no credentials, rental or raw upload.

Final prefreeze validation passes **2,287 tests with one Linux-only skip** in
155.53 seconds (`artifacts/EXP-500/preflight-tests-01.xml`). The final-source
saved controls, including direct certificate replay, take 1.84 seconds in
`artifacts/EXP-500/preflight-controls-03`. All 102 bound numerical/source paths
cover the observed import closure. The staged public scan passes on 2,753
files; paper references and the receipt-generated control table verify.
Source freeze and new target census follow these checks; these preflight
results are not the target result.
