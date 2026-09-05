# External compute verification

| Change | Status | Evidence | Limit |
|---|---|---|---|
| RunPod finite hourly ceiling, invalid-price cleanup, and credential redaction (2026-09-04) | Unit-tested only | 33 mocked cases in `tests/test_runpodctl.py`; independent code review | No live API calls in this audit. Cleanup confirms only a successful deletion request, not a subsequent provider state. Hourly checks occur after provisioning and do not enforce cumulative spend. |
| EXP-477 read-only credential/catalog path (2026-09-04) | Verified live, read-only | Successful authenticated worker inventory and secure GPU catalog queries during protocol preparation | No create, SSH deployment, collection or teardown was tested by these queries. Unrelated running workers were not changed. Catalog prices are not reservations. |
| EXP-477 local CPU deployment reference and disk gate (2026-09-04) | Smoke-tested locally | [Full known-anchor receipt](../experiments/receipts/EXP-477-cpu-control.json); preparation-only refusal before provider calls | Both CPU profiles completed. No GPU comparison or target computation. The observed destination had 8.6 GB available versus 17.7 GB required. |
| EXP-477 owned-worker lifecycle and raw-retaining SSH executor (2026-09-04) | Unit-tested only | `tests/test_runpod_symbolic_worker.py` and `tests/test_symbolic_center_cloud.py`; separate code-review pass | Preparation-only by default; provisioning requires `--execute`. Storage preflight blocks this Mac. No live watchdog, creation, SSH, GPU parity, collection, retrieval or termination has been exercised. The local watchdog is not a provider-side billing cap. |

Earlier live GPU qualification and teardown records remain in
[runpod-strategy.md](runpod-strategy.md) and the experiment receipts. They
do not establish that the newly changed error paths have been tested live.
