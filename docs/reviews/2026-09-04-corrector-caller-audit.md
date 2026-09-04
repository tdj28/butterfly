# Corrector acceptance and caller audit — 4 September 2026

## Outcome

Two implementation defects were confirmed and fixed: segmented pseudo-arclength
correction omitted its arclength residual from the success gate, and nine
periodic-correction call sites in seven scripts could consume an unsuccessful
correction. This is a prospective safety fix, **not a finding that the historical
scientific results are false**. Frozen manifests and experiment receipts were not
rewritten, and no continuation campaign was rerun for this audit.

The relevant distinction is between optimizer termination and solving the
requested equations. A solver can terminate with a small flow-closure error but
an unacceptable phase or arclength residual. A visually closed trajectory does
not justify using that failed correction to qualify an orbit, update a Floquet
bracket, or certify an independent numerical check.

## 1. Segmented pseudo-arclength acceptance

`scripts/multiple_shooting_core.py::correct_arclength` already returned matching,
phase, and arclength residuals. Its `success` flag required optimizer success,
matching residual at most `1e-8`, and phase residual at most `1e-8`, but omitted
the arclength equation. Consequently, callers that trusted this flag could accept
a point away from the requested predictor hyperplane.

The flag now also requires `arclength_residual <= 1e-8`. The optimizer, matching
and phase thresholds, and scientific diagnostics are unchanged. Nonfinite
arclength residuals fail this comparison.

The inspected direct consumers of this shared corrector were:

- `scripts/validate_multiple_shooting_switch.py`
- `scripts/switch_multiple_shooting_high_period.py`
- `scripts/switch_augmented_flip_child.py`
- `scripts/switch_period320_flip_to640.py`
- `scripts/switch_jones_period12_segmented_child.py`
- `scripts/continue_jones_period24_segmented_child.py`

These consumers already check `status["success"]`, so the shared fix closes this
path without changing their experiment-specific acceptance rules. Other functions
also named `correct_arclength` are not automatically covered by this change.

### What the stored records show

A read-only historical scan for this audit examined dictionaries in
`artifacts/EXP-*/*.json` containing both matching and arclength residuals:

| Stored subset | Count or value |
| --- | ---: |
| Dictionaries with both residual fields | 426 |
| Those reporting `success: true` | 360 |
| Largest arclength residual among the 360 successes | `2.81009086948285e-12` |
| Reported successes with arclength residual greater than `1e-8` | 0 |

Thus this stored subset contains no demonstrated over-threshold success caused
by the missing gate. It is not an exhaustive revalidation: omitted diagnostics,
other file layouts, and earlier source revisions are outside that scan. A saved
residual is also not an independent integration of the saved trajectory.

## 2. Failed periodic corrections consumed downstream

`butterfly.correct_periodic_orbit` now qualifies optimizer termination, flow
closure, and phase together in its `success` field. The following callers did
not consistently honor that result; their later acceptance checks could rely on
closure, multipliers, or orbit similarity without checking the failed phase
condition.

| Script and call site | Previously unchecked use | Fix |
| --- | --- | --- |
| `compare_periodic_orbit_identity.py::corrected_from_rows` | Interpolated branch correction supplied to monodromy and orbit-identity comparison | Abort before monodromy if correction fails |
| `qualify_separated_normal_form.py::correct_fixed_b` | Fixed-parameter correction supplied to normal-form and identity diagnostics | Same guard in the shared wrapper |
| `refine_identity_constrained_flip.py::multiplier` | Failed correction could supply a multiplier for bracket refinement | Abort before computing multiplier or crossing count |
| `continue_periodic_orbits_in_b.py::main` | Initial family seed bypassed the success check used by subsequent steps | Abort before seed-row construction or continuation |
| `continue_period2_c_to_flip.py::main` | Independent-solver check consumed an unsuccessful correction | Abort before independent monodromy or identity checks |
| `continue_period2_c_arclength_to_flip.py::main` | Independent and reference re-corrections both lacked guards | Guard both corrections before their downstream use |
| `continue_period4_c_arclength_to_flip.py::run_arclength_continuation` | Same two verification paths | Guard both corrections before their downstream use |

These nine guards raise a descriptive error rather than emit a new passing
receipt. Successful corrections still follow the existing workflow and
experiment-specific thresholds. The fixed-parameter wrapper is also imported by
11 other scripts, so its guard applies to their future uses without changing
their frozen inputs.

### Explicit alternative acceptance policies are different

Not every use of an optimizer result with `success == false` is automatically a
scientific error. `continue_pim_upos_in_a.py::_correction_accepted` can apply
manifest-specified closure and phase limits while separately requiring optimizer
success. The period-6 switching code has an explicit, recorded,
residual-qualified termination policy. These are not the unchecked failure paths
fixed above. Similarly, the Hopf-to-hub script's final row qualification checks
closure and phase explicitly. This audit did not silently replace those policies
with new thresholds or retroactively reclassify their receipts.

## Verification and limits

New failure-injection tests cover:

- Closed, phase-fixed multiple-shooting output off the arclength hyperplane;
  dense and sparse Jacobians; zero, subthreshold, over-threshold, and nonfinite
  arclength residuals.
- All three shared periodic wrappers, including successful corrections,
  closed-but-phase-failed corrections, and unsuccessful optimizer outcomes.
- Failed initial seeds and independent verification corrections in the natural
  continuations.
- Both independent and reference verification failures in the period-2 and
  period-4 pseudo-arclength scripts, before dense identity comparison or receipt
  creation.

The focused check passed **31 tests**, including the existing periodic-corrector,
segmented derivative, and sparse/dense consistency tests:

```sh
python -m pytest -q \
  tests/test_multiple_shooting_acceptance.py \
  tests/test_multiple_shooting_parameters.py \
  tests/test_multiple_shooting_sparse.py \
  tests/test_periodic_caller_acceptance.py \
  tests/test_periodic.py
```

This was a bounded source-level caller audit plus injected-failure tests, not
an exhaustive examination of every historical solver, dynamically imported
caller, experiment acceptance policy, or saved trajectory. The fixes make future
failures explicit; establishing whether any older periodic receipt relied on an
unsuccessful correction would require its saved status diagnostics or a targeted
replay with the same inputs.
