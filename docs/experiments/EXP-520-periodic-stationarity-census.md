# EXP-520: where could the periodic orbit acquire an extra inner return?

## Question and timing

EXP-519 restored a numerical full-state proximity test to one return-map
fold. It did not identify D, a double-critical center, or a Jones symbolic
arrow. This successor asks a narrower, directly geometric question: on the
**actual primitive periodic orbit**, which stationary y-coordinate is closest
to the historical section through the small equilibrium? Does the same
object recur in both integration methods and both repeated cycle windows?

This is a prospectively specified saved-data follow-up informed by EXP-519's
published contact results, not an independent replication of that experiment.
The new root census and extremum gaps are not opened before the complete
source/plan is committed and live-pushed. Preflight reads only original known
parent results, file hashes and array headers. A metadata probe initially used
a removed private NumPy header helper; it failed at import before opening data.
The replacement uses public version-specific header readers.

## Complete input set, without new integrations

Use all five EXP-519 points, in their original order: coarse-minus,
coarse-plus, fine-minus, fine-plus and the prescribed correction. At each,
use both DOP853 and Radau observations, each covering 2.5 periods, and both
phase windows `[0.25T,1.25T)` and `[1.25T,2.25T)`. The ten immutable NPZ
observations contain **417,460** dense segments (55,520 DOP853; 361,940 Radau).
The machine input inventory records exact original summary-bound hashes,
sizes, shapes and binary64 dtype. No new IVPs or GPU work are authorized by
this plan. No raw upload or paid review is needed.

The fixed EXP-519 audit receipt and its original raw summary SHA are the
upstream evidence. This run authenticates all ten selected observation files
against that summary; it does not rerun EXP-519's entire 513-IVP audit. The
receipt can be copied byte-for-byte from its published source branch if its
release PR has not yet merged. No unmerged EXP-519 execution code is required.

## Exact polynomial census and its limits

In the Rössler field, `dy/dt=x+a*y`. On every saved dense segment this linear
state function is a polynomial: degree at most seven for DOP853 and three
for Radau. Interpret each binary64 coefficient and parameter as its exact
rational value. Construct all three state polynomials using the producer's
alternating dense-output recurrence. The auditor reconstructs DOP853 through
an independently expanded `x^p(1-x)^q` basis; Radau's stored power basis is
direct. Its scalar certificate verifier uses direct affine Bernstein
coefficients instead of the producer's subdivision recurrence.

The established exact-rational polynomial-census helper supplies complete
segment coverage, sign-variation counts and root brackets. Root time-box
width is at most `1e-15`; search bounds are depth 160, 2,048 nodes per
segment and 256 single-root refinements. Zero polynomials, unresolved
multiple roots and exhausted searches remain explicit unresolved intervals.
They cannot be treated as zero roots or dropped to make the profile qualify.

All segment endpoints are checked against retained mesh states. Shared exact
endpoint roots have one owner and both witnesses. A stationarity-sign jump
between adjacent polynomials, a shared-root disagreement or normalized state
join/mesh discrepancy above `1e-10` prevents completeness qualification.
These are certificates for the **stored polynomials**, not interval
enclosures or exact-flow all-roots proofs. Ordinary SciPy callbacks are a
comparison, never the source of the complete census.

## Geometry and predeclared comparisons

For every root retain its rational time and state boxes, midpoint state,
signed `g=y-y*`, normalized `g/15`, z displacement from the equilibrium,
full speed, `d²y/dt²=-y-z+a(x+a*y)`, curvature sign, and the derivative of
the stored y polynomial. A regular accepted candidate requires nonzero
interval curvature sign, normalized stored-derivative/field discrepancy at
most `1e-7`, and normalized root-state interval width at most `1e-9`.
The derivative of the dense interpolant need not equal the original ODE
field identically; that distinction is reported rather than concealed.

Compare every ordered root with the original callbacks over the full saved
observation, then compare both phase-aligned windows and both solvers.
State difference uses maximum coordinate error scaled by `(15,15,0.01)`
at most `1e-6`; phase difference is at most `1e-7`. Window boundaries need
root clearance exceeding `1e-7` in phase. Equal counts, ordered identity,
all-root completeness and regularity are required before local nomination.
A mismatch is a result, not permission to resample or widen a threshold.

Only within a qualified point, nominate the root with smallest `|g/15|`.
All four method/window contexts must select the same ordered root index;
the gap to the second-smallest absolute residual must exceed `1e-7` in
every context. Otherwise retain all roots and report ambiguous nomination.
No cross-parameter branch identity is inferred solely from a matching
ordinal: a later continuation must validate that identity.

At exact stationarity, `g=0` gives `x=x*` but leaves z free. If
`z=z*+delta`, the field is `(-delta,0,(x*-c)delta)` and the y acceleration
is `-delta`. A projected-center passage with nonzero delta is therefore a
regular section tangency, **not an equilibrium approach or homoclinic proof**.
No C/D letter or verified word arrow follows from small `g` alone.

## Verdicts, resources and execution

All ten profiles and all twenty windows are released, including failures.
The primary outputs are complete root inventories, original-callback
agreement, method/window correspondence, and whether nearest-object
nomination is qualified or ambiguous. No target value, slope, parameter
correction or acceptance radius for 'grazing found' is selected here. Results
guide a separate periodic-family continuation, without reusing a stale
transient-boundary distance or an old parameter Jacobian.

The source inventory binds the runtime, auditor, tests, protocol, package
imports and dependency lock. An isolated startup on the exact file allowlist
must import the real consumers, validate the plan and run analytic controls
without reading raw trajectory coefficients. Tests cover actual SciPy dense
replay, same-sign hidden roots, tangent/multiple roots, unresolved intervals,
joins, certificate mutations and ambiguous nomination.

Each producer/audit phase has a 7,200-second limit; the producer admits at
most 500,000 segments and 256 MiB of JSON output, reserving 64 KiB for a
failure record. Initial free disk must be at least 9 GiB and the continuing
floor 8 GiB. Writes are size-admitted before file creation. The only target
attempt creates `artifacts/EXP-520/target-once.json` after all preflight
checks and before opening trajectory coefficients. Consumed markers and
partial products are never reset or overwritten. Frozen sources and raw
hashes are checked again at completion. The whole saved-data census runs
immediately when its source, local tests, public push and resource gates pass;
unrelated release-CI waiting is not a scientific gate.

Paid review: `not_requested-human-approval-policy`. Local source and numerical
audits apply; no review approval is fabricated. Permitted claim: a complete
stored-polynomial census under the stated numerical comparisons. Forbidden:
exact-flow completeness, D identification, homoclinicity, zero full-flow
Floquet multiplier, a verified Jones arrow or an entire-plane explanation.
