# EXP-480 — Historical-section successor design

Status: draft executable and synthetic controls implemented; review and execution
freeze pending. No new target trajectories, fits, or words generated.

## Objective and fixed inputs

Determine whether the two EXP-479 exploratory nominations support a defensible
historical-section symbolic test. Retain **both** `local-a025-c083` and
`local-a027-c083`; do not pick the one that more closely matches a desired word.
Their parameter values are `(0.21575,0.2,7.212)` and `(0.21577,0.2,7.212)`.
The result-dependent selection is disclosed: these are nominated follow-ups,
not new independent discovery samples or exact doubly-critical centers.

Inputs must bind the complete EXP-479 analysis receipt
`4147ff20adefb6adf536137cb0a92809446ce66d40c20b6c00f909fa6235755f`
and EXP-204 candidate input
`71aab52016abc8163887b2bdfd4e8124bde0e436be2239751f19d29bed490012`.
The complete source/raw/fit/input bundle is verified on prax; see the
[EXP-479 result](../updates/2026-09-06-symbolic-scout-results.md).

## Existing evidence that must not be counted again as discovery

- The candidate input already contains corrected flow orbits and six
  historical-section versus eight Barrio-section crossings. Reintegrating
  them would be a numerical cross-check, not discovering new cycle lengths.
- EXP-176 qualified a neutral partition at `(0.2,0.2,20)`, not here.
- EXP-185 qualified the operational historical alphabet only at that control.
- EXP-186 failed the exact printed landmark word test; EXP-190 found only one
  historical x critical point in a different neighborhood. Neither failure
  may be erased or generalized to the current nominations without a test.
- EXP-479 nominated using Barrio z residuals. Its orbit indices `[7,5]` are
  not critical letters in Jones's historical six-return representation.

## Execution worklist

1. **Freeze an event-transport feasibility pilot.** Independently reintegrate
   both corrected cycles with DOP853 and Radau, retaining full event times,
   states, solver failures, closure/phase errors, and normalized crossing
   angles on both declared sections. Check the complete ordered return sets
   and possible shorter recurrence periods. Use phase alignment only for
   numerical cycle comparison, not to manufacture a historical word. This
   shares the repository's shooting formulation; it is not an independent
   continuation-method replication.
2. **Specify the historical-section sample and scalar-map test.** Fix seeds,
   event rules, capture definitions, finite horizons, calibration/validation
   separation, and graph-likeness/coverage/uncertainty metrics before new
   survivor outcomes. Record full raw events and failures. The asymptotically
   attracting cycle alone cannot supply an independent partition cloud.
3. **Separate section changes from sample-selection changes.** A different
   section can change capture decisions and hence which survivors are retained.
   Comparing independently selected clouds would confound that change with
   geometry. The design must either track both sections on a common retained
   trajectory population or explicitly quantify and report this conditioning
   difference. Do not silently reuse Barrio survivor labels as historical ones.
4. **Test critical membership before historical labels.** Infer neutral
   branch/critical identities without the target words. Measure residuals and
   uncertainty for both nominated orbits. A scalar projection may be monotone,
   multivalued, or insufficiently supported; each is reportable, not a reason
   to move boundaries. Do not require z to have critical points merely because
   it did at the distant control, and do not choose another coordinate after
   seeing which one reproduces the source word.
5. **Only then test an explicit alphabet transport and a connection.** Freeze
   the transport rule, comparison conventions, uncertainty exclusions and a
   bounded continuation path before generating the relevant word/arrow outcome.
   Counts of six versus eight returns prohibit simply relabeling the scout's
   eight entries into a six-letter source word. A successful node test is not
   yet a successful `p -> p+1` connection.

## Before target execution

The above is a worklist, **not an executable frozen protocol**. Next deliverables
are a machine manifest, runtime, synthetic/known-control failure tests, full
provenance checks, stopping rules, and an adjudicated design review consistent
with the research-integrity playbook. Numerical tolerances and sample support
must be fixed there; no undisclosed engineering pilot on these nominations.
Any bounded feasibility work must be explicitly labeled exploratory. A
confirmatory stage requires its own reviewed, pushed pre-outcome freeze; it
cannot inherit confirmatory status from EXP-479's exploratory nomination.

No new paid worker is needed to prepare this design. The outstanding ambiguous
Runpod transaction remains separately guarded, and no duplicate paid create
is authorized while it is unresolved. No manuscript PDF release accompanies
this design-stage update.

## Draft executable: event feasibility only

`scripts/check_historical_event_transport.py` implements the first worklist
item; `experiments/manifests/EXP-480-event-transport.json` records its proposed
numerical choices. The manifest is explicitly `draft-awaiting-review` with
`execution_authorized=false`. Preflight reads only existing hash-bound inputs.
The real execute CLI refuses the draft before opening target data or calling
a solver. It requires an approved adjudication bound to the exact design,
raw review receipt and runtime/dependency files; a clean pushed source is
also required before execution and checked again before the final receipt.

The proposed profiles are DOP853 and Radau, each at `(rtol,atol,max_step)`
`(1e-10,1e-12,0.02)` and `(1e-12,1e-14,0.01)`. Each starts from the same
previously corrected candidate seed and independently repeats the repository
shooting correction. It then integrates one trajectory for 2.5 proposed
periods and records both sections' unoriented plane roots and normal-velocity
extrema. Oriented/gated acceptance is applied only after all these event
records are retained. Integration step times and states are saved too.

The two fixed, half-open observation windows are `[0.25T,1.25T)` and
`[1.25T,2.25T)`. No window or cyclic rotation is searched to obtain agreement.
The expected counts remain the already-known six historical and eight Barrio
returns. Every window must have separated events, adequate crossing angle,
and a boundary margin. Repeated windows and all four numerical profiles must
agree in chronological event states and phases. Plane extrema near zero are
flagged as unresolved instead of being discarded. These diagnostics do not
prove that all between-step roots are found or certify a primitive flow period.

Proposed gates (all subject to pre-target design review) are:

- closure `<=1e-9`, phase residual `<=1e-10`, scaled seed correction `<=1e-3`,
  and relative seed-period change `<=1e-5`;
- state scales `[15,15,0.01]`; repeated/cross-profile scaled event-state error
  `<=1e-6`, event-phase error `<=1e-7`, and relative period disagreement `<=1e-7`;
- normalized crossing angle `>=1e-6`, distinct-event scaled separation
  `>=1e-5`, fixed-window boundary margin `>=1e-7` periods, and relevant
  normalized extremum-to-plane distance `>=1e-8`;
- 1,800 seconds cooperative wall budget, checked at profile boundaries and
  after final audits; this is not a hard per-solver timeout. No automatic retry.

Ordinary profile failures are retained while other predeclared profiles are
attempted; an interruption terminates the run with a partial receipt. Raw
arrays, corrections, per-profile diagnostics and file descriptors are saved
before final comparison. A changed raw file or source invalidates the final
pass without deleting its evidence. No partition fitting or word encoding is
called by this runner, and it assigns no historical symbols.

The tests use an analytic circular oscillator on synthetic sections and forced
failures, not either nominated Rössler trajectory. They exercise both real
DOP853 and Radau event integration, orientation/gate filtering, raw retention,
serialization, window/near-extremum rejection, ordering, empty-design rejection,
interruptions, final source failure, and review/runtime binding. Passing these
controls is implementation evidence only; target execution remains locked.
