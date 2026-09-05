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
- SSH relays bytes through the Mac without saving a bulk local archive.
  Both transfer size and time are bounded. A partial transfer remains
  partial; a valid archive is not by itself a complete scientific receipt.
- All received hashes and the complete candidate/profile/raw-file inventory
  must pass before collection can be marked complete and before normal
  owned-worker teardown.
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
