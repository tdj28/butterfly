# Remote evidence storage for the independent symbolic scout

## Authorization and scope

The owner offered `ubuntu@prax` as a storage destination, then explicitly
asked to implement it. The earlier Mac storage failure is retained in the
[previous update](2026-09-04-independent-symbolic-verification.md); it was
before any GPU creation or target collection.

This change moves bulk evidence storage, not the scientific goalposts.
EXP-477 remains a word-independent exploratory nomination pilot using all
551 frozen candidates and the unchanged numerical manifest. It cannot
verify a Jones word, center, generating partition or connecting arrow by
itself. The successful EXP-478 scalar control remains a separate result.

## Storage and computation boundary

The [storage runbook](../compute/remote-evidence-storage.md) records the
reusable commands and evidence-retention rules.

- A new private directory below `/home/ubuntu/butterfly-research` on `prax`
  will retain the bounded archive and extracted raw data. Existing server
  files and unrelated workloads are outside scope.
- The initial implementation supports a bounded in-memory SSH relay. The
  live timing below led to a different choice for this attempt: retain and
  verify locally first, then upload after GPU shutdown. A partial transfer
  remains partial; a valid archive alone is not a complete scientific receipt.
- All received hashes and the complete candidate/profile/raw-file inventory
  must pass at the chosen retrieval destination before collection can be
  marked complete and before normal owned-worker teardown. For the selected
  post-termination workflow that first destination is the Mac.
- CPU analysis remains on the Mac, fetching one hash-checked raw profile at
  a time into a bounded disposable cache. Full original evidence remains on
  `prax`; eviction removes only copies created by the analysis invocation.
  Original hashes are checked before fitting and again after it.
- No packages or numerical jobs are installed/run on the shared `prax`
  server. Its receiver/verifier uses the existing Python standard library.
- Runpod credentials, SSH private keys, lifecycle records, watchdog and
  controller remain on the Mac. No SSH agent is forwarded.

The original archive-plus-extraction space requirement is retained on
`prax`, with a separate smaller Mac reserve. The GPU container must also
retain enough free space for its raw collection after runtime installation;
remote final storage does not remove that requirement.

## Before paid execution

The implementation must pass synthetic transfer, integrity, interrupted-stage,
cache-bound and numerical-equivalence controls, a small live storage smoke,
and an independent code review. Its source and runtime policy are then
publicly frozen before a fresh CPU deployment reference and any GPU target
run. The earlier CPU reference/source tags are preserved, not relabeled.

The existing one-worker plan remains: secure A40, actual rate at most
USD 0.50/hour, three-hour lifetime ceiling, no-progress timeout, and USD 3
reserved for the entire attempt including storage/transfer margin. GPU
qualification and a measured throughput projection precede target collection.
This is within the owner's standing under-USD-30 authorization; no new
larger budget is assumed. The watchdog is a durable **local** control, not
a provider-enforced billing cap, and cannot act without the Mac/network.

## Current checkpoint

Read-only SSH succeeded with the existing verified host key. The intended
server filesystem had sufficient space and Python 3.12 was available.
The provider inventory contained an unrelated running worker; it was not
changed. Implementation is in progress. No new paid worker or target
trajectory has been launched at this checkpoint. Actual test, freeze,
execution, failure/completion, and teardown receipts will be added below.

During implementation the Mac's available storage increased substantially
without any deletion by this task. Remote evidence storage remains the
requested destination; the new local batch-analysis path is not justified by
pretending that the earlier free-space reading is still current.

## Implementation checks

Independent review found and corrected two lifecycle gaps before live use:
the watchdog must authenticate with its own process environment before any
create request, and local watchdog retirement must verify service/process
exit rather than just send a removal request. Credential identity is bound
privately on the Mac so a different account cannot falsely establish that
the owned worker is absent. The private fingerprint is not exported.

The storage tests cover exclusive destinations, changed/missing evidence,
partial transfers, bounded memory and cache eviction. The original local
analysis and remote-provider fixtures produce byte-identical results under
fixed synthetic clocks. On Linux, the new quiescence control also exercises
interrupted parent/grandchild writers and rejects an orphaned live writer
group. This is an infrastructure test, not an integration of the flow.

Live storage timing will be reported as **Mac–prax transport only**; it
cannot establish GPU-to-prax end-to-end bandwidth. Both the archive and
extracted smoke data will remain in their own new test folder. No existing
server data is overwritten or removed.

## Live controls and transport decision

Source `e8739a9d8d81d534f654d1baa8d942989e436443` was pushed and preserved
as `exp-477-prax-protocol` before any target execution. The first commands
at the earlier `e1c18f5` source correctly refused at clean-source preflight
because a final guard/test edit had arrived after the commit. Those refused
commands created no remote files, worker, or CPU reference.

The completed controls at the new freeze are:

- [Prax transport and Linux writer control](../experiments/receipts/EXP-477-prax-storage-smoke.json),
  SHA-256 `cf3ea31cd92e5a1916364f0658e08c858248ac6703f94efe651da246f5a44177`.
  The deterministic 16 MiB payload survived roundtrip hash checks; an
  incorrect descriptor was rejected. Interrupted parent/grandchild writers
  stopped, and an orphaned live group was refused as non-quiescent.
- [Independent watchdog control](../experiments/receipts/EXP-477-prax-watchdog-smoke.json),
  SHA-256 `e8c73c87db39c6ca1f1a1bc63c9701ae2c6789bf5d0fc708adb206e1a0fd3872`.
  Authentication and exact local service/process retirement passed without
  a provider mutation or paid worker.
