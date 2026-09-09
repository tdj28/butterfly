# EXP-500: checking for crossings outside the old nomination boxes

EXP-499 is merged through [PR69](https://github.com/tdj28/butterfly/pull/69),
main `d2e8be5164c6abc54281bd089371d3acd7065ad1`. Its higher-precision reference
qualifies all old nominated crossings, but did not search the rest of each
trajectory. EXP-500 addresses that specific gap using the same saved data.

**The complete census and raw certificate audit now pass at all 32 inputs.**
All 64 profiles cover **239,072 segments** with no unresolved root regions,
failed mesh-join checks or ambiguous event classifications. The full census
contains 1,024 plane roots: 480 accepted downward crossings, 480 upward
crossings outside the half-plane, and 64 initial roots excluded by the time
guard. Both decimal configurations reproduce the entire original accepted
sequence. Nothing outside the original nomination boxes adds an accepted
crossing on these stored trajectories.

These are 32 fixed inputs evaluated twice, not 64 independent replications.
The full-horizon counts depend on history depth and perturbation sign; they
are not minimal periods or a measured `p -> p+1` periodic-family connection.

## What this changes

EXP-499 established accuracy agreement at previously nominated crossings.
EXP-500 now closes their **complete stored-polynomial census** limitation:
there is no hidden accepted crossing in the remaining numerical segments.
It also keeps all upward and excluded initial crossings visible. This supplies
a qualified event sequence for the next geometric and branch-domain analysis.

The exact arithmetic applies to the stored polynomials, not the true flow.
Agreement cannot bound their common ODE approximation error. Both reference
configurations land on the same root-isolation grid here; identical reported
times do not mean exact time accuracy. All EXP-498 failures, including the
cases investigated by EXP-499, remain unchanged.

## What was tested

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

## Frozen execution, audit and public replay

Source `966fd814bb62bbb42947fa357070a38c8f22bd11` was pushed and preserved at
`codex/exp500-local-execution` before the analysis. The runtime verified that
live ref, authenticated the entire original raw/source inventory, passed
controls and consumed `artifacts/EXP-500/analysis-once.json`. Do not reset the
marker or repeat this analysis as a fresh experiment. All 102 frozen source
paths remain unchanged.

Full local evidence is under `artifacts/EXP-500/census-966fd81`, summary
SHA-256 `418d3c7ec4a9e87be6db9cda485d2674c7b31d6387418fcdfb2f38b688514773`.
The separate count-certificate audit passed on all segments and inputs.
Its [public compact result](../experiments/receipts/EXP-500-complete-polynomial-census-result.json)
is byte-identical to `artifacts/EXP-500/primary-audit-01.json`: 1,926,485 bytes,
SHA-256 `e77a6ef000671836d272f0be6d6aaabc536c791682e88c74cff2fc79c548c54d`.
It retains all root records, classifications, comparisons and parent ledger
entries. Full coefficients and covering certificates remain local; no public
raw download, off-machine backup or separate-environment raw replication is
claimed. Public comparison replay is not the complete coefficient audit.

Final release validation passes **2,293 tests with one Linux-only skip** in
158.11 seconds (`artifacts/EXP-500/release-tests-01.xml`), including 43 focused
census/public-replay tests. The public replay recomputes all reported counts
and comparisons without loading private coefficient archives or integrating.
The staged credential scan passes on 2,756 files; manuscript references and
the receipt-generated symbolic control table verify. All 102 frozen source
hashes remain unchanged after the analysis and certificate audit.

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.verify_exp500_public_census \
  --result docs/experiments/receipts/EXP-500-complete-polynomial-census-result.json \
  --expected-sha256 e77a6ef000671836d272f0be6d6aaabc536c791682e88c74cff2fc79c548c54d
```

With the retained raw directories, a reader can also replay the frozen full
auditor into a fresh output path:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.audit_exp500_polynomial_census \
  --run artifacts/EXP-500/census-966fd81 \
  --expected-sha256 418d3c7ec4a9e87be6db9cda485d2674c7b31d6387418fcdfb2f38b688514773 \
  --output artifacts/EXP-500/reader-audit.json --public
```

## Next scientific step

Use the qualified decimal event sequences for the local geometric replay and
then high-precision grazing/branch-domain transport. The remaining obstacle
is not a missing crossing at these inputs: the second critical object or
consistent piecewise domain boundary still needs a measured relationship to
the primitive periodic orbit. Joint conditions in a and c, with minimal-period
guards and an explicit branch dictionary, precede a source-word comparison.
Do not count distinct upstream preimages as distinct physical critical points
or infer an arrow from different finite-time crossing counts at fixed parameters.
The separate legacy turning-point impact audit remains a manuscript-release
requirement. No paid Pro review is required for these routine next checks.
