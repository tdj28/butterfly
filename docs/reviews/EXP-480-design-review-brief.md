# EXP-480 decision-level design-review brief

Status: prepared for adversarial review; **no review has been obtained or
adjudicated, and execution is not authorized**. This is not a review receipt.

## Decision to review

Is the proposed event-transport feasibility check a useful, correctly bounded
next step toward independently testing Jones's symbolic chains, or would it
merely repeat already-established orbit facts without reducing uncertainty?
Identify necessary changes before execution, prioritizing scientific construct
and numerical failure modes over cosmetic suggestions.

The ultimate objective is historical-section partition/critical-membership/
alphabet/chain verification. This small step does **not** claim to accomplish
that objective. Reject any interpretation that turns a passing event check
into confirmation of a symbolic node or connecting arrow.

## Prior outcomes already known to the executor

The EXP-479 exploratory CPU scout ran all 551 candidates: 384 eligible, two
direct nominations (`a=0.21575` and `0.21577`, `b=0.2`, `c=7.212`), no
corner-range cells. Their maximum normalized critical-projection residuals
are approximately 0.01845 and 0.01997 against a 0.02 nomination threshold.
These are not root certificates or evidence for two distinct centers.

Their existing input records already contain corrected stable flow cycles,
six historical-section crossings and eight Barrio crossings. EXP-480 would
revalidate numerical event chronology, not discover those counts. A qualified
historical alphabet at the separate `(0.2,0.2,20)` control does not establish
transport to these points. Prior exact-landmark and historical-projection
failures remain part of the record. No new trajectory or fit at either
nomination has been generated in preparing this draft.

## Proposed design and safeguards

Retain both nominations, all four solver profiles and all failures. Recorrect
each same seed with the existing phase-conditioned shooting formulation using
DOP853 and Radau, each at base/refined tolerances and step caps. Integrate
both sections along each *same* corrected trajectory for 2.5 periods. Save
step states/times, all unoriented plane events, normal-velocity extrema and
the oriented/gated acceptance masks before making event comparisons.

Fixed half-open windows `[0.25T,1.25T)` and `[1.25T,2.25T)` must agree in
ordered event states/phases. No window or rotation search. Check correction,
closure, phase, event separation, transversality, boundary margin, relevant
near-plane extrema, solver/step agreement and finite raw data. The precise
proposed thresholds and profile options are in the machine design below.
No survivor selection, partition inference, critical lettering, word comparison
or parameter continuation is called. There is a cooperative 1,800-second
limit, not a hard per-integration timeout, and no automatic retry.

Synthetic controls use an analytic circular oscillator; both real solvers run
there. Other tests inject solver/source/raw-file failure and interruption,
verify full retained outputs, reject empty designs, and exercise the draft
execution lock. These controls are not target evidence.

## Questions for adjudication

1. Does common-trajectory event chronology supply a meaningful prerequisite
   for the next partition study, given the already-known unequal return counts?
2. Are fixed-window correspondence and distinct-event tests adequate for the
   limited feasibility claim? What degeneracies could make them misleading?
3. Are oriented events, extrema diagnostics and four profiles an appropriate
   numerical check of missed crossings? A rigorous all-root or primitive-period
   claim is expressly excluded. Is the remaining wording still too strong?
4. Are the proposed scaled tolerances justified and interpretable, particularly
   the small z scale? Should controls or error-normalization be changed before
   observing the target outputs?
5. Does the no-word, no-partition boundary prevent target-driven relabeling?
   What must the subsequent common-population historical survivor study fix
   to separate section geometry from capture-selection effects?

## Review packet and binding

Primary files:

- `docs/experiments/EXP-480-historical-section-successor-design.md`
- `experiments/manifests/EXP-480-event-transport.json`
- `scripts/check_historical_event_transport.py`
- `tests/test_historical_event_transport.py`

Canonical design SHA-256 (sorted compact JSON of the manifest's `design`):
`c7915accbf4dc63d5fba84434ad98aa95163a466d4119390aa21d350daca9fe4`.
Runtime SHA-256 at this checkpoint:
`9ddb1b3587ffb6a54c454cd0f7f67097410f45afb4575d287016b7292409c987`.
If design/runtime changes, regenerate bindings and adjudicate the changes
before any execution approval. A completed adjudication must retain the actual
raw review receipt and hashes for every `REVIEW_RUNTIME_PATHS` entry.

Only the compact decision packet and necessary source excerpts belong in a
future external review. Raw trajectories, the 2.19 GB evidence archive, keys
and private provider lifecycle records are not part of this packet. A review
based on this packet must not be described as an audit of omitted raw evidence.
