# EXP-477 — Raw-retaining, word-independent center nomination pilot

Status: prepared; target trajectories not yet collected. The original local
storage block is retained in the
[initial update](../updates/2026-09-04-independent-symbolic-verification.md).
The owner has now authorized SSH evidence storage on `prax`; its implementation
and current execution status are in the
[remote-storage update](../updates/2026-09-05-prax-evidence-storage.md).
The known-anchor CPU deployment reference has completed; GPU parity and
target collection have not run.

## Why this is needed

The source redraw is historical evidence, not an independent verification.
EXP-186 did not recover the reported word at an approximate landmark, but it
also failed partition parity. EXP-204 prepared an independent center search
without executing it. This new experiment retains that search's numerical
design while adding source binding, raw-data retention, conservative event
validity gates, and separate GPU collection/local CPU analysis. It does not
retroactively change EXP-204 or claim that the old experiment ran.

## Scope and frozen numerical design

The [new manifest](../../experiments/manifests/EXP-477-symbolic-center-pilot.json)
hash-binds the complete EXP-204 design, the complete 551-candidate input, and
its two selection/evidence files. Candidate order is preserved and collection
uses deterministic batches of eight. All candidates receive both Float64 RK4
steps, `0.01` and `0.005`, the same 8,192 initial conditions, and horizon 200.
Analysis retains both nested supports and all three smoothing variants,
giving twelve reconstructions per candidate; numerical acceptance thresholds
are unchanged from the parent. No target words enter nomination.

This is a **Barrio positive-x section, z-coordinate, eight-phase scout**.
Historical period-six labeling refers to a different section. A scout
nomination is not a Jones six-symbol word, and an alphabet control at
`(a,b,c)=(0.2,0.2,20)` cannot be transported here without new evidence.

## New collection gates

- Preserve each final survivor's seed ID, event states and event times in
  non-pickle NPZ files, with candidate/profile metadata and hashes, before
  fitting anything. Retain survivor and failure counts for the whole ensemble.
- Reject a batch if any survivor's recording reaches the kernel's 32-event
  capacity. The old kernel saturates its counter, so equality is treated as
  possible truncation rather than assumed safe.
- Reject recorded survivor events with nonfinite states or normalized section
  transversality below `1e-6`, where the diagnostic is
  `abs(n dot f)/(norm(n)*norm(f))`. This is a conservative numerical admission
  threshold, not a theorem or a bound on events the kernel did not record.
  Report the actual minimum. It says nothing about captured trajectories,
  missing/tangent returns, or archive-wide section transversality.
- Stop on the first invalid batch or at the next batch boundary after 3,600
  seconds. Preserve partial/failure receipts. No silent retries, candidate
  dropping, or horizon/threshold adjustment within this experiment.

## Interpretation and successor gates

Even with all numerical gates satisfied, a point with small two-coordinate
residuals is only a nomination. A four-corner cell whose two residuals each
straddle zero separately is also only a nomination: it is **not** a proof of a
simultaneous root, a Poincaré–Miranda face-sign condition, or nonzero degree.
The historical label `signed_bracket` in reused analysis retains only this
weaker meaning. If fewer than 250 candidates remain eligible, coverage fails;
neither an empty nor an incomplete search refutes Jones.

After a nomination, freeze a separate experiment to:

1. correct and verify a primitive periodic flow orbit using independent
   adaptive solvers and a transverse historical section;
2. reconstruct the partition from fresh, dense transient/saddle data with
   that candidate cycle withheld;
3. establish branch count, critical uncertainty and zero-slope membership
   without adjusting the partition to reproduce a desired word;
4. calibrate and transport the local alphabet, encode in time order, and
   only then compare the full itinerary; and
5. continue verified centers/curves before claiming any connecting arrow.

Across a nominated cell, establish continuous correspondence of the whole
periodic orbit's phases; matching integer phase indices alone is insufficient.
Check critical-location stability on a common physical coordinate scale as
well as support-specific normalized domains, which can conceal physical
drift. These are successor verification gates, not retroactive changes to
the historical scout's numerical acceptance rules.

## Compute and publication boundary

The user explicitly permits Runpod for this task. Collection is conditional
on synthetic local tests, a clean public source/manifest freeze, and a cheap
GPU qualification/timing gate. CPU spline/bootstrap analysis runs locally
**after retrieval and verified GPU teardown**. No cloud launch is needed for
the separate exact quadratic control, EXP-478.

The deployment control is implemented in
[`qualify_symbolic_gpu_records.py`](../../scripts/qualify_symbolic_gpu_records.py).
It reuses the known EXP-196 anchor, not any of the 551 target candidates.
Before launch, the local CPU constructs a fresh corrected anchor and records
a fixed 8-by-8 ensemble at both steps with the parent's horizon/capture/window
settings. On the worker, require identical survivor IDs, survivor counts and
event counts, zero integration failures, unsaturated records, and finite
event-state/time differences no larger than `1e-6`. This tests deployment
parity, not generating-partition validity or long-horizon chaotic identity.
Then time integration, host retrieval and raw preservation for two eight-copy,
8,192-seed, `dt=0.005` anchor batches. Use the slower
time times `69 * 1.5 * 2` (full batches, two-profile work, safety factor) as a
projection; proceed only if it is at most 2,400 seconds. This projection is
not a guarantee, and the independent resource deadline remains mandatory.
No spline/bootstrap fitting occurs on the GPU host. Local analysis has its
own 7,200-second cooperative limit; a timeout preserves an incomplete receipt.

