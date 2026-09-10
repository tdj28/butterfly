# EXP-515: resolve the third-return sensitivity before changing the curve

## Question and timing

This is a prospective, outcome-informed numerical diagnostic, not a new
confirmation of Jones's symbolic chains. EXP-514 has already identified
grazing inside all five previously misleading fold brackets. A post-result
inspection of EXP-512's saved center/neighbor profiles found that event-time
projection first leaves a tiny tangent at return three, not only at return
eight. The correction subtracts substantial phase-direction components.
That algebra alone cannot distinguish real contraction from accumulated
integration error. No new target integration preceded this protocol.

Does the complete event-corrected tangent at each of the first three returns
agree between the existing 40- and 50-digit Taylor configurations, and do the
historical binary64 solvers resolve that same tangent? A positive result can
support a precision-consistent small nonzero derivative at these inputs. A
negative result identifies unresolved numerical sensitivity, not absence of
the physical fold. Neither outcome establishes a C/D partition, periodic-family
connection, zero full-flow Jacobian, exact-flow root census, or a Jones arrow.

## Fixed input and comparator matrix

Use EXP-512's public audited receipt with SHA-256
`c89bb30f90bf26a4f4902e349459b234201a66b00d3d2b4a500d6849fdb96e76`.
Take nodes 8, 9 and 10 in both original directions, without selecting a subset.
Both historical methods have exactly identical initial state and tangent at
each node: six distinct IVPs, each integrated at both decimal configurations,
giving twelve new target IVPs. Both historical solver comparators remain.
The old raw audit is not repeated by authenticating this public receipt.

Preserve the exact binary64-realized initial state, tangent, parameters and
legacy section using `Decimal.from_float`, not decimal reinterpretations of
short printed values, unrounded affine initial inputs or a newly computed
high-precision equilibrium. Reconstruct the legacy binary64 section with the
existing model implementation and record its exact converted values. The
parameter is a=0.21559488260076548, b=.2, c=7.162000000000001.

The horizon is 18: ceil(maximum saved third accepted time + 1), validated
across all twelve old profiles. Start at time zero and retain every state and
variation Taylor coefficient. The complete stored-polynomial section census
uses the unchanged EXP-500 rules: downward crossings, x below the frozen small
equilibrium, angle at least 1e-7, initial-root exclusion through time 1e-8,
root boxes at most 1e-25, and no unresolved roots or joins for qualification.
Every crossing is reported, including rejected directions and initial roots.
Require exactly three accepted returns within this horizon for target parity.

## Numerical comparison and possible outcomes

Use precisely the existing decimal-40/order-24/step-.02 and
decimal-50/order-32/step-.01 configurations, unchanged state/tangent tail and
magnitude guards, no fallback and no adaptive precision search. This compares
two precision/order/step profiles, not precision alone or independent methods.

Evaluate state and variation at the rational midpoint of each certified
polynomial root box, never at a float-converted time. Project
`v_section = v - f * v_y/f_y`. The y component is identically zero.
Also evaluate rational interval bounds for the same expression over the whole
root box. Report scaled Euclidean norms using [15,15,.01], box-radius estimates,
complete vector differences, and subtraction conditioning. Decimal renderings
of these interval diagnostics are not validated global ODE error bounds.

Paired target qualification requires complete same-classification event
censuses; all event times agree within 1e-12 and states within 1e-9 in scaled
max norm. At each of the three accepted ordinals, nonzero corrected norms
must agree in vector relative error within 1% of the smaller norm, and each
root-box radius estimate must be at most .1% of its norm. Failure is
`unresolved`, not zero. Record every failed ordinal and continue all twelve
IVPs unless an execution/resource guard prevents safe collection.

Compare both old solver tangents to each decimal profile at all three ordinals,
using the same 1% vector-error diagnostic and reporting absolute errors too.
Old/new time and full-state parity must pass before interpreting tangent
differences. Do not let an absolute tolerance larger than a tiny tangent
declare it resolved. Report whether the resolved third-return gain is below
the historical 1e-4 minimum, but do not change or rerun that depth-eight
acceptance gate. No old verdict is overwritten.

## Controls, evidence and resources

The exact producer and census run six analytic constant-field cases at both
configurations: ordinary transverse sensitivity, pure phase sensitivity,
phase plus a 1e-14 z component, an exact initial root, a root at 1e-10, and
a root at 2e-8. The field is (1,-1,0); analytic state, variation, crossing time,
acceptance and corrected tangent are known. These twelve control IVPs test
cancellation and both sides of the initial exclusion boundary. Separately
coded scalar coefficient-recurrence checks and independent polynomial
certificate verification audit their retained raw products and every target.
Same-agent audit is not independent-team replication.

Freeze the runtime, analysis, audit, tests, source closure and machine plan;
pass analytic controls, isolated startup, tamper tests and full regression;
push and live-verify the exact source before creating the exclusive attempt
marker. Retain partial outputs and failures; never reset a consumed attempt.
The target cap is twelve IVPs, 3600 seconds and 2 GiB including summary.
Initial free space must be at least 11 GiB; continuing floor 8 GiB; reserve
1 MiB for failure evidence. Controls have a separate twelve-IVP, 180-second,
64-MiB cap. Every compressed write, including gzip close, and every JSON
product requires pre-write quota admission. Raw archives remain local;
code, compact audited receipts and figures may be published.

No paid review, GPU job, external raw upload or registry submission is needed.
Pro is not requested under the human-approval policy. Stop for new authority
if external spending/ownership, raw egress or the research scope must expand;
do not manufacture success by altering scientific gates. A subsequent
representation change needs its own prospective test; reference-guided
recentring is calibration, not independent validation.
