# EXP-522 — Nonlinear refinement after the failed c-step predictor

Prospective outcome-informed experiment, 2026-09-10. Freeze and push this
protocol, source, manifest and tests before any new target integration.

EXP-521 completed and passed raw audit, but all sixteen linear fold predictions
failed the 0.1 relative-error gate. Its actual contact geometry qualified.
The post-run even-c curvature diagnosis explains most of that error but is not
a validated prediction. Nothing in this experiment changes EXP-521's verdict.

## One new measurement

Start from EXP-521's prescribed correction: a=0.21559346273240781,
b=0.2, c=7.147000000000001. Hold b and c fixed. Use the authenticated EXP-519
a derivative to subtract mean signed x-contact residual divided by mean
normalized slope. Bound the realized a step by 1e-5 and the original EXP-519
a-stencil domain. Record the old derivative's complete parameter center:
it is not the center of this new correction. There is no newly exact Jacobian.
The preliminary calculation from already-open parent data predicts
a=0.21559338680106457. It has not been integrated when this protocol is written.

Measure exactly one conditional correction, not another four-point c stencil.
Use all four history-4/history-7 direction constructions, DOP853 and Radau,
both periodic windows, unchanged primitive/correspondence checks, historical
and Barrio section counts 6/8, and the complete sixteen-root stationarity
census. Match all roots by unique cyclic phase/full-state/curvature identity.
The reference geometry, fold rows and periodic seed come from EXP-521's actual
correction. Both tracked inner maxima remain in the complete record.

## Predeclared decision and its references

All sixteen six-component full-state distances must remain <=1e-4; all sixteen
full-vector prediction errors and eight gap prediction errors must be <=0.1,
with unchanged motion-denominator floors 1e-12 and 1e-8. Predictions start at
the measured EXP-521 correction. In addition, **every** full-state distance
must decrease at least tenfold relative to that correction. This stronger
refinement criterion is tested with new data, not fitted to its outcome.

The first maximum must remain closer to section grazing in all four contexts
than at the **original EXP-519/520 c-step anchor**. This reference is distinct
from the EXP-521 trial. The fixed-c correction is predicted to sacrifice a
small part of the first maximum's c-step improvement while restoring fold
contact; demanding further gap improvement during this normal correction
would test a different objective. Therefore retain the old local progress
decision verbatim as a nested diagnostic, and report both references explicitly.
Do not relabel EXP-521 as passed, or describe this as monotonic progress from
its trial. The second maximum need not improve but must pass identity and
prediction. No tolerance or failed historical test is relaxed.

## Reproducibility, controls and resources

Authenticate complete EXP-519/520/521 receipts and numerical sources directly;
do not replay historical authorization or execute an older paid-review client.
A fresh sealed python -I -B consumer must validate the complete deployed source
and ancillary input closure without raw target data. Test known linear truth,
the distinction between local and net progress, nonlinear and full-state
failures, secondary-gap failure, wrong-point substitutions, plan tampering,
one-shot guards, scalar decision replay and the actual sealed consumer.

Use a clean live-pushed immutable source ref, a new output directory and one
consumed marker. Limits: 256 IVPs, 3600 seconds, 150000 **censused periodic
dense segments**, 1.5 GiB output, 10 GiB initial free space, 8 GiB free-space
floor, 1 MiB failure reserve. Segment accounting is not a bound on every raw
mesh; the byte cap bounds all output. These prospective resources are for one
point, rather than EXP-521's five. Record runtime versions before outcomes.

Audit every new raw midpoint/fold/guard/cycle and every stored polynomial root
certificate, with separate scalar parameter/prediction/decision arithmetic.
Producer and auditor share geometry; this is not independent-team verification.
Stored polynomial completeness is not an exact-flow enclosure. Preserve failed
attempts and all raw arrays locally. Public compact receipts do not provide
raw-data reproducibility or backup. No paid Pro call, GPU rental or private
data upload is requested or authorized by this protocol.

## Claim boundary

A positive result is one freshly tested nonlinear contact correction at fixed
c with net gap progress from the original anchor. It is not an exact critical
locus, a grazing endpoint, a C/D dictionary, a homoclinic connection, a verified
Jones symbolic arrow, or a complete parameter-plane explanation.

Commands (substitute the exact new pushed commit/ref and actual summary hash):

```sh
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp522_nonlinear_refinement.py --prepare
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp522_nonlinear_refinement.py --startup
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp522_nonlinear_refinement.py --execute --source-commit COMMIT --remote-ref refs/heads/codex/exp522-local-execution --output artifacts/EXP-522/target-COMMIT
PYTHONPATH=.:python .venv/bin/python -B scripts/audit_exp522_nonlinear_refinement.py --run artifacts/EXP-522/target-COMMIT --expected-sha256 SUMMARY_SHA --output artifacts/EXP-522/primary-audit-01.json
```