- [Fresh CPU reference](../experiments/receipts/EXP-477-prax-cpu-control.json),
  SHA-256 `e3dee57e7916e8863c9336984acb65c1ebd5539ed7542bb9974e4a5e11523939`.
  Both profiles passed at the same source; it is not a GPU comparison.

The synthetic originals are retained at
`/home/ubuntu/butterfly-research/exp477-storage-smoke-20260905-e8739a9`.
Local validation finished with 1,217 passing tests and one Linux-only skip;
public Python 3.12/3.13 CI passed, including the Linux control.

The measured transport was approximately **1.86 MB/s upload** and
**6.19 MB/s download** (decimal MB; full timings are in the receipt). An
8 GiB archive would exceed the frozen 900-second streaming window at that
upload rate. Therefore the paid scout will **not** use inline prax streaming.
The Mac now has enough space for the original bounded local retrieval path:
retrieve and verify complete raw evidence locally, verify GPU termination,
then archive to prax with a separate bounded transfer while no GPU is rented.
Both local and remote originals remain retained. This is a prospective
operational amendment, not a changed numerical threshold or a target retry.
The post-termination archiver and matching source will be frozen before
target execution. The USD 3 attempt ceiling is unchanged.

Review of that new archiver caught an admission error before live use: its
CPU reference must be checked against the separate EXP-196 deployment
design, not the EXP-204 scout design. Distinct-parent regression fixtures
now exercise the real validator. The staged candidate bytes are also
checked against their original frozen hash/size independently of their
preparation descriptor. Neither correction changes any trajectory or fit.

## Final freeze and bounded deployment outcome

The final pre-target source is
`b53bfabf441e5afe756b7cfaec69f0a6989690e5`, preserved by
`exp-477-post-termination-protocol`. All 1,243 local tests passed (one
Linux-only skip), and public Python 3.12/3.13 CI passed. Fresh matching
[CPU](../experiments/receipts/EXP-477-post-termination-cpu-control.json),
[watchdog](../experiments/receipts/EXP-477-post-termination-watchdog-smoke.json)
and [prax/Linux](../experiments/receipts/EXP-477-post-termination-storage-smoke.json)
controls passed. The CPU input hash actually used was
`0c639fab4ecd09401f11bff62d68ad3e73419b3b4ba24b8739d49e6b0eaae87f`.

The single authorized POST created task worker `b03jtnuv8qws5q`. Its
configuration failed the frozen on-demand/disk/no-volume/SSH-only contract
check **before the workload callback**. No source was uploaded to that
worker, no GPU deployment comparison ran, and no target trajectory or
scientific raw collection was produced. There was no second paid request.

The controller/watchdog terminated that exact owned worker. Both direct
HTTP 404 and inventory absence were verified, then independently rechecked.
The local launchd service and recorded watchdog processes were also confirmed
absent. The unrelated pre-existing worker was unchanged. The interval from
the create-attempt timestamp to verified termination was about 5.12 seconds;
actual provider billing was not queried and the realized hourly rate was not
retained in this failed validation path.

The [generated public attempt summary](../experiments/receipts/EXP-477-deployment-attempt-summary.json)
has SHA-256 `e566bce27477744df61c3a8bca8ee161bf7b6d41a72251b1eb03d15f8f82478e`.
It includes producer/input hashes and explicit teardown/cost limitations;
private credentials, local identity records and unrelated worker IDs are
not copied. Regenerate it with `scripts/summarize_symbolic_attempt.py` using
the privately retained lifecycle/ownership and public preparation records.

**Diagnostic limitation:** the failing provider configuration fields were
not preserved before teardown. Therefore this record cannot identify which
field failed, or distinguish an actual unwanted configuration from a
provider response-schema mismatch. Do not guess that the provider allocated
a volume or that a particular field was missing. Before another paid
attempt, add an allowlisted configuration diagnostic receipt and compare it
with the current API contract. Preserve this failure; do not weaken the
deployment checks or describe it as a scientific negative result.

Prax storage is working. The bounded post-termination archiver and
remote-backed fitting remain unit-tested rather than target-verified,
because this attempt produced no target collection to archive or fit.

## Verified preparation backup on prax

The server now also holds actual frozen preparation material at
`/home/ubuntu/butterfly-research/exp477-preparation-20260905-b53bfab`:
`source.tar`, `source-inventory.json`, `candidates.json` and
`cpu-control.json`. This is an archive of the allowlisted public source and
numerical inputs, not a working checkout or a trajectory result.

All four remote SHA-256 values and sizes matched their frozen local
descriptors exactly. The directory is mode 700 and files mode 600, verified
through SSH. The [backup receipt](../experiments/receipts/EXP-477-prax-preparation-backup.json)
lists the hashes and 8,114,716-byte total. Local originals remain intact;
no credentials, private lifecycle records, correspondence or existing server
files were uploaded, removed or overwritten.

The transfer used the installed `rsync --ignore-existing --checksum` with
an explicit four-file allowlist and strict existing-host-key SSH, followed
by exact-file permission setting and independent `sha256sum`/`stat` checks.
An initial rsync command rejected an unsupported permission option locally
before transfer; no partial upload resulted from that command.

This completes the remote storage setup and preparation backup. Historical
research results have not been migrated. The next research step is resolving
the deployment diagnostic gap above, then prospectively freezing any
successor attempt; Jones' flow chains remain unverified by EXP-477.
