# EXP-479: completed CPU scout, two exploratory nominations

The full frozen collection and analysis completed successfully. This is useful
progress toward a flow-level symbolic test, not verification of Jones's chains.

## Complete result, including exclusions

All 551 candidates completed both integration profiles. The complete raw audit
passed 1,102 profiles with zero recorded integration failures. The analysis
completed all 551 candidates in 1,419.329 seconds, within its unchanged
7,200-second limit. All 1,653 saved fit/combined files match their recorded
hashes and sizes. Both completed local services exited normally and were
verified unloaded; no restart or numerical retuning occurred.

Of the 551 candidates, **384 were eligible and 167 were ineligible** under the
frozen reconstruction rules. Two eligible candidates passed the direct
nomination threshold; 382 eligible candidates did not. No corner-range
nomination cells were returned. The coverage requirement of 250 eligible
candidates passed.

| Candidate | a | b | c | Maximum normalized residual | Maximum critical-location span |
|---|---:|---:|---:|---:|---:|
| local-a025-c083 | 0.21575 | 0.2 | 7.212 | 0.01845414 | 0.00625577 |
| local-a027-c083 | 0.21577 | 0.2 | 7.212 | 0.01997409 | 0.00905230 |

Each nominated candidate retained a common assignment of orbit indices
`[7, 5]` across 12 reconstructions (two time steps, two nested supports,
three smoothings). These are indices in the scout's eight-phase cycle,
**not historical Jones symbols**. The direct residual threshold was 0.02;
the second nomination lies close to that cutoff. Neither residual is zero,
and neither establishes simultaneous critical membership or a center root.
These nearby parameter points are not evidence for two distinct centers.

## What this means for Jones

We now have measured, reproducible locations at which to attempt the next
test. This scout neither debunks nor confirms the historical symbolic claim.
It uses the Barrio positive-x section and scalar z projection, so its success
does not establish the historical-section partition, a single-valued quotient,
the proposed alphabet mapping, or any arrow in Jones's chain diagram.

The next scientific step is an explicitly frozen successor that retains both
nominations: correct and continue the flow cycles, reconstruct the historical
section independently of desired words, assess scalar-map ambiguity, and test
critical membership with uncertainty. Only then compare flow itineraries with
the source transcription. If a partition or center remains unresolved, report
that failure; do not tune the partition to obtain the expected chain.

## Evidence and backup

- Frozen numerical source: `30f6c5b0aeaa4c9d8548bb2b0a60f802ebb096e2`.
- Collection receipt SHA-256:
  `845e3cd783a8aee9a49a7db9b377515c45fe6bb6974ad9f0a857132e0b0b86da`.
- Analysis receipt SHA-256:
  `4147ff20adefb6adf536137cb0a92809446ce66d40c20b6c00f909fa6235755f`.
- Full CPU bundle: 4,970 evidence assets, including every raw/checkpoint/fit
  file, both terminal receipts, audit, qualification, original CPU control,
  candidates and credential-scanned frozen source archive. No private provider
  lifecycle or credentials are included.
- Bundle size: 2,186,342,400 bytes; SHA-256:
  `edee329dd0d56987d1874fdd1d96836e49c5c1bd1b83fc49f21ef3d22619fdc0`.

`scripts/archive_exp479_cpu.py` prepares and stream-verifies this tar locally.
Its separate upload mode requires the exact preparation receipt and a fresh
task-owned prax child, strict known-host SSH, no forwarding, a two-hour transfer
timeout, and remote hash/size/private-permission verification. It retains the
tar remotely without extracting or executing its contents. Failures preserve
local originals and remote partials; no automatic retry is permitted. The
CPU-specific 7,000-file bound accommodates serial batches and does not alter
the GPU archive protocol's limits. Remote upload is pending at this checkpoint.

A read-only preflight found that a background environment without the local
SSH agent could not authenticate. Passing only its local socket fixed that
check; agent forwarding stays explicitly disabled. The launcher now rehearses
authentication with its exact isolated environment before creating a service.
No transfer or remote child was created by the failed authentication check.

## Upload authorization boundary

The final wrapper passed 1,311 local tests (one Linux-only skip) and both CI
Python versions, and was merged into main. The subsequent launch request was
rejected by the execution approval system **before the command ran**. It
requires explicit authorization for this complete source/research/analysis
payload to prax; general remote-storage authorization was not accepted for
this bundle. No upload service or remote destination was created by that
request. Do not retry via another transport or indirect execution.

The pending destination is
`ubuntu@prax:/home/ubuntu/butterfly-research/exp479-complete-20260906-30f6c5b/evidence.tar`.
The exact payload is the 2,186,342,400-byte bundle with SHA-256
`edee329dd0d56987d1874fdd1d96836e49c5c1bd1b83fc49f21ef3d22619fdc0`.
It contains frozen source and unpublished research evidence, but no credentials
or private provider lifecycle records. Originals and the verified local bundle
remain intact. Obtain explicit owner authorization before this upload.

## Owner approval and active upload

The owner explicitly approved the complete payload/destination after the
boundary above and requested continued work. The same verified upload was
then launched successfully, with no payload or destination change.
Service: `gui/501/io.butterfly.exp479.archive.91d43fc9eaea4952b01ee571f41916a6`;
initial PID 94605, one launch, no exit at inspection. Its code SHA-256 is
`946cc7b94c767de97488b68f09f9007f3a58d3fdc0e3dda95c341e69ec6b7421`.
Launch/log records are in `artifacts/EXP-479/archive-service-30f6c5b`.

The remote partial reached 466,099,200 bytes with mode 0600 at the first
progress check. This is transfer progress, **not a verified remote archive**.
Completion requires the full 2,186,342,400 bytes, matching SHA-256, the
terminal upload receipt, and verified process/service exit. Do not launch a
duplicate transfer. Scheduled research follow-ups have resumed, and the
separate Runpod watchdog remains live.

The next design must preserve a distinction already present in the input
evidence: these flow cycles have six historical-section crossings and eight
Barrio-section crossings. EXP-185's operational alphabet qualification at
`(0.2,0.2,20)` does not transport itself to these points. The next test must
track the return events and partition geometry explicitly, without matching
the known words to choose labels. EXP-190 also documented a two-branch
historical x map in a different searched neighborhood; retain that negative
result rather than assuming every section must exhibit two critical points.

The ambiguous Runpod create still has no assigned ID or matching task name;
its watchdog remains alive. This is not a verified rejection. No new paid
compute or unrelated-resource mutation occurred.
