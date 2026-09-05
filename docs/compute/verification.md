# External compute verification

| Change | Status | Evidence | Limit |
|---|---|---|---|
| RunPod finite hourly ceiling, invalid-price cleanup, and credential redaction (2026-09-04) | Unit-tested only | 33 mocked cases in `tests/test_runpodctl.py`; independent code review | No live API calls in this audit. Cleanup confirms only a successful deletion request, not a subsequent provider state. Hourly checks occur after provisioning and do not enforce cumulative spend. |
| EXP-477 read-only credential/catalog path (2026-09-04) | Verified live, read-only | Successful authenticated worker inventory and secure GPU catalog queries during protocol preparation | No create, SSH deployment, collection or teardown was tested by these queries. Unrelated running workers were not changed. Catalog prices are not reservations. |
| EXP-477 local CPU deployment reference and disk gate (2026-09-04) | Smoke-tested locally | [Full known-anchor receipt](../experiments/receipts/EXP-477-cpu-control.json); preparation-only refusal before provider calls | Both CPU profiles completed. No GPU comparison or target computation. The observed destination had 8.6 GB available versus 17.7 GB required. |
| EXP-477 owned-worker lifecycle and raw-retaining SSH executor (2026-09-04) | Unit-tested only | `tests/test_runpod_symbolic_worker.py` and `tests/test_symbolic_center_cloud.py`; separate code-review pass | Preparation-only by default; provisioning requires `--execute`. Storage preflight blocks this Mac. No live watchdog, creation, SSH, GPU parity, collection, retrieval or termination has been exercised. The local watchdog is not a provider-side billing cap. |
| EXP-477 prax storage and bounded local analysis (2026-09-05) | Storage smoke-tested live; analysis unit-tested | [Source-bound transport/Linux control](../experiments/receipts/EXP-477-prax-storage-smoke.json); local/provider byte-equivalence fixtures and independent review | A 16 MiB roundtrip and mismatch rejection passed; interrupted writers stopped and an orphaned live group was rejected. No target collection or remote-backed target fitting. Measured Mac upload was about 1.86 MB/s, so use verified local GPU retrieval followed by post-termination archival; do not assume the streaming deadline can accommodate 8 GiB. |
| EXP-477 independently authenticated watchdog readiness and verified retirement (2026-09-05) | Smoke-tested live, no worker creation | [Read-only watchdog control](../experiments/receipts/EXP-477-prax-watchdog-smoke.json); lifecycle/API regression tests | The watchdog independently authenticated using the privately bound credential identity, then its exact service and recorded processes retired. No provider mutation occurred. This does not yet establish live paid-worker teardown or the create-error paths. |
| EXP-477 fresh source-matched CPU control (2026-09-05) | Smoke-tested locally | [Reference at e8739a9](../experiments/receipts/EXP-477-prax-cpu-control.json) | Both profiles passed; this is a deployment reference, not a target or GPU result. A later source amendment requires a fresh matching CPU reference. |
| EXP-477 post-termination local-archive upload (2026-09-05) | Unit-tested only; shared SSH transport smoke-tested | `tests/test_archive_symbolic_collection_to_ssh.py`; independent producer/schema review | Requires the exact source-bound worker's verified termination and complete local raw/archive/control hashes before SSH. Explicit execute only; 7,200-second transfer ceiling; no provider calls or deletion of local originals. No complete target collection has yet exercised this command. |
| EXP-477 final frozen deployment attempt (2026-09-05) | Live creation and verified cleanup; deployment qualification failed | [Generated summary](../experiments/receipts/EXP-477-deployment-attempt-summary.json); source tag `exp-477-post-termination-protocol` | The sole task-owned A40 request failed configuration validation before workload/source upload; exact worker deletion and local watchdog retirement were independently verified. No GPU comparison or target collection. The failing response fields were not retained, so the specific contract/schema mismatch remains unresolved. No paid retry occurred. |
| Prax frozen source/input preparation backup (2026-09-05) | Verified live | [Four-file backup receipt](../experiments/receipts/EXP-477-prax-preparation-backup.json) | Independent SSH SHA-256/size and private-permission checks passed for source archive, inventory, candidates and CPU reference. Local originals retained. Not a trajectory collection or migration of historical results. |

Earlier live GPU qualification and teardown records remain in
[runpod-strategy.md](runpod-strategy.md) and the experiment receipts. They
do not establish that the newly changed error paths have been tested live.
# 2026-09-05 provider-contract recovery

The direct REST lookup now explicitly requests machine and network-volume
details. Configuration-only observations are durably saved before validation;
failed disk/volume/port checks identify individual fields. Numerical and safety
thresholds are unchanged. Local full suite: 1278 passed, one Linux-only process
identity test skipped on macOS. Focused lifecycle suite: 80 passed, including
forced contract failures with retained observations and verified teardown.
Live successor qualification is pending; this is not flow-symbolics evidence.

The first recovery isolated a missing REST `interruptible` field and verified
teardown. A second repair obtains exact-owned `podType=RESERVED` evidence via
GraphQL when REST omits the field; it never overrides explicit spot status.
Full local suite after this repair: 1284 passed, one Linux-only skip; focused
lifecycle suite: 86 passed. Live GraphQL query syntax/absence was rehearsed
against the terminated owned ID. No target trajectories have run yet.

Live configuration qualification subsequently passed with exact-owned
GraphQL `RESERVED` evidence. SSH setup exposed a missed raw-validator call;
the consumer is corrected and the real connection path now has a provider-
shaped regression. Full suite: 1285 passed, one Linux-only skip. Failed worker
and watchdog teardown verified; no upload or target computation occurred.

EXP-479 adds a default-off CPU adapter and detached-worktree local launcher.
Both preserved 64-seed control profiles pass through the real adapter. The
full-size, target-free 8192-seed benchmark retains both raw NPZ profiles with
zero failed integrations. This is adapter/reference equivalence, not independent
solver validation. The original CUDA path remains the default and its timing
metadata is unchanged; CPU metadata explicitly says `elapsed_cpu_seconds`.
