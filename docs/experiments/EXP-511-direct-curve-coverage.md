# EXP-511: direct coverage of the failed long-history curves

Prospective, outcome-informed local diagnostic. No paid review requested.
Target not yet executed when this protocol is frozen. It does not change any
EXP-510 file, threshold, failure, consumed marker or qualification decision.

## Question

At EXP-510's second parameter, Newton found four zeros with near-collapsed
input curves rather than qualified folds. Do the declared depth-eight curves
reach the qualified depth-four fold elsewhere in their original parameter
boxes? A fixed sampling diagnostic separates sampled coverage and possible
regular fold brackets from the collapsed roots. It does not retry Newton or
reduce continuation steps again.

The fixed parameter is a=0.21559488260076548, b=0.2,
c=7.162000000000001. Reconstruct the two depth-eight directions from the
qualified first substep and the original second-substep recipe. Compare with
all four qualified depth-four input/output state pairs at the same parameter.
The four already-audited collapsed roots are exposed diagnostic anchors,
extracted without integrations into a hash-bound public witness. They are
not qualified roots or replacement warm starts.

## Fixed matrix and numerical interpretation

Each curve has 17 uniform nodes across its original u-box, supplemented by the
mean of its two collapsed-root coordinates and mean +/- 1e-6. Sort and deduplicate:
at most 20 nodes per curve. Execute DOP853 and Radau at every node, each with
one guard and one full six-dimensional state/variational solve: at most 80
profiles and 160 IVPs. No target-dependent refinement or node replacement.
Use unchanged EXP-510 tolerances, time horizon, section, event ordinal and
regularity thresholds. There are no cycle or boundary integrations.

Compare all selected event states and times between solvers (scaled state
1e-6, time 1e-7), normalized input tangents (1e-6), and graph slopes
(1e-6 times max(1, absolute slopes)). Candidate brackets require regular
endpoints, matching orientation of the input x coordinate, opposite slopes
or an interior exact sampled zero with opposite neighbors, and agreement
between solver bracket sets. These are **numerical bracket candidates**, not
certified continuous-u brackets or isolated exact-flow roots. Gaps and input
turns remain unresolved, not silently bridged. All unsampled cells remain
uncertified even if endpoints are regular. No global absence claim is allowed.

Retain every profile, including explicit guard/main solver failures; unexpected
exceptions or resource exhaustion stop the consumed attempt and preserve its
prefix. A completed grid can contain failed or irregular measurements. This
does not make the scientific result successful. Report distances in the full
three-state input and output, using scales [15,15,0.01]. Sampled extrema and
ranges are not continuum bounds. No generating partition, homoclinic orbit,
exact contact or Jones symbolic chain is verified by this diagnostic.

## Evidence and controls

Save guard meshes and main meshes, every main dense polynomial coefficient
(DOP853 F or Radau Q), old states, both solver event lists with augmented
states, census reports, event-time-corrected tangents, starts, pairs and all
analyses. Capture numerical products before checking solver success.
The raw audit replays dense endpoints, solver event states, plane/velocity
root residuals, extrema partitions, bracketed plane roots, event algebra,
corrected tangents, complete pairs and curve analyses without new IVPs.
Separately coded scalar comparisons check distances and bracket decisions.
Extrema remain numerically detected, not all-root isolated. Dense replay is
an evidence-consistency check, not independent ODE validation.

Before the target, exercise the same capture/replay path on an analytic
rotating/contracting field: fold, no-fold, and projection-degenerate controls,
both solvers (six profiles, 12 IVPs). Check return times, full states and
event-corrected tangents against closed form within 1e-8; keep all raw control
products. Express the analytic z coordinate at physical scale 0.01 and
conjugate k to 10000 (or zero for no-fold), retaining target regularity
thresholds. Add target-free tamper, gap, exact-zero, solver-disagreement,
nonfinite, failure-retention and accounting controls. Existing bounded-writer
tests remain mandatory. Validate a copied-source consumer with no raw-artifact
access and run the full regression suite before source freeze.

## Resources, provenance and release

One exclusive target marker; no reset. Target wall cap 3600 seconds, total
output including final summary 2 GiB, initial free space 11 GiB, continuing
floor 8 GiB, failure reserve 1 MiB. All JSON/NPZ producer boundaries use
pre-write admission. Controls have a separate 64 MiB / 120 second / 12-IVP
cap. No cloud, API, upload or monetary spend is needed.

The executable manifest contains the complete fixed selection, inherited
numerical settings, input hashes and source closure. Freeze tested sources,
protocol and manifest in an explicitly staged, scanned, pushed commit; live
verify the exact remote ref before target execution. The runner refuses dirty
or mismatched source and replays hash-bound controls before consuming its
attempt. Preserve frozen bytes after exposure. Any new scientific refinement
requires a new prospective experiment, not editing this plan.

Release a local full raw audit and a compact public receipt/verifier with
tamper controls. State explicitly that compact public replay does not repeat
raw integration auditing. Update the research log with successes, failures,
coverage limitations and the next discriminating experiment. Normal merge
requires all final-head push and PR Python 3.12/3.13 checks green.

Verification ledger at freeze: new machinery is target-free control-tested
and isolated-startup-tested; target execution and raw audit are not yet done.
Later status belongs in updates/receipts, not edits to this frozen protocol.
