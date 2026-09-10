# EXP-519 release-test portability correction

The final-head Python 3.13 push job 102981376472 (run 34509917046,
commit `73ff7772aea07847175778ffecc6dccd9bd30135`) failed the extra
dictionary-equality assertion in `test_real_complete_response_receipt`.
The public verifier itself passed: its complete source/input and numerical
replay checks did not fail. Linux reconstructed several prediction-error
norm ratios one or two binary64 units in the last place differently from the
saved macOS result. For example, `0.006322556522304345` replayed as
`0.0063225565223043465`. This is not a scientific threshold failure.

The post-run release test now permits at most four ULPs **only for the
norm-derived prediction-error field**. All keys, contact/prediction verdicts,
full-state distances and signed coordinates retain exact equality. Synthetic
regressions accept a one-ULP prediction difference and reject an eight-ULP
difference, changed verdict, changed distance and changed variant identity.
The production verifier, frozen experiment, scientific thresholds, original
receipt, figures and consumed attempt marker are unchanged. The original CI
failure remains in GitHub's job history; it is not relabeled as a pass.

The Python 3.12 push job 102981376155 subsequently completed with the same
single roundoff assertion failure: 3,049 other tests passed in 3,097 seconds.
It had no isolated-replay timeout. Both Python 3.13 jobs also failed only that
assertion (the PR job reported 3,049 passes in 1,952 seconds). The remaining
Python 3.12 PR job was still running at this checkpoint; no success is inferred.

The corrected local release suite passed **45 tests in 205.58 seconds**,
including the authentic complete receipt, isolated replay and all semantic
mutation controls (`artifacts/EXP-519/public-response-portability-01.xml`).
The narrow change does not alter or waive any historical startup timeout.
