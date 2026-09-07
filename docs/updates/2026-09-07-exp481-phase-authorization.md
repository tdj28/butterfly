# EXP-481: one-use phase authorization and complete campaign dispatch

The actual controller can now connect reviewed setup to all three fixed
numerical phases. It does not yet have a real reviewed release to execute.
The existing analytic-circle control completes through the new authorization
path, and no new research trajectory or paid review has been generated.

## What changed

`scripts/run_paired_campaign.py` still defaults to outcome-free source preflight.
Its explicit `execute` mode first performs fresh **reviewed** setup, including
the live Git/review gate, source-bound tests, preserved input audit and isolated
full-design validation. No CLI accepts a saved approval, prior setup directory,
phase subset, alternative target thresholds or resume request.

The host dispatcher then claims the fixed local path
`artifacts/EXP-481/target-once.json` exclusively and durably. A new output folder
does not create another target attempt. Failures and interruptions keep this
marker; no command removes it. The final numerical release is still absent, so
the production command cannot presently reach that claim.

For each phase, the controller creates a fresh anonymous Unix socketpair and
passes one endpoint to its actual worker. The worker challenges that channel
with a fresh nonce, checks its peer PID against its actual parent, checks the
parent's OS-observed ordinary Python/controller invocation, and checks the
controller file against the runtime's source binding. The grant is limited to
one child, phase, runtime, design, input package, predecessor and campaign slot.
An issuer consumes even a failed handshake. Matching JSON/checksums and copied
controller arguments from a different program fail the actual-parent check.
The controller digest is additionally anchored in the frozen authorization
module itself: a coherently rehashed runtime contract cannot name a different
program as its own authority. A regression checks that independent digest
against the actual controller source and rejects substituted controller bytes.
The parent's actual executable image is checked separately with the OS process
API; an `argv[0]` string naming Python is not evidence that the process is Python.
The wire message is canonical finite JSON with a symmetric 65,536-byte ceiling
and bounded reads. Paths/arguments containing whitespace are explicitly refused
by the authorized controller's current strict argv contract.

This channel is separate from the original supervisor liveness pipe. The
worker's parent-loss guard remains attached to the original pipe, including
after stdin redirection. After the bounded standard-library handshake, the
worker installs its remaining authorized deadline **before** dependency
verification or scientific imports. The deadline starts on the controller's
monotonic clock before spawn, not after expensive startup. Numerical budgets
come from the unchanged design: 1,800 seconds for qualification, 14,400 for
collection and 7,200 for analysis; 2 GiB sampled RSS, 8 GiB sampled evidence
storage and 16 GiB initial free space. The analytic control retains its own
explicit 60-second budgets; its timings are not research runtime estimates.

Each worker reconstructs its design independently, checks the grant's complete
limits and bindings, and calls the existing phase implementation. The controller
requires a successful actual supervisor receipt with verified owned-group
cleanup, the matching worker witness, and the complete phase inventory before
granting the next phase. Failed numerical qualification blocks collection;
incomplete collection blocks analysis. A complete but scientifically unresolved
analysis remains an unresolved result, not an execution failure or permission
to select a better subset.

Failure bookkeeping no longer always says zero trajectories. Once target work
may have started, the count is `null` unless independently counted; it never
means zero. Partial journals remain the authoritative evidence. Analytic
controls continue to report zero target trajectories.

The numerical runtime now has 25 files: the only additional module is the
standard-library authorization reader. Review/API tooling and the phase
dispatcher remain host-side. The research design, integrators, event/capture
rules, sampling, fits and inference thresholds are unchanged.

## Verification ledger

- Development control `artifacts/EXP-481/authorized-control-01`: all three
  phases completed through the actual controller, both primary identity maps
  resolved, and historical symbols remained explicitly unverified. This is an
  unfrozen development control, not final source-qualified evidence.
- The authorization tests include full real-controller execution;
  wrong/missing grant, false parent argv and wrong predecessor; independently
  rehashed supervisor/witness tampering; exact/over-limit messages; and refusal
  of a foreign parent even with correct real file hashes and copied argv.
- The actual controller-loss test kills its own controller after an authorized
  analytic collection writes a raw prefix. The worker stops; the prefix remains;
  no phase terminal, next analysis or completed campaign receipt is invented.
- The earlier full local suite passed **1,705 tests with one older Linux-only
  skip** in 84.29 seconds. Final independent-parent-anchor checks, source-bound
  verification and CI are pending the implementation freeze.

This is a trusted-host integrity boundary, not a security sandbox against a
same-user debugger, modified interpreter, malicious startup hook or concurrent
hostile filesystem writer. The host/controller source binding and OS process
observations are trusted. Peer credentials identify a local process, not a
provider-signed scientific approval. The socket credential interfaces were
checked against [Apple's XNU header](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/un.h)
and the [Linux Unix-socket manual](https://www.man7.org/linux/man-pages/man7/unix.7.html).
The Mac path is exercised locally; Linux is exercised by CI, not claimed from
the Mac run alone.

## Next

Run the actual source-bound setup plus authorized control against the pushed
implementation, preserve its receipt, and merge only on passing CI. Then obtain
the one compact research-director review, adjudicate it, and publish the exact
executable release before target outcomes. The experiment-integrity playbook
requires these prospective checks; it does not require another routine user
permission request. No result here verifies Jones's alphabet, chain arrows,
homoclinic assertion or the entire parameter plane.
