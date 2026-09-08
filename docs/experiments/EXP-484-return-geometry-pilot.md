# EXP-484: direct, two-dimensional first-return geometry

Status: prospective local exploratory pilot; no symbolic verdict is promised.
Routine local audit under the human-controlled review policy; no paid review.

EXP-483 found that the four-pair selector discards much of the available early
support, while late-time concentration persists. Of the four original fits
that reached held-out evaluation, about 97% of unsupported rows lie outside
the fitted endpoint interval. These findings motivate direct local flow
geometry instead of enlarging an empirical scalar fit's endpoint domain and
calling it a validated partition.

## Fixed test

Use both nominated cases, a=0.21575 and 0.21577, b=0.2, c=7.212. From the
authenticated fine-step EXP-482 profile's original early-window **calibration**
cohort, select one actual source crossing per original 40-bin input cell:
lowest global seed ID, then lowest original stratum. No held-out states,
target words, median states, interpolated points or new parameter nominations
enter selection. Empty bins fail preparation. This is geometry-directed
coverage, not a random independent sample or an invariant-curve construction.

At all 80 selected states, integrate the first return and its two section
tangent columns with DOP853 and Radau. Retain every detected oriented event,
including the initial root and any gate-rejected roots. Exclude the initial
root using the frozen time guard. Compare solver states, times and the
event-time-corrected 2D Jacobian, as well as the saved RK4 next return.

For bins 0, 10, 20, 30 and 39 of each case, also compare the variational result
with centered DOP853 finite differences in both section coordinates, at two
fixed step sizes. Ten states receive this extra check; the other 70 must not
be described as finite-difference validated. The complete matrix is **240
target integrations**, plus two analytic rotation/contraction controls.

The machine plan freezes tolerances, scales, a 20-unit per-integration horizon,
all comparison limits and missing-return handling. All points and failures
are reported; numerical comparison failures do not authorize changed limits
or a consumed-slot retry. Runtime/integrator exceptions stop the run and retain
the failure, completed trials and started-trial records.

## What the derivative means

For the section normal n, fixed-time flow tangent Phi and return velocity f,
the return-time correction is

`DP = (I - f n^T / (n^T f)) Phi E`,

where E contains the two initial section-coordinate directions. This follows
by differentiating the defining section equation with respect to the initial
point. Omitting the event-time correction would differentiate a different map.
The implementation rejects insufficiently transverse events; the detected
roots are numerical solver events, not interval-certified exhaustive roots.

A partial derivative with respect to x at fixed z is **not** the derivative
along an invariant return curve. A zero in that partial cannot be assigned
Jones's C or D. To test projected folds next, a curve tangent or a justified
quotient must be supplied independently. This pilot supplies local flow data
for that task; it does not establish a generating partition, double critical
membership, a symbolic chain, a chain arrow or a homoclinic orbit.

## Release and preservation

Before the source freeze, 30 focused synthetic/diagnostic tests passed. The
full suite then passed **1,818 tests**, with one pre-existing Linux-only skip,
in 113.49 seconds. No EXP-484 target integrations were performed by these tests.

Implementations: `python/butterfly/return_geometry.py` and
`scripts/run_exp484_return_geometry.py`; machine plan:
`experiments/manifests/EXP-484-return-geometry-pilot.json`.

The CLI requires a clean committed source equal to its pushed upstream SHA,
verifies the preserved campaign/analysis/diagnostic anchors and each selected
profile hash, saves the actual source states, and runs the analytic controls
before consuming a unique `artifacts/EXP-484/target-once.json` slot. `--execute`
is explicit. A preflight without it never performs target integration.

The local wall limit is 1,800 seconds and output limit 32 MiB, with a per-trial
write reserve and a 240-integration cap. Each trial saves raw detected event
states, tangents and configuration. The final inventory records file hashes
and sizes. No original EXP-482/483 evidence, historical review response or
attempt marker is changed. No upload, cloud rental or paid API is involved.
