# EXP-508: continue with the fold constraint explicit

## Execution outcome: preserved controller failure

The frozen source 709af03fe9a8f6c6d9b5480a886cb7d0a2c3ce5a was pushed and
live-verified before execution. The predictor producer completed its raw point
after 196 IVPs. The controller then raised a TypeError while reading the
missing contact envelope of an unqualified point. No corrector ran and no
original summary or point-comparison record exists. The failure and complete
raw inventory are retained and hash-verified. This is not an accepted step.

The separate [EXP-509 forensic replay](2026-09-09-exp509-failed-predictor-replay.md)
repairs reporting prospectively without changing any EXP-508 frozen source,
raw evidence, consumed marker or tolerance. Its full 196-IVP raw replay now
passes: depth-8 input-curve collapse caused a legitimate fold rejection. Both
short-history folds miss contact tolerance, despite a 6.735% boundary-gap
reduction. EXP-508 remains failed and no step is accepted.
The pre-target text below is the historical checkpoint, not current status.

## Pre-target checkpoint

The [two-stage protocol](../experiments/EXP-508-constrained-contact-step.md)
is implemented. One lower-c predictor is followed by one fixed-c correction
when its numerical qualification permits it. All raw predictor and corrector
records are retained. The predictor-only result is a declared baseline: a
correction is not assumed to help and a favorable predictor cannot replace a
failed prescribed correction.

The initial 39 controls passed in 3.86 seconds. Before freeze, the plan was
tightened to avoid binding platform-specific matrix-diagnostic bits: the
diagnostics remain in execution evidence, and plan-bound predictions use
scalar sums with a NumPy arithmetic cross-check. No target outcome had been
generated. The earlier unfrozen plan is preserved at
artifacts/EXP-508/unfrozen-plan-draft-01.json. The revised **41 controls pass
in 3.06 seconds**, including a known linear solution, all conditional stages,
full-state versus scalar rejection, predictor-only baseline, original/start/
adjacent identity failures and inherited exact-byte/quota controls.

The authentic isolated copied-source startup passes with 87 source paths and
94 total source/input paths. All 34 original analytic-control files hash-check
and replay without new integrations. Receipts are retained in
artifacts/EXP-508/preflight-startup-02.json and preflight-controls-01.json.
The full suite passed **2,524 tests**, one Linux-only skip, in 183.39 seconds
(artifacts/EXP-508/pretarget-suite-01.xml). Citation/figure and symbolic-table
checks pass. The staged public scan passed 2,851 tracked files. These checks
precede the source freeze and live remote verification; no target has run yet.

Machine-plan SHA-256:
`2acbf461a885f28a25fdeea040ed8340c2d3327784edbd1f4e69480b47c7d1d2`.
The predictor is a=0.21559892539912653, b=.2, c=7.152000000000001. The corrector
is a frozen formula applied to that new measured point, not a manually selected
second point. At most two points, 1,024 IVPs, 3,600 seconds and 3 GiB of complete
output are allowed, with a 12 GiB initial reserve and 8 GiB continuing floor.

## Local design audit

The model is deliberately limited: its a column is the observed EXP-504/507
secant, while its c column is inherited from the original fine stencil. It is
not a new full-Jacobian measurement. Every measured component is reported, and
neither a favorable combined norm nor a mean alone licenses acceptance.

Acceptance needs a completed prescribed sequence, full-state fold proximity
at the unchanged 1e-4 radius, all numerical and primitive-cycle qualifications,
all original/start/adjacent identity checks, a smaller worst full-state boundary
distance and a smaller absolute boundary residual in every correlated variant.
The baseline exposes whether explicit correction is necessary at this step.
The sole scalar-floor waiver also requires full-state proximity; a zero scalar
residual cannot conceal a failed three-dimensional distance.

Both stages use the already tested complete-output writers. Summary references
avoid duplicate raw journals, and the raw audit counts the entire directory,
including its summary. Storage is planned for both points, not just the first.
This same-agent local audit is not independent scientific replication. No paid
review, new cloud worker, remote computation, raw upload or deletion is needed.
Jones's symbolic chains remain unverified, not debunked. The new run and full
raw audit must finish before the next scientific interpretation.
