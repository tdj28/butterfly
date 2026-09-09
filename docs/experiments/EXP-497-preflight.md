# EXP-497 pre-outcome validation

2026-09-09. Same-agent local audit, no paid review. The full EXP-496 endpoint
experiment is merged into main as `5d28941`; its raw archive publication is
separately blocked pending payload-specific approval and is not being bypassed.
All inputs required for local localization are already present. No EXP-497
target attempt has been consumed at this checkpoint.

## Design and tested boundaries

The complete two-case/three-level ledger retains the second case as ineligible;
it does not discard its failed depth-eight endpoint representations. Only the
first case qualifies for interior refinement. Every eligible level uses the
same original periodic phase seed, a strictly interior false-position proposal,
both periodic solvers and all four fold representations. Primitive six/eight
counts, paired observations and full-state fixed-event proximity are required.
Unresolved signs, a failed cycle or fold, or three unsuccessful points stop
the path. No alternative index, preimage, parameter or seed is substituted.

Seventeen focused tests pass, including complete eligibility, sign failures,
section transport, deterministic seed interpolation, unchanged phase reference,
all-variant scalar contact replay, blocked levels, the three-point limit,
input tampering, wrong raw anchors, and actual periodic-circle control replay.

Twelve actual fold controls and four actual periodic-circle controls were
generated before targets. All production decisions pass. The separate corrected
auditor replays all sixteen controls without new IVPs. The receipt is
`artifacts/EXP-497/preflight-controls-01/preflight.json`, SHA-256
`0f2cf7423e2d972a272fb2c5761df749c956234e0a0ffaeb8cbf40d12effcaa4`.
The frozen runtime will repeat the controls and audit the periodic controls
before creating the exclusive target witness.

## Retained preflight errors and fixes

1. The first full-suite launch overlapped the local checkout transition to the
   newly merged main. During that transition an EXP-496 import was temporarily
   absent, causing collection failure. No target ran. The transition completed;
   subsequent tests were run without concurrent checkout mutation. The failed
   collection receipt remains `artifacts/EXP-497/preflight-tests-01.xml`.
2. The first new circle-control auditor incorrectly reconstructed the metric
   from ordinary solver event roots rather than the production definition's
   extrema-bracketed dense-interpolant roots. This changed a near-zero diagnostic
   from about 1.105e-13 to 4.129e-16, just outside the existing absolute replay
   tolerance. The auditor now reconstructs the defined roots from saved dense
   coefficients and extrema. No accuracy threshold was loosened and no control
   data was regenerated to obtain agreement. The earlier records remain beside
   `replay-correction-01.json`; the new live-circle regression also passes.

The subsequent full suite passed 2193 tests with one existing Linux-only skip
in 138.34 seconds (`preflight-tests-02.xml`). A final full-suite run after the
replay fix and added regression passed **2194 tests with one existing Linux-only
skip**, in 139.58 seconds (`preflight-tests-03.xml`). No target has run.
Executed numerical source and input hashes are next frozen in Git and checked
against the live pushed reference before the consumed attempt is created.
