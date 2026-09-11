# EXP-525 — one fresh predictor/corrector from audited historical calibration

This is the conditional second phase of the human-approved EXP-523 recovery,
not a restart or completion of EXP-523. EXP-524's completed private audit must
authenticate and qualify before any new trajectory. Its full receipt remains
access-controlled pending payload-specific public-release approval. No private
receipt or raw data is uploaded by this experiment: both already reside on the
existing prax host. Public source binds the receipt by exact hash and byte count.

## Question

Does the first bounded predictor from the qualified historical calibration
produce a locally qualified contact-preserving step, directly or after the
single normal correction permitted by EXP-523's original rules?

Freeze the first-step controller, not another calibration sweep. Reuse the
eight audited samples explicitly as historical inputs. Compute at most one
predictor and, conditionally, one new normal correction, each from newly
retained trajectory data in an EXP-525 namespace. Do not inspect or reuse the
interrupted EXP-523 predictor. Never count historical calls as new measurements.

## Unchanged scientific gates

Use the same initial EXP-522 anchor, all sixteen full-state fold variants,
all eight gap variants, both solvers, both cycle windows and complete
stationary-root correspondence. Preserve the historical/Barrio 6/8 event gates.
Any crossing-count change stops this continuation and requires separate
investigation; it is not automatically a Jones symbol insertion.

The quadratic predictor remains bounded by the original stencil. Its actual
full-state geometry must pass 1e-4 and predictions must pass relative error .1;
root 5 must improve in every context. Direct acceptance additionally requires
all contact residuals at most 1e-7. The original normal-correction eligibility,
fresh prediction checks, tenfold residual reduction, 1e-7 accepted contact,
and net progress relative to the original anchor remain unchanged. Preserve a
failed predictor even when its permitted correction succeeds. No second
correction, second continuation step or regenerated calibration is allowed.

Full retained-raw replay and separately coded scalar/census checks follow
collection. The scalar auditor receives a one-row internal projection with
the original two-step overall flag false; the successor separately checks its
one-step acceptance flag. This does not create an EXP-523 success summary.

## Operational limits and evidence

- One new attempt and namespace; 384 new IVPs and 200,000 census segments maximum.
- **Six hours total for collection plus audit**, with no extension or reset.
- Two GiB output cap, one MiB failure reserve, eight GiB free-space floor;
  initial free-space requirement eleven GiB. Existing retained data count
  against available disk; no old data are deleted or duplicated to qualify.
- Exact retained managed runtime: Python 3.13.13, NumPy 2.5.1, SciPy 1.18.0.
- Public-source physical-closure rehearsal and authentic same-host preflight
  run before the marker and before new integrations. Historical calibration
  access in preflight is explicit and guarded against any solver call.
- Record every attempted point, raw inventory, error and missing outcome.
  A collection summary alone is not a successful audit. A failure receipt
  prevents successful interpretation even if collection had completed.
- No new rented host, provider create or paid API request; no Pro review.

This sampled local step could support the next geometric test. It cannot
establish a continuous exact critical locus, grazing endpoint, homoclinic
connection, C/D dictionary, Jones arrow or complete parameter-plane explanation.
Report success, failed prediction, failed geometry and operational failure
under these same rules.
