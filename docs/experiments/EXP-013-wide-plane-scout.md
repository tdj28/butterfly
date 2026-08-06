# EXP-013 — Wide-plane reconnaissance beyond `a = 0.22`

Status: completed reconnaissance; candidate qualification pending
Manifest: `experiments/manifests/EXP-013-wide-plane-scout.json`
Claim targets: CLM-001, CLM-009, CLM-010, and the new bounded-global-atlas
question

## Question

Does the recovered code's historical high-`a` domain contain stable periodic
windows that can seed a systematic explanation of shrimp and hub families
beyond the primary Jones hub?

The historical `Quickstart.txt` example scans `a in [0.25, 0.34]` and
`c in [5, 15]`. This experiment deliberately covers that rectangle and extends
its lower boundary to `a = 0.22`.

## Prospectively frozen method

- Rössler system with `b = 0.2`.
- Uniform discovery grid: `29 x 41`, or 1,189 points.
- Domain: `a in [0.22, 0.36]`, `c in [5, 15]`.
- Initial state: `(0, 4, 0)`.
- DOP853, Float64, `rtol=1e-9`, `atol=1e-11`, `max_step=0.1`.
- Transient 600 and observation horizon 800.
- Up to 128 oriented, interpolated legacy-section crossings.
- Fundamental recurrence periods through 32, requiring four repeats.
- Immutable hash-bound tiles with deterministic aggregation.

The verified aggregate will be summarized into same-period eight-connected grid
components and ranked nonperiodic near-recurrences. These are search seeds, not
claims that pixels establish connected shrimp geometry.

## Acceptance and interpretation gates

The reconnaissance succeeds operationally if all 1,189 points finish in a
verified aggregate with no missing or duplicate indices and a deterministic
summary is generated.

A detected periodic component is only a candidate family. Each candidate must
subsequently pass local adaptive refinement, multiple initial conditions,
transient checkpoints, periodic-orbit recovery, Floquet stability, and branch
continuation. An unresolved pixel is not called chaotic. Components touching a
search boundary force a domain-extension decision.

The experiment cannot establish completeness over the unbounded `(a,c)` plane.
It begins a bounded, progressively extensible atlas and provides data for a
quantitative stopping criterion based on boundary activity and discovery rate.

## Result

The clean run from commit `426f7986ff399229306549e8d45d54f25d333cfc`
completed all 1,189 points in 16 immutable tiles. The aggregate contains 82
periodic and 1,107 unresolved points, with no integration failures. The summed
tile time was 2,233.3 seconds; eight local workers completed the run in roughly
five minutes.

The deterministic summary found 52 coarse same-period components:

| Period | Components | Periodic pixels |
| ---: | ---: | ---: |
| 1 | 11 | 30 |
| 2 | 19 | 23 |
| 3 | 4 | 11 |
| 4 | 8 | 8 |
| 5 | 2 | 2 |
| 6 | 5 | 5 |
| 8 | 2 | 2 |
| 12 | 1 | 1 |

Eight components touch a boundary, so this rectangle is not a closed atlas.
The raster reveals a prominent diagonal low-period band from approximately
`(a,c)=(0.245,15)` toward `(0.295,5)` and separated islands through `a=0.36`.
These are candidate organizing families, not yet continued structures.

Aggregate result SHA-256:
`58aa45114962c285edff6deab08915f89f953b5b7437996b82bb9a7ad6e50e3d`.
The checked-in receipt is [`receipts/EXP-013.json`](receipts/EXP-013.json).
EXP-014 freezes 39 spatially diverse periodic and near-recurrence targets for
two-initial-condition and Lyapunov qualification.

## Cost gate

Local CPU execution is the first gate. Paid GPU work remains capped by the
owner's total authorization of USD 100. No production rental is justified until
the GPU implementation passes section-crossing and classification parity, not
only short-horizon endpoint parity.
