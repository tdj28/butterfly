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

The ambiguous Runpod create still has no assigned ID or matching task name;
its watchdog remains alive. This is not a verified rejection. No new paid
compute or unrelated-resource mutation occurred.
