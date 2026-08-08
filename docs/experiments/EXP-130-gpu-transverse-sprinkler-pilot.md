# EXP-130 — GPU transverse saddle-boundary discovery pilot

Status: failed the prospective scientific-resolution gate; execution complete

## Question

Does the qualified finite-time GPU sprinkler recover ordered two-to-three
saddle-topology brackets on the new `c=19.8` and `c=19.9` slices at `b=0.2`?

This leaves pure one-dimensional bisection at `c=20`. The experiment is a
discovery filter for expensive PIM validation, not a PIM substitute and not a
claim that a continuous topology-bifurcation curve already exists.

## Frozen design

Four `c=20` controls bind the calculation to the published two-/three-branch
cases and the local EXP-129 finite bracket. Twelve untouched targets cover
`a=0.145,...,0.150` at each new `c` value. The existing DOP853 reference first
has to recover a stable fundamental period-4 attractor at every resolved case.

Each case receives two independently scrambled `2^17` Sobol ensembles. All
four controls and the `a=0.148` point on each new slice also receive a `2^16`,
half-step repeat. The Float64 RK4 sprinkler conditions survivors through time
420 and measures return pairs over `[300,360]`. The four bounded Newton updates
localize the Poincare crossing inside an RK4 step on a cubic-Hermite
interpolant; they do not advance the ODE.

A run is resolved only when:

- at least 100 trajectories survive and both coordinates supply 1000 pairs;
- no integration fails and no retained trajectory saturates the crossing
  buffer;
- all 15 branch-oracle variants agree with normalized critical-location span
  at most `0.03`;
- all 15 lower-support slopes have a common sign and minimum magnitude `0.1`;
  and
- the negative/two and positive/three prediction agrees with the critical-
  point count in both `y` and `z`.

All applicable runs must agree to label a parameter point. Unresolved target
points remain unresolved. A slice passes only if its resolved labels never
reverse from three back to two and contain a finite two-to-three bracket. All
four controls must pass. A successful slice bracket selects held-out PIM
targets; it is not itself a saddle-defined continuation.

Immutable manifest:
`experiments/manifests/EXP-130-gpu-transverse-sprinkler-pilot.json`.

## Cost and teardown gate

The prelaunch 2026-08-07 account list is empty. The current catalog advertises
an RTX A5000 from `$0.16/hour`; secure-cloud returned pricing is authoritative
and may differ. Prefer a secure A5000, with A40 fallback, but automatically
reject any returned offer above `$0.40/hour`. The 38 runs contain an estimated
`2.09190912e11` state steps; the already qualified A5000 warm rate is
`5.9765e8` state steps/second. Provisioning, two kernel compilations, DOP853
cycle construction, bootstrap analysis, retrieval, and teardown give a
25-minute base and 45-minute slow estimate. Maximum wall time is one hour and
hard spend is `$0.40`. Fifteen minutes without progress triggers teardown.

Only the owner-authorized tracked-file archive of the exact frozen commit may
be uploaded. The raw receipt and remote hashes must be retrieved and verified
before the task-owned pod is terminated; the account list must then be empty.

## Frozen execution command

```bash
PYTHONPATH=python python scripts/gpu_sprinkler_boundary_pilot.py \
  --manifest experiments/manifests/EXP-130-gpu-transverse-sprinkler-pilot.json \
  --output artifacts/EXP-130/receipt.json \
  --source-commit SOURCE_COMMIT
```

The run must use the clean pushed preregistration commit. Result interpretation
and any PIM target selection are post-result changes.

## Result

The frozen workload completed on a secure RTX A5000 from source commit
`2cbe797` in `1075.37 s`. The returned price was `$0.27/hour`; complete
provisioning-to-teardown spend is conservatively below `$0.10`. The 465,456-
byte remote and local receipts match SHA-256
`e291d0656c7a66974cfd462405655e4904159275a9e65de7a9196933e58f27d2`.
The pod was terminated and the account list verified empty.

The published controls pass in all six base/half-step profiles. The two local
PIM-qualified controls do not: all six profiles remain unresolved because the
15 branch variants disagree and the slope variants cross zero or approach it.
This occurs despite zero integration failures, zero buffer saturation, at
least 121 final survivors and 1002 pairs, and warm throughput up to `6.221e8`
state steps/second. It is a scientific resolution failure rather than a
compute failure.

Neither transverse slice satisfies the preregistered bracket gate. At
`c=19.9`, only `a=0.150` fully resolves, as three. At `c=19.8`, the high-
accuracy attractor at `a=0.149` is not classified as stable period 4 and is
skipped. The non-claim-bearing exploratory signatures prospectively select
PIM endpoint pairs `(0.145,0.148)` at `c=19.8` and `(0.145,0.150)` at
`c=19.9`.

The result rejects brute finite-survivor continuation near the boundary. It
does not reject the Jones/Barrio topology transition; it requires the next
transverse test to construct the saddle with adaptive PIM.

Tracked compact receipt: `docs/experiments/receipts/EXP-130.json`.
