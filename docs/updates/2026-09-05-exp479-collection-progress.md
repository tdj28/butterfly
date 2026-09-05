# EXP-479 collection progress

## September 5 heartbeat (18:41 UTC)

The local CPU service is running from the unchanged frozen execution checkout.
Its launchd record reports one launch and no exit. No restart or numerical
amendment has occurred.

At this inspection:

- 48 of 551 candidates have completed both step-size profiles.
- 97 profiles have durable checkpoints, including the first profile of the
  next candidate.
- Every completed profile passes the frozen raw-data validity checks.
- All 97 raw-file SHA-256 values and byte counts match their checkpoint
  metadata; together those raw files occupy 197,737,057 bytes.
- No terminal collection receipt exists yet. Available local disk space is
  approximately 47 GiB.

These are operational checks, not a center-nomination or symbolic-word result.
No partition fitting, candidate ranking, or word comparison was performed.
Raw checkpoints remain under `artifacts/EXP-479/collection-30f6c5b`; the
execution source and numerical design remain those documented in
[EXP-479](../experiments/EXP-479-cpu-symbolic-center-pilot.md).

The ambiguous Runpod transaction still has no assigned ID and no exact-name
match in the current provider inventory. Its reconciliation watchdog is live.
This does not prove that the earlier HTTP 500 definitively rejected creation.
No new rental or unrelated-resource mutation was performed.

The completed, target-free CPU benchmark was also copied to the authorized
`prax` server in a fresh private directory named
`exp479-control-20260905-30f6c5b`. Both raw profile hashes and the receipt hash
match the local originals. This backup covers the benchmark only, not the
ongoing target collection; local originals are retained.
