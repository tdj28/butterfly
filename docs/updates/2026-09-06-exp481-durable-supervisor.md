# EXP-481: interrupted workers preserve evidence without claiming completion

Durable adaptive recording and the local-stage supervisor now pass their
synthetic controls. Accepted events and capture labels on **both** sections
survive forced shutdown. The interrupted runs correctly remain incomplete.
No new Rössler trajectory or Jones symbolic claim was produced.

## What is implemented

`paired_adaptive_journal.py` saves bounded full-prefix snapshots with exclusive,
fsynced NPZ files followed by hash-chained JSON commits. An offline audit
checks fixed seed identity, configuration, event-step/time alignment, immutable
prior traces/events, capture provenance and final-result concordance. Object
arrays, changed raw bytes, orphan data, substituted bindings and invalid
completion claims are rejected. No overwrite, repair, retry or resume is added.
A missing terminal receipt remains incomplete even if a saved state reached
the entire requested horizon. Malformed partial JSON may require manual
inspection; it is never repaired or silently promoted by the audit.

`paired_supervisor.py` starts only an explicit local argv and environment,
never a shell. It samples the owned process group's RSS and the evidence
directory's bytes, logs operational metrics and stops on resource thresholds.
Its session leader remains unreaped until cleanup, preventing reuse of the
numeric group ID while owned children are terminated. Tests verify a leftover
same-session child is cleaned up and a separate unrelated session is untouched.

These are **sampled operational thresholds, not hard kernel quotas**.
Memory/disk may overshoot between samples, and queries/termination take time.
Bounded per-batch and per-snapshot allocations also remain necessary. The
supervisor is for trusted research code, not hostile processes escaping their
session. Missing cleanup verification cannot be treated as success.

The standard-library-only `_process_guard.py` can be loaded before importing
the scientific package. A worker installs it on its supervisor-owned liveness
pipe and sets a local deadline. If the supervisor is killed or the deadline
expires, the worker terminates its own session. Generic argv supervision does
not prove this hook was installed; the real production consumer must attest it
before target access. That complete consumer/startup contract is still pending.

## Observed controls

The isolated synthetic CLI uses `python -I -B`, loads the guard before NumPy or
`butterfly`, and invokes the real new journal and supervisor components on an
analytic circle. It does not load any research candidate file.

| Case | Durable evidence | Correct completion status |
|---|---|---|
| DOP853 completion | Full time-7 trace, accepted events and both capture labels | Completed |
| Radau completion | Full time-7 trace, accepted events and both capture labels | Completed |
| Worker stopped by supervisor's wall limit | Prefix through time 4.98819…, both accepted events and capture labels | Incomplete |
| Supervisor forcibly killed | Same durable prefix; worker stops on pipe loss; no invented supervisor terminal | Incomplete |

All four controls pass and every worker stops. The first `synthetic-runtime-01`
also passed but paused before any section crossing. It is preserved. The second
control deliberately waits until the first 500-step snapshot, so the process-loss
test exercises accepted-event and capture-label persistence, not only a state
trace. This is stronger synthetic coverage, not tuning on target outcomes.

The [source-bound public summary](../experiments/receipts/EXP-481-synthetic-runtime.json)
links the local run `artifacts/EXP-481/synthetic-runtime-02`: 54 files totaling
145,643 bytes excluding its inventory receipt. Raw files remain local; hashes
alone are not a public data release. Reproduce with a fresh output directory:

```sh
PYTHONPATH=.:python .venv/bin/python scripts/qualify_paired_runtime.py \
  --output-dir artifacts/EXP-481/synthetic-runtime-NEW
```

This command intentionally terminates only its own synthetic processes and
requires host access to read process-group/RSS metadata. It makes no provider
calls. The full local suite, run with that host access, passes **1,494 tests**,
with one older Linux-only test skipped on macOS. There are **25 new tests** for
durability, exact terminal concordance, real SIGKILL, wall/RSS/disk stops,
parent-loss/deadline guards, symlink rejection and owned-only cleanup. Restricted
hosts skip live process tests if process inventory is unavailable; that skip
must not be described as live qualification. CI is required before merge.

## Remaining production work

Wire these components into the real source/input/review-bound production CLI,
with the complete fixed trial set and both-case aggregation. The current
synthetic CLI qualifies component wiring, not a sealed production deployment.
Build the isolated import closure, canonical environment constructor and genuine
startup attestation before the compact review. One observed detail must be
handled explicitly: this Mac's scientific worker adds `LC_CTYPE` and
`__CF_USER_TEXT_ENCODING` to the requested environment. The control records
those keys; it does not yet authenticate their complete values. Do not copy the
requested environment and call that proof of the realized environment.

Then run the compact design review, adjudicate findings, push the exact
executable freeze and perform the declared target experiment. The numeric
proposal remains unreviewed and execution-disabled. No routine permission
request is needed, but the research-integrity playbook still requires the
reviewed freeze before target outcomes. Its influence here is concrete:
write-once evidence, honest incomplete statuses, raw/terminal concordance and
explicit operational—not absolute—resource guarantees.

No paid model review, worker rental or remote upload was used. The separate
legacy stationary-inflection historical-impact audit remains required before
a new manuscript release. These software controls do not clear earlier claims.
