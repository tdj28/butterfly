# Remote evidence storage on prax

EXP-477 can retain its raw collection on `ubuntu@prax` instead of saving a
bulk archive on the Mac. This is an opt-in evidence destination, not a
general server backup or a migration of older experiments.

Only new directories under `/home/ubuntu/butterfly-research/<run-name>` are
created. Credentials, private keys and private lifecycle records stay on the
Mac. The receiver needs only the server's existing Python standard library;
no numerical packages or fitting jobs are installed on prax.

## Qualification

Run from a clean, pushed source snapshot. Use a new name for every attempt;
existing destinations are rejected and failed evidence is retained.

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.smoke_symbolic_ssh_storage \
  --source-commit FULL_FROZEN_COMMIT \
  --remote-dir /home/ubuntu/butterfly-research/UNIQUE_SMOKE_NAME \
  --output-dir artifacts/EXP-477/UNIQUE_SMOKE_NAME \
  --execute
```

This sends and retrieves a deterministic 16 MiB synthetic payload, audits
its hashes, rejects a deliberately incorrect hash, and tests owned Linux
writer shutdown. It creates no Runpod worker and integrates no trajectories.
Without `--execute`, it performs local source preflight only.

The separate `scripts.smoke_symbolic_watchdog` control verifies the real
local launchd watchdog's independent read-only provider authentication and
its subsequent retirement, also without creating a worker. Passing either
smoke is not GPU qualification or scientific evidence.

## Collection and analysis

The selected workflow uses the existing **local retrieval** mode of
`scripts.execute_symbolic_center_cloud` (omit `--ssh-storage-dir`). After
complete local raw verification and verified worker termination, run
`scripts.archive_symbolic_collection_to_ssh` with its source-matched
collection directory, lifecycle/ownership hashes and a fresh remote/output
directory. Default is local preflight; `--execute` permits the upload. Its
7,200-second transfer bound consumes no GPU rental time, and it retains
local originals as well as the new remote copy.

This choice follows a passing live smoke with approximately 1.86 MB/s Mac
upload: streaming the maximum 8 GiB directly during GPU rental would exceed
the short retrieval window. GPU-to-Mac retrieval still has its own bounded
deadline; the prax smoke does not measure that link.

An alternative inline mode remains opt-in: add
`--ssh-storage-dir /home/ubuntu/butterfly-research/UNIQUE_RUN_NAME` to
`scripts.execute_symbolic_center_cloud`, using its required matching frozen
source and fresh CPU-control hash. Preparation-only remains the default;
with this option preparation stages small public helper/control files on
prax. Only explicit `--execute` permits the bounded worker creation.

The selected evidence path is:

1. Collect on the single task-owned GPU worker after parity, throughput and
   disk qualification.
2. Stop and verify the worker's owned writers, then retrieve a bounded
   archive to the Mac.
3. Verify the archive, every raw file and the complete candidate/profile
   inventory locally; terminate the exact owned worker and verify absence.
4. Upload the retained archive to prax and verify its complete raw closure
   again. Retain both the archive and extracted originals on both hosts.
5. Run `scripts.analyze_symbolic_remote_collection` locally, supplying the
   hash-bound storage, collection, lifecycle and ownership receipts. This
   uses the unchanged numerical analysis with one disposable raw-file cache
   at a time and audits all remote originals before and after fitting.

Use each script's `--help` for required receipt arguments. Source-inventory
arguments support analysis from the same frozen source snapshot after
documentation advances; they do not permit changed analysis code.

The frozen limits are 8 GiB of evidence / 2,000 files, at least
17,722,933,248 free bytes on prax before preparation, and 9 GiB on the worker
after installation/qualification. Inline mode needs 2 GiB on the Mac for
control/staging; the selected local retrieval mode requires the full
archive-plus-extraction reserve (also 17,722,933,248 bytes).
Analysis limits one raw file to 256 MiB (including decompressed NPZ payload),
with a 512 MiB total cache ceiling. Cache cleanup removes only local copies
created by that invocation, never original remote data.

Partial transfers or failed qualification are preserved as failures; neither
an upload nor an empty worker inventory alone certifies success. The durable
watchdog is local, not a provider billing cap. No automatic paid retry exists.

See the [verification ledger](verification.md) and
[dated execution update](../updates/2026-09-05-prax-evidence-storage.md) for
what has actually run and the exact receipts.
