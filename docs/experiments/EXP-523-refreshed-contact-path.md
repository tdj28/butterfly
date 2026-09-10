# EXP-523 — Two steps with refreshed contact derivatives

Prospective, outcome-informed numerical continuation, 2026-09-10. Freeze and
push source, protocol, manifest and tests before target integration. No new
outcomes have been examined at protocol construction. This is not formal
preregistration or independent-team verification.

## Research question

Can the accepted EXP-522 fold/orbit contact be continued through two successive
parameter steps while the same physical inner maximum moves toward section
grazing? Refresh derivatives at each accepted point instead of repeatedly
extrapolating the original EXP-519 response. This tests a short sampled path,
not Jones's complete symbolic chain. C/D identification and the actual
insertion transition remain necessary subsequent work.

Start at the authenticated EXP-522 correction, a=0.21559338680106457,
b=0.2, c=7.147000000000001. Its sixteen normalized full-state contact residuals
are <=1.577918e-8. EXP-521's failed predictor remains failed. Its even-c
curvature diagnosis motivates a **new**, prospectively tested quadratic
prediction here; the diagnosis itself is not a successful forecast.

## Fixed algorithm and claim thresholds

At each of at most two accepted anchors, measure all eight stencil points:
a offsets +/-1e-5 and +/-5e-6, and c offsets +/-0.005 and +/-0.0025, holding
the other parameters fixed. Keep the four history-4/history-7, direction-0/1
fold constructions, both DOP853/Radau solvers, both periodic windows, historical
and Barrio counts 6/8, and every one of the sixteen stationary roots. No new
partition boundaries or symbolic names are assigned.

Require the unchanged 5% coarse/fine derivative consistency tests for all
six-component fold vectors and both inner gaps in every context. Estimate the
pure-c quadratic coefficient by the symmetric even part about the measured
anchor, scaled to c increment 0.005. Require 5% coarse/fine consistency of all
six-component quadratic vectors and all eight gap coefficients, with the
predeclared 1e-8 normalization floor. This is a local approximation: mixed
a/c and higher-order terms are not silently treated as zero truths.

The existing bounded linear predictor chooses a c step that reduces the first
maximum's absolute gap while restoring mean signed x-contact. Subtract the
mean quadratic c contribution divided by the fresh mean a slope from its a
step. Reject proposals outside the same +/-1e-5 a neighborhood; do not clip
and retry. Predict every fold-vector component and both gaps using fresh
linear derivatives plus the measured pure-c quadratic term.

Measure the prescribed point once. Preserve its complete prediction verdict:
all sixteen full-vector prediction errors <=0.1, contact radius <=1e-4, all
eight gap prediction errors <=0.1, and root-5 gap improvement in all four
contexts relative to this step's accepted anchor. Motion-denominator floors
remain 1e-12 for fold vectors and 1e-8 for gaps. Direct acceptance additionally
requires the stricter full-state contact radius **1e-7** in every variant.

If the predictor fails or is not tight enough, permit at most one normal
correction **only** when its actual geometry qualifies, all gap predictions
pass, all four root-5 gaps improve, and full-state contact remains <=1e-4.
Use only this step's fresh a derivative, with its complete original center
explicitly recorded. Hold the trial c fixed, bound the correction by 1e-5
and the current step's a-stencil domain, and test all new full-vector and gap
predictions against a new integration. Require every residual to improve
tenfold and to be <=1e-7; retain net gap progress relative to the accepted
anchor, not necessarily relative to the trial. An accepted refinement does
not turn a failed predictor into a pass. No second correction, step-size
retry, alternate target or third step is permitted in this experiment.

At every recenter, preserve the complete physical identity of all sixteen
roots by rotating **a copied reference census** into the previous anchor's
uniquely matched cyclic order. Never alter measured censuses/certificates.
Check that self-matching this reference returns exactly the tracked gap
objects. This addresses a pre-execution review finding: merely replacing
the reference with native event order can silently switch roots 5 and 13.

Stop the path on any unqualified response, missing bounded proposal, failed
correction, lost correspondence, count change or resource failure. Preserve
the accepted prefix and every failed trial. A future grazing/count change
requires a new two-sided protocol; do not relax the current count gates.

## Execution and full evidence audit

Authenticate the complete public EXP-519/520/521/522 inputs and the exact
source closure. Before target access, run analytic truth/negative controls,
rotated-root regression, scalar semantic-mutation tests, synthetic complete
writer/census/auditor and one-shot checks, and the real sealed python -I -B
consumer. Include a local adversarial pass; no paid review is requested.

Use the existing task-owned prax workspace and managed CPython 3.13 with the
committed uv.lock. Fetch only the exact frozen **public source and compact
inputs from GitHub**, using a single-ref blob-filtered no-checkout clone and
explicit sparse file closure. Check every required file physically exists
and matches its source hash. Do not upload old raw archives, credentials or
private files. Retain the new raw output on prax. No GPU rental or paid API.

One consumed marker, at most twenty measured points and 3200 IVPs, six-hour
target-execution wall cap, 2200000 censused periodic dense segments, 10 GiB raw-output cap,
20 GiB initial free space, 8 GiB free-space floor and 1 MiB failure reserve.
Preparation requires 21 GiB free before fetching dependencies. Segment count
is not a count of every stored mesh; the byte limit covers all run output.
Keep the compact audit receipt separately within a 128 MiB bound and preserve
failed preparation/launch directories. No attempt reset or automatic retry.
The following audit has a separate six-hour process-wide alarm, covering
fold replay, census traversal and receipt writing. The two scientific phases
therefore have a combined maximum twelve-hour envelope, not six hours total;
preparation/startup are separate. An audit timeout preserves raw evidence and
does not authorize re-execution of the consumed numerical attempt.

The frozen worker performs full raw fold/midpoint/guard/cycle replay and every
stored polynomial root-certificate audit before exposing a scientific result.
The auditor replays the adaptive sequence using the same accepted reference
at each point, separately checks scalar derivatives, curvature, proposals,
predictions, normal-correction authorization and accepted endpoints, and
accounts for all files, IVPs and periodic census segments. Geometry and
controller code are shared: this is not independent implementation evidence
and stored-polynomial completeness is not a rigorous exact-flow enclosure.

## Commands

```sh
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp523_refreshed_path.py --prepare
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp523_refreshed_path.py --startup
PYTHONPATH=.:python .venv/bin/python -B -m pytest -q tests/test_exp523_refreshed_path.py tests/test_exp523_runner.py
# After local checks, source freeze and public push to the immutable ref:
PYTHONPATH=.:python .venv/bin/python -B scripts/deploy_exp523_prax.py --commit COMMIT --rehearse
PYTHONPATH=.:python .venv/bin/python -B scripts/deploy_exp523_prax.py --commit COMMIT
PYTHONPATH=.:python .venv/bin/python -B scripts/deploy_exp523_prax.py --commit COMMIT --launch
```

A positive result establishes at most two locally qualified sampled steps
on this candidate contact branch. It establishes neither an exact continuous
critical locus, a grazing endpoint, a homoclinic connection, a C/D dictionary,
a Jones symbolic arrow, nor a global parameter-plane explanation.