Use at most one new task-owned secure on-demand GPU at a time, an actual
returned hourly rate no higher than USD 0.50, no network volume, and no more
than three hours of provisioned lifetime. Reserve USD 3 for the attempt,
including disk/setup/retrieval margin; this is a task stop budget, not a
provider-enforced billing cap. A durable local watchdog and verified teardown
are mandatory. If these controls or the timing gate cannot be established,
do not launch/scale and record the reason. The existing account's unrelated
resources must not be changed or counted as this experiment's spend.

The initial live catalog inspection is read-only; it is not a reservation or
a price guarantee. The lifecycle receipt must record the exact returned
offer, source/input hashes, hardware/software environment, elapsed lifetime,
cost estimate and its uncertainty, and final direct/provider-inventory absence.
Provider billing is authoritative. Credentials and private correspondence
remain local; transfer only the frozen tracked source and declared numerical
input to the single owned host. Retain raw files locally and document their
availability separately from any public compact result.

Runpod control fields and lifecycle semantics were checked against its
[create-pod API](https://docs.runpod.io/api-reference/pods/POST/pods) and
[pod-management documentation](https://docs.runpod.io/pods/manage-pods).

## Execution entry points

The [cloud runtime manifest](../../experiments/manifests/EXP-477-cloud-runtime.json)
pins one A40 image, Python minor version, CUDA/PyTorch overlay and stage
deadlines. The installed Python patch, GPU driver, and complete installed
package list are recorded. The extra CUDA overlay is not claimed to be
covered by the CPU environment lockfile.

From the clean, publicly pushed source commit, first create the small local
known-anchor control:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.qualify_symbolic_gpu_records \
  --mode cpu --source-commit FULL_FROZEN_COMMIT \
  --output artifacts/EXP-477/cpu-control.json
```

Then supply that receipt's SHA-256 and **new** ignored/private output and
state paths to the executor. Preparation performs no provider calls:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.execute_symbolic_center_cloud \
  --source-commit FULL_FROZEN_COMMIT \
  --cpu-control artifacts/EXP-477/cpu-control.json \
  --cpu-control-sha256 CPU_CONTROL_SHA256 \
  --state-dir artifacts/EXP-477/owned-worker-state \
  --output-dir artifacts/EXP-477/cloud-attempt --prepare-only
```

The placeholder commit and hash above must be replaced with verified values.
A live invocation replaces `--prepare-only` with the explicit `--execute`
opt-in and uses new paths, because evidence is never overwritten or silently
resumed. With neither flag the executor only prepares. It refuses to provision unless
the local destination has space for the maximum 8 GiB payload, its archive,
and reserve (about 16.5 GiB). This must be on the intended retrieval volume;
free space elsewhere is not sufficient. A separate durable local watchdog
must be confirmed alive before creation. It is not a provider-side lifetime
guarantee and cannot act while the Mac or its network is unavailable.

After complete hash-verified retrieval **and verified owned-worker absence**,
run `run_symbolic_center_pilot.py --mode analyze` locally with the same frozen
source, collection directory and collection-receipt SHA-256. The analysis
refuses incomplete collection and rechecks all raw hashes before fitting.

## Execution checkpoint

Frozen runtime: `bf6231ed489bf9c2ee5599fa0f9ee71191578e9f`, retained by tag
`exp-477-protocol`. The complete
[CPU control receipt](receipts/EXP-477-cpu-control.json) was generated from
that clean, publicly pushed commit and passed its local construction checks.
Its SHA-256 is
`6849f6a1cf53689e96cc70f0b436c2823e669df105e18b378281dad0ca777118`.
This is a reusable GPU comparison input, not a flow-center result. Subsequent
execution must use that frozen source (or prospectively declare a successor),
not substitute the later documentation-only merge commit for its source ID.

The preparation-only attempt stopped at the local disk gate before any
provider calls. No GPU qualification, target collection, spline analysis,
center nomination or chain verification has occurred in EXP-477.

## Remote evidence deployment amendment

The 2026-09-05 amendment adds `--ssh-storage-dir` to the cloud executor. An
explicit path must be one **new** child of
`/home/ubuntu/butterfly-research` on the authorized `ubuntu@prax` host.
Preparation may stage the small hash-bound storage helper and expected
evidence binding there; it creates no GPU worker. Only `--execute` provisions.
No numerical thresholds, candidates, seeds, integration settings or fitting
rules change. The original runtime tag and CPU control above remain historical;
the complete amended source gets its own public freeze and fresh CPU control.

Use the same cloud command with the additional argument:

```sh
--ssh-storage-dir /home/ubuntu/butterfly-research/NEW_UNIQUE_ATTEMPT
```

The bounded tar stream is relayed through the Mac's memory to `prax`. The
same full raw-evidence size allowance and hash/identity checks apply at the
destination. Original raw records stay there. Local metadata, controller,
watchdog, provider credentials and private keys never move to the server.
Both the authenticated watchdog and transfer path must pass a target-free
live control before paid collection. Failed stages must be quiescent before
their partial archive is packed.

After verified GPU termination, the new
[`analyze_symbolic_remote_collection.py`](../../scripts/analyze_symbolic_remote_collection.py)
driver calls the same analysis with a remote asset provider. It validates
the complete original inventory before the first fit and after the last,
checks each fetched file, and caches only one raw profile at a time. The
cache is capped, and compressed **and uncompressed** NPZ sizes are bounded
before allocation. No analysis runs on `prax`; only its standard-library
hashing/transfer helper executes there. The driver requires explicit hashes
for the storage binding, collection receipt, ownership and final lifecycle
receipts, and exact collection/analysis source-commit equality.

The [remote-storage update](../updates/2026-09-05-prax-evidence-storage.md)
will record the actual new freeze, commands, receipts and outcomes. Preparing
this deployment is not a symbolic verification result.
