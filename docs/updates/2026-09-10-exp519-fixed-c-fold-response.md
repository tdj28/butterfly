# EXP-519: testing whether the recovered fold can meet the orbit

## Current status

**Completed and raw-audited: all 513 integrations pass, and the single
prescribed correction meets full-state fold/orbit proximity in all sixteen
variants.** The earlier disk block cleared without an amendment. The original
reserve and scientific thresholds were unchanged. See the
[execution and result record](2026-09-10-exp519-execution.md).

EXP-518 is merged through PR84 after all four final-head
Python 3.12/3.13 push/PR checks passed. Main advanced to `1895bfd`; the successor
branch is `codex/exp519-fixed-c-fold-response`.

The next scientific test is not another figure of the same result: it computes
fresh a-derivatives for the recovered four/seven-return fold constructions,
recomputes the periodic orbit at four nearby parameter points, and permits one
bounded correction only after the fresh response qualifies. Both endpoints in
all three state coordinates must pass in every solver/construction/window
variant. The old x-only success remains an explicitly failed full-state
baseline. No paid Pro request, GPU rental or raw upload is involved.

## Local design audit before targets

This is a same-agent adversarial pass with separately coded scalar arithmetic,
not an independent team review.

| Objection | Resolution fixed before outcomes |
| --- | --- |
| Old h8 derivatives do not describe recovered h7 curves. | New h4/h7 family identities; four fresh points; no reused Jacobian. |
| Projected x can meet while z misses. | Six-component input/output residual and all-variant full-state radius; projection-only negative control. |
| Moving folds against a stale orbit can mimic contact. | New qualified periodic shooting and complete two-window observation at every point. |
| A multiple traversal can impersonate a primitive cycle. | Existing primitive geometry and six/eight event-count gates remain; retained analytic circle controls are replayed. |
| History/window changes can create a derivative by relabeling. | Fixed ordered sixteen-key matrix plus original/anchor index correspondence and complete fold prefixes. |
| A convenient stencil outcome can be cherry-picked. | All four stencil points run; only the prescribed single correction can supply the corrected endpoint. |
| A converged Newton equation can sit on a collapsed input. | Unchanged gain, projection, angle, curvature, region and complete-prefix gates. |
| A positive x derivative is assumed from old data. | Both common orientations are accepted; unresolved or inconsistent fresh slopes block correction. |
| A small x residual does not validate linear response. | Separate full-state prediction-error test; contact and prediction statuses reported separately. |
| Repeated recursive ancestry checks can dominate startup. | Hash-sensitive local input cache; actual isolated production startup is tested, not replaced by a fake receipt. |

The protocol is [EXP-519](../experiments/EXP-519-fixed-c-fold-response.md).
Implementation, tests, machine plan and raw auditor were sealed and pushed
before the one-shot target run. The result is recorded separately after the
full raw audit, not inferred from unit-test success. The following sections
preserve the pre-outcome sequence and its initially blocked status.

## Pre-outcome incident and repair

The first complete preflight (`artifacts/EXP-519/preflight-full-01.xml`)
finished with 37 passes and one failed source-identity check in 188.28 seconds.
The isolated child successfully validated the plan, but source/test edits made
while it ran meant its copied tree no longer matched the working tree. This is
an operational sequencing error, not a numerical failure. No target IVPs or
target attempt marker existed. The failed copied-source tree and test receipt
are retained. The final rehearsal must run without concurrent source changes;
the failed receipt is not used to authorize execution.

The local audit also added a sticky resource-abort guard before outcomes:
if a numerical producer catches a resource exception, the next budget check
still aborts the entire run rather than misclassifying the interruption as an
ordinary failed point. Synthetic IVP, clock and disk interruptions verify this
behavior without spending or generating a target outcome.

## Final preflight

With source held fixed, `preflight-final-02.xml` records **84 passed** in
188.63 seconds (EXP-519 plus EXP-518 transport and EXP-502 response tests).
The real isolated startup validates all 159 deployed files without ambient
raw artifacts or bytecode; its successful temporary public-file copy is
discarded only after hash comparison. `preflight-numerics-01.xml` records
**63 passed** in 3.74 seconds for periodic transport/minimal periods,
fold/cycle localization and bounded JSON/compressed products.

The machine plan binds 142 source paths and 24 input bindings (159 unique
deployed files). The fixed source is ready for the live public Git barrier and
one local execution. These are validation results, not target outcomes. All
control receipts, the failed first rehearsal, raw-upload restrictions and old
experiment failures remain preserved.

## Public freeze and operational block

Source `cdd08b37762e2c89bc368535331450c94cd33f53` was committed, public-scanned
(2,997 tracked files) and live-verified at
`refs/heads/codex/exp519-local-execution` before the launch commands.
Both launch commands exited at the initial fresh-output/disk-reserve gate,
before output creation or one-shot marker consumption. They generated zero
new target IVPs; neither is a scientific result. The numerical source,
machine plan, reference inputs and old experiment markers remain unchanged.

The first subsequent disk observation was 12,556,292 KiB available, below the
12,582,912 KiB startup requirement. Four task-created temporary EXP-517/518
source-copy trees were removed only after every file was SHA-256-identical
to its still-present repository counterpart: 143, 143, 151 and 151 files,
139,494,212 logical bytes altogether. These were recoverable public-file
duplicates, not raw evidence. Nonidentical rehearsal trees and the failed
EXP-519 rehearsal were preserved. The cleanup did not produce enough reported
free space, so the unchanged retry was also correctly refused. At 15:58 UTC,
12,432,404 KiB was reported available. This is an observation after the failed
launches, not an invented measurement from inside their exception handlers.

At that earlier checkpoint, I requested explicit approval to lower only the initial reserve
to 11.5 GiB, while preserving the 3 GiB output cap, 8 GiB continuing floor,
one-shot rule and every scientific threshold. **That amendment is not approved
or implemented at that checkpoint.** Subsequently the filesystem reported
enough free space, and the unchanged frozen design executed successfully.
No approval was inferred and the proposed amendment was never used.

## Why the full state matters for the next symbolic step

Rereading Jones's Figures 4--6 reinforces the distinction: C names the
critical point retained on the two-branch side, while D is the additional
critical point in the bimodal description. A section-grazing event cannot
simply be assigned D without establishing that return-map geometry.

There is also an exact algebraic reason not to confuse a projected encounter
with the fixed point with a homoclinic approach. Let the small equilibrium be
`(x*,y*,z*)`, and let the recovered section be `s=y-y*=0`.
The Rössler equations give `ds/dt=x+a*y`. At a section tangency,
`x=x*` and `y=y*`, but **z is unconstrained**. Writing `z=z*+delta`,
the full vector field at that point is

```text
(-delta, 0, (x*-c)*delta),     d²s/dt² = -delta.
```

For nonzero delta this is a regular flow point with quadratic section
tangency, directly above or below the equilibrium in the xy projection.
It is not the equilibrium. Consequently, apparent contact with the center
in an xy picture is not evidence of full-state equilibrium approach, much
less the required global stable/unstable connection. This is an algebraic
clarification of the existing vector field and section, not a new target
integration, a new claim about Jones's homoclinic orbit, or a substitute for
the missing C/D dictionary.
