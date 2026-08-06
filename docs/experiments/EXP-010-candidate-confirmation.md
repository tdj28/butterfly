# EXP-010 — Candidate confirmation with basin probes

Status: completed finite-time confirmation; focused replication pending
Manifest: `experiments/manifests/EXP-010-candidate-confirmation.json`
Claim target: confirmation stage for P0-005 and P0-009

## Purpose

Confirm or reject the frozen EXP-009 lowest-1%-plus-neighbors set using longer
crossing records, full Lyapunov spectra, uncertainty-aware classification, and
two initial conditions per parameter point.

## Frozen selection

The manifest binds the exact EXP-009 aggregate result hash, selects the lowest
1% of finite normalized near-recurrence scores, and adds every in-grid neighbor
within Chebyshev radius one. This deterministically produces 17 core points and
139 total targets. Selection is recomputed and verified at runtime; the cases
are not chosen manually after inspecting their confirmation behavior.

## Method

- initial states `(0,4,0)` and `(1,1,1)`;
- 800-unit crossing transient and up to 128 interpolated crossings;
- minimal periods through 24 with six required repeats;
- 400-unit Lyapunov transient and 800-unit full spectrum;
- six uncertainty blocks; and
- aggregation across initial conditions with explicit multistability.

## Command

```sh
.venv/bin/python scripts/confirm_candidates.py \
  --manifest experiments/manifests/EXP-010-candidate-confirmation.json \
  --source-result artifacts/EXP-009/aggregate/result.json \
  --output-root artifacts/EXP-010 \
  --tile-count 32 \
  --workers 4 \
  --resume
```

## Acceptance criterion

Every selected point must produce a retained result for both initial conditions
or an explicit failure. Periodic recurrence conflicting with positive Lyapunov
evidence remains unresolved. Distinct resolved attractor signatures are labeled
multistable. The receipt must bind the source aggregate, selection, manifest,
source commit, tile outputs, and confirmation aggregate.

No candidate is promoted solely because it ranked highly in EXP-009.

## Result

The clean run from commit `672098655e3b9d7b4c686f8a8608a6265850d518`
completed 139 targets, two initial conditions per target, in 370.4 seconds of
wall time using four workers. The summed tile time was 1,456.1 seconds.

| Target classification | Count |
| --- | ---: |
| chaotic for both basin probes | 135 |
| multistable candidate | 2 |
| unresolved | 2 |
| numerical failure | 0 |

Across the 278 initial-condition runs there were 273 chaotic, two periodic, and
three unresolved classifications. Every run produced all 128 requested
crossings. The maximum absolute Lyapunov trace-identity error was `1.74e-9`.

## Multistability candidates

At `(a,c)=(0.17675,10.42)`, initial state `(0,4,0)` was chaotic, while
`(1,1,1)` converged to period 8 with recurrence error `9.90e-7` and spectrum
`(0.000292,-0.005752,-10.154866)`.

At `(a,c)=(0.18475,10.35)`, initial state `(0,4,0)` was chaotic, while
`(1,1,1)` converged to period 6 with recurrence error `4.07e-8` and spectrum
`(-0.002592,-0.007540,-10.043888)`.

These are reproducible finite-time multistability candidates, not yet completed
periodic-orbit continuations. The next experiment must extend horizons, sample
additional initial conditions, recover the exact periodic orbits, and compute
Floquet multipliers.

Successor correction: EXP-012 shows that both initial conditions eventually
converge to the same period-8 or period-6 attractor. The finite-time
`multistable` labels here are therefore rejected as persistent multistability
and reinterpreted as long transient capture.

The two unresolved points were `(0.17775,10.24)` and `(0.1845,10.4)`; the latter
retained a period-12 near-recurrence for `(1,1,1)` but did not pass the declared
threshold.

Aggregate result SHA-256:
`aa1b9557c16f9a763c59040065bb6668430c072e8ca8443f486c7f76e1fd2804`.
The checked-in receipt is
[`receipts/EXP-010.json`](receipts/EXP-010.json).
